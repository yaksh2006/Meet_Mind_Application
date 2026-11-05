import os
import json
from openai import OpenAI
from core.schemas import MeetingAnalysisResult, TaskItem, ParticipantSummary
from config.settings import settings

api_key = os.getenv("OPENAI_API_KEY") or getattr(settings, "OPENAI_API_KEY", None)

client = OpenAI(
    api_key=api_key.strip() if api_key else "",
    base_url="https://api.groq.com/openai/v1"
)

SYSTEM_PROMPT = """
You are MeetMind, an elite AI Meeting Intelligence engine.
Your task is to parse meeting transcripts into structured intelligence.

Return ONLY a valid JSON object matching this exact schema:
{
  "meeting_title": "Short descriptive meeting title",
  "executive_summary": "High level overview of what was discussed",
  "tasks": [
    {
      "task_description": "Clear action item description",
      "assigned_to": "Name of the person assigned or 'Unassigned'",
      "assigned_by": "Name of person assigning or 'Host'",
      "deadline_raw": "Mentioned deadline text or 'None'",
      "deadline_normalized": "YYYY-MM-DD or null",
      "confidence_score": 0.9,
      "source_context": "Exact sentence or context from transcript",
      "is_implicit": false
    }
  ],
  "participant_insights": [
    {
      "participant_name": "Full name of the participant",
      "missed_key_points": [],
      "critical_mentions": []
    }
  ]
}

CRITICAL RULES:
1. Every task MUST have 'assigned_to'. If not explicitly mentioned, assign to 'Unassigned'.
2. In participant_insights, use 'participant_name' exclusively, NOT 'name'.
3. Do not include markdown formatting or commentary outside the JSON.
"""

def extract_meeting_intelligence(transcript: str) -> MeetingAnalysisResult:
    """
    Extracts structured action items, executive summaries, and participant insights.
    """
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this transcript:\n\n{transcript}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        raw_json = response.choices[0].message.content
        data = json.loads(raw_json)

        # 1. Fallback & Normalization for Tasks
        sanitized_tasks = []
        for t in data.get("tasks", []):
            sanitized_tasks.append(
                TaskItem(
                    task_description=t.get("task_description") or "Follow up on action item",
                    assigned_to=t.get("assigned_to") or t.get("assignee") or t.get("owner") or "Unassigned",
                    assigned_by=t.get("assigned_by") or "Host",
                    deadline_raw=t.get("deadline_raw") or "None",
                    deadline_normalized=t.get("deadline_normalized"),
                    confidence_score=float(t.get("confidence_score", 0.8)),
                    source_context=t.get("source_context") or "Extracted from meeting audio",
                    is_implicit=bool(t.get("is_implicit", False))
                )
            )

        # 2. Fallback & Normalization for Participant Insights
        sanitized_insights = []
        for p in data.get("participant_insights", []):
            name = p.get("participant_name") or p.get("name") or p.get("participant") or "Participant"
            sanitized_insights.append(
                ParticipantSummary(
                    participant_name=name,
                    missed_key_points=p.get("missed_key_points") or [],
                    critical_mentions=p.get("critical_mentions") or []
                )
            )

        # 3. Final Schema Assembly
        return MeetingAnalysisResult(
            meeting_title=data.get("meeting_title") or "Team Sync & Task Alignment",
            executive_summary=data.get("executive_summary") or "Discussion on ongoing technical items and tasks.",
            tasks=sanitized_tasks,
            participant_insights=sanitized_insights
        )
        
    except Exception as e:
        print(f"Extraction Error: {e}")
        raise