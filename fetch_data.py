import os
import httpx
from dotenv import load_dotenv
from config.settings import settings
from db.session import SessionLocal
from core.extractor import extract_meeting_intelligence
from db.models import Meeting, Task, ParticipantInsight
import json

load_dotenv()

# Aapki recorded meeting ki Bot ID
BOT_ID = "ad501a55-7a5d-4ebc-8c92-0359d1579046"
MEETING_URL = "https://meet.google.com/cgi-vckc-htw"
BASE_URL = "https://ap-northeast-1.recall.ai/api/v1"

api_key = getattr(settings, "RECALL_API_KEY", None) or os.getenv("RECALL_API_KEY")
headers = {
    "Authorization": f"Token {api_key.strip()}",
    "Content-Type": "application/json"
}

# 1. Naya API Endpoint - Pehle Bot ki details fetch karte hain
print(f"🚀 Fetching bot info for ID: {BOT_ID}...")
bot_res = httpx.get(f"{BASE_URL}/bot/{BOT_ID}/", headers=headers, timeout=20.0)

if not bot_res.is_success:
    print(f"❌ Error fetching bot: {bot_res.text}")
    exit()

bot_data = bot_res.json()
recordings = bot_data.get("recordings", [])

if not recordings:
    print("❌ No recordings found for this bot yet.")
    exit()

recording_id = recordings[0]["id"]
transcript_info = recordings[0].get("media_shortcuts", {}).get("transcript")

# 2. Check karna ki Transcript bani ya nahi
if not transcript_info or "download_url" not in transcript_info.get("data", {}):
    print("⏳ Transcript abhi ready nahi hai! Recall.ai ko request bhej rahe hain...")
    create_url = f"{BASE_URL}/recording/{recording_id}/create_transcript/"
    # Naya Async Transcript Trigger Endpoint
    c_res = httpx.post(create_url, headers=headers, json={"provider": {"recallai_async": {}}})
    print(f"Request Status: {c_res.status_code}")
    print("⏳ Dashboard par Transcript banna shuru ho chuki hai. Please wait 1-2 minutes aur ye script wapas run karein.")
    exit()

# 3. Direct Download URL milne par Transcript Extract Karna
download_url = transcript_info["data"]["download_url"]
print("✅ Transcript Download URL mil gaya! Downloading...")

t_res = httpx.get(download_url)
if not t_res.is_success:
    print(f"❌ Download failed: {t_res.status_code}")
    exit()

data = t_res.json()
transcript_lines = []
for segment in data:
    speaker = segment.get("participant", {}).get("name", "Unknown")
    words = " ".join([w.get("text", "") for w in segment.get("words", [])])
    if words.strip():
        transcript_lines.append(f"{speaker}: {words}")

raw_transcript = "\n".join(transcript_lines)
print("\n✅ Transcript processed successfully. AI Extraction shuru kar rahe hain...")

# 4. AI Engine aur Database save
analysis = extract_meeting_intelligence(raw_transcript)

db = SessionLocal()
new_meeting = Meeting(
    id=BOT_ID,
    meeting_url=MEETING_URL,
    title=analysis.meeting_title,
    executive_summary=analysis.executive_summary,
    full_transcript=raw_transcript
)
db.merge(new_meeting)

for task in analysis.tasks:
    db.add(Task(
        meeting_id=BOT_ID,
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

for insight in analysis.participant_insights:
    db.add(ParticipantInsight(
        meeting_id=BOT_ID,
        participant_name=insight.participant_name,
        missed_key_points_json=json.dumps(insight.missed_key_points),
        critical_mentions_json=json.dumps(insight.critical_mentions)
    ))

db.commit()
db.close()
print("🎉 Sab data database me save ho gaya! Streamlit Refresh karein.")