from fastapi import APIRouter, BackgroundTasks, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json

from db.session import get_db
from db.models import Meeting, Task, ParticipantInsight
from services.recall_service import dispatch_bot, get_transcript
from core.extractor import extract_meeting_intelligence

router = APIRouter()

# Schema for frontend request
class MeetingStartRequest(BaseModel):
    meeting_url: str
    bot_name: str = "MeetMind Bot"

@router.post("/meetings/start")
def start_meeting(req: MeetingStartRequest):
    """Frontend se aayi link ko Recall.ai bot tak pahuchana."""
    try:
        bot_data = dispatch_bot(req.meeting_url, req.bot_name)
        return {"status": "success", "bot_id": bot_data.get("id"), "message": "Bot dispatched successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def process_transcript_background(bot_id: str, meeting_url: str, db: Session):
    """
    Industry Standard: AI heavy-lifting hamesha background task me hoti hai.
    Ye function transcript layega, AI se process karayega, aur Database me save karega.
    """
    try:
        # 1. Fetch raw transcript
        raw_transcript = get_transcript(bot_id)
        if not raw_transcript.strip():
            print(f"Empty transcript for bot {bot_id}")
            return

        # 2. Run Core AI Extraction Engine
        analysis = extract_meeting_intelligence(raw_transcript)

        # 3. Save Data Transactions securely
        new_meeting = Meeting(
            id=bot_id,
            meeting_url=meeting_url,
            title=analysis.meeting_title,
            executive_summary=analysis.executive_summary,
            full_transcript=raw_transcript
        )
        db.add(new_meeting)

        # Tasks insert karna
        for task in analysis.tasks:
            db.add(Task(
                meeting_id=bot_id,
                assigned_to=task.assigned_to,
                assigned_by=task.assigned_by,
                task_description=task.task_description,
                deadline_raw=task.deadline_raw,
                deadline_normalized=task.deadline_normalized,
                confidence_score=task.confidence_score,
                source_context=task.source_context,
                is_implicit=task.is_implicit,
                status="Pending"
            ))

        # Insights insert karna (Aadhi meeting miss karne walo ke liye)
        for insight in analysis.participant_insights:
            db.add(ParticipantInsight(
                meeting_id=bot_id,
                participant_name=insight.participant_name,
                missed_key_points_json=json.dumps(insight.missed_key_points),
                critical_mentions_json=json.dumps(insight.critical_mentions)
            ))

        db.commit()
        print(f"✅ Successfully processed and saved meeting {bot_id}")
        
    except Exception as e:
        print(f"❌ Error in background processing: {e}")
        db.rollback()


@router.post("/webhooks/recall")
async def recall_webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    payload = await request.json()
    event_type = payload.get("event")
    print(f"🔔 Webhook received event: {event_type}")

    bot_data = payload.get("data", {}).get("bot", {})
    bot_id = bot_data.get("id")
    meeting_url = bot_data.get("meeting_url", "")
    
    # Status code extract
    status_changes = bot_data.get("status_changes", [])
    current_status = status_changes[-1].get("code") if status_changes else None
    print(f"📊 Current Bot Status: {current_status}")

    # Jab transcript ready ho jaye ya bot call exit kar chuka ho
    if event_type == "transcript.done" or current_status in ["done", "call_ended", "ready"]:
        print(f"⚡ Triggering background processing for bot: {bot_id}")
        background_tasks.add_task(process_transcript_background, bot_id, meeting_url, db)
            
    return {"status": "received"}