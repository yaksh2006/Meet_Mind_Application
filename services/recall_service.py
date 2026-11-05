import os
import httpx
from fastapi import HTTPException
from dotenv import load_dotenv
from config.settings import settings
from typing import Dict, Any

load_dotenv()

def get_base_url() -> str:
    url = getattr(settings, "RECALL_API_URL", None) or os.getenv("RECALL_API_URL")
    if not url or not url.strip():
        url = "https://ap-northeast-1.recall.ai/api/v1"
    url = url.strip().strip("'").strip('"').rstrip("/")
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"https://{url}"
    return url

def get_headers() -> Dict[str, str]:
    api_key = getattr(settings, "RECALL_API_KEY", None) or os.getenv("RECALL_API_KEY")
    if api_key:
        api_key = str(api_key).strip().strip("'").strip('"')
    print(f"🚀 DEBUG - API Key Loaded: {api_key}")
    return {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }

def dispatch_bot(meeting_url: str, bot_name: str = "MeetMind NoteTaker") -> Dict[str, Any]:
    base_url = get_base_url()
    endpoint = f"{base_url}/bot"
    print(f"🚀 DEBUG - Dispatching to endpoint: {endpoint}")

    # ap-northeast-1 region me transcription_options field allowed nahi hai
    payload = {
        "meeting_url": meeting_url,
        "bot_name": bot_name
    }

    with httpx.Client() as client:
        try:
            response = client.post(endpoint, json=payload, headers=get_headers(), timeout=20.0)

            if not response.is_success:
                error_msg = response.json() if response.content else response.text
                print(f"❌ RECALL API ERROR: {response.status_code} - {error_msg}")
                raise HTTPException(status_code=response.status_code, detail=f"Recall API Error: {error_msg}")

            return response.json()

        except httpx.RequestError as e:
            print(f"❌ HTTP REQUEST FAILED: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to connect to Recall.ai API: {str(e)}")

def get_transcript(bot_id: str) -> str:
    base_url = get_base_url()
    endpoint = f"{base_url}/bot/{bot_id}/transcript"

    with httpx.Client() as client:
        response = client.get(endpoint, headers=get_headers(), timeout=20.0)

        if not response.is_success:
            print(f"❌ TRANSCRIPT ERROR: {response.status_code}")
            return "Transcript not available yet."

        data = response.json()
        transcript_lines = []
        for segment in data:
            speaker = segment.get("speaker", "Unknown")
            words = " ".join([w.get("text", "") for w in segment.get("words", [])])
            transcript_lines.append(f"{speaker}: {words}")

        return "\n".join(transcript_lines)