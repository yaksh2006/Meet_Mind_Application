<div align="center">

# 🧠 MeetMind
### *Autonomous Meeting Intelligence & Action Engine*

Transform raw video meetings into actionable intelligence, structured task graphs, and participant alignment insights in real-time.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Groq](https://img.shields.io/badge/Groq-LPU%20Inference-f55036?style=for-the-badge)](https://groq.com/)
[![Recall.ai](https://img.shields.io/badge/Recall.ai-Virtual%20Participant-black?style=for-the-badge)](https://www.recall.ai/)
[![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

</div>

---

## 🌟 Executive Summary

**MeetMind** is an enterprise-grade meeting intelligence layer that completely eliminates post-meeting admin work. Instead of relying on passive call recordings, MeetMind dispatches an autonomous bot to your virtual calls, streams the conversation, and runs high-throughput inference using Groq LPU acceleration.

The system extracts explicit and implicit tasks, tracks confidence metrics, flags missed discussions for late/absent attendees, and maps all intelligence into an interactive executive dashboard.

---

## 🔄 End-to-End Architecture & Dataflow

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Host
    participant GM as Google Meet / Zoom
    participant RB as Recall.ai Bot
    participant RS as Recall.ai Media Server
    participant FA as FastAPI Server / Script
    participant LLM as Groq Engine (Llama 3.3 / OSS)
    participant DB as SQLite Storage
    participant UI as Streamlit Dashboard

    User->>GM: Start Meeting & invite Bot
    GM->>RB: Bot joins & captures dual-channel audio
    User->>GM: Meeting concludes & disconnects
    RB->>RS: Upload raw audio & generate transcript
    FA->>RS: Query /bot/{id}/ or Webhook triggers transcript ready
    RS-->>FA: Stream structured JSON transcript
    FA->>LLM: Send transcript + MeetMind Grounding Prompts
    Note over LLM: Extract Action Items, Confidence Scores,<br/>Source Quotes & Member Insights
    LLM-->>FA: Return validated schema payload
    FA->>DB: Ingest Meeting, Tasks, and Insights
    UI->>DB: Query intelligence tables
    UI-->>User: Render interactive dashboards & visual analytics
