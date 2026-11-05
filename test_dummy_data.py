from db.session import SessionLocal
from db.models import Meeting, Task, ParticipantInsight
import json
import uuid

def run_test():
    db = SessionLocal()
    
    print("🧪 Running offline test (Bypassing OpenAI API for instant testing)...")
    
    transcript = """
    W: Meeting start karte hain. X abhi available nahi hai, wo half-hour baad aayega.
    Y: Theek hai. Toh humne decide kiya hai ki naya backend framework FastAPI hoga.
    Z: Perfect. Y, tum naya server setup Friday tak complete kar lena.
    Y: Got it, ho jayega.
    W: Oh, X ne join kar liya hai. Hi X!
    X: Hi team, sorry main late ho gaya.
    W: Koi baat nahi X. Naya backend FastAPI final hua hai. Tumhe Monday tak iske hisaab se frontend UI update karni hai.
    X: Okay, main Monday tak frontend update kar dunga.
    """
    
    bot_id = "test_bot_" + str(uuid.uuid4())[:8]
    
    # 1. Meeting details save karna
    new_meeting = Meeting(
        id=bot_id,
        meeting_url="https://meet.google.com/test-abc",
        title="Sprint Planning: Backend & Frontend Alignment",
        executive_summary="Team aligned on migrating to FastAPI. Y is handling server setup, while X will update the frontend screens.",
        full_transcript=transcript
    )
    db.add(new_meeting)
    
    # 2. Tasks add karna (W, X, Y, Z scenario)
    sample_tasks = [
        {
            "assigned_to": "Y",
            "task_description": "Setup naya server with FastAPI",
            "deadline_raw": "Friday",
            "source_context": "Z: Perfect. Y, tum naya server setup Friday tak complete kar lena.",
            "status": "Pending"
        },
        {
            "assigned_to": "X",
            "task_description": "Update frontend UI based on FastAPI integration",
            "deadline_raw": "Monday",
            "source_context": "W: Tumhe Monday tak iske hisaab se frontend UI update karni hai.",
            "status": "Pending"
        },
        {
            "assigned_to": "W",
            "task_description": "Coordinate sprint goals and final architecture review",
            "deadline_raw": "End of week",
            "source_context": "W: Meeting start karte hain.",
            "status": "In Progress"
        }
    ]
    
    for t in sample_tasks:
        db.add(Task(
            meeting_id=bot_id,
            assigned_to=t["assigned_to"],
            task_description=t["task_description"],
            deadline_raw=t["deadline_raw"],
            source_context=t["source_context"],
            status=t["status"]
        ))
        
    # 3. Missing window insights save karna (X jo late aaya tha)
    insights = [
        {
            "participant_name": "X",
            "missed_key_points": [
                "Decision taken: Backend framework finalized as FastAPI.",
                "Y was assigned server setup before your arrival."
            ],
            "critical_mentions": [
                "W mentioned that you were joining 30 mins late."
            ]
        },
        {
            "participant_name": "Y",
            "missed_key_points": [],
            "critical_mentions": ["Assigned server deployment task."]
        }
    ]
    
    for i in insights:
        db.add(ParticipantInsight(
            meeting_id=bot_id,
            participant_name=i["participant_name"],
            missed_key_points_json=json.dumps(i["missed_key_points"]),
            critical_mentions_json=json.dumps(i["critical_mentions"])
        ))
        
    db.commit()
    print("✅ Dummy data successfully database me save ho gaya!")
    print("👉 Ab browser par Streamlit Dashboard (http://localhost:8501) refresh karein.")
    db.close()

if __name__ == "__main__":
    run_test()