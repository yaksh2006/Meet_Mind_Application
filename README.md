<div align="center">
  <h1>🧠 MeetMind</h1>
  <p><b>An Elite AI Meeting Intelligence & Extraction Engine</b></p>

  [![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green.svg)](https://fastapi.tiangolo.com/)
  [![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)](https://streamlit.io/)
  [![Groq API](https://img.shields.io/badge/AI-Groq%20Llama%203-orange.svg)](https://groq.com/)
  [![Recall.ai](https://img.shields.io/badge/Bot-Recall.ai-purple.svg)](https://www.recall.ai/)
</div>

---

## 🌟 Overview

**MeetMind** is an advanced AI-powered meeting assistant designed to automate meeting transcriptions and extract actionable intelligence. It deploys a bot directly to Google Meet, captures transcripts using **Recall.ai**, and leverages the blazing-fast **Groq API** to extract tasks, deadlines, confidence scores, and participant insights. All data is beautifully visualized on an interactive **Streamlit** dashboard.

## ✨ Key Features

- 🤖 **Automated Bot Integration:** Seamlessly joins Google Meet calls to record and transcribe audio automatically.
- 🧠 **Smart AI Extraction:** Generates an executive summary and identifies action items using Groq's high-speed LLMs.
- 🎯 **Task Management:** Automatically detects Assignees, Assigners, and normalizes Deadlines into a clean format (YYYY-MM-DD).
- 🛡️ **Hallucination Prevention:** Strictly grounds every extracted task with an exact source context/quote from the transcript.
- 👥 **Participant Insights:** Tracks missed key points and critical mentions for individual participants.
- 📊 **Interactive Dashboard:** View real-time meeting intelligence via a clean, user-friendly Streamlit web interface.

## 🛠️ Tech Stack

| Component | Technology |
| --- | --- |
| **Frontend Dashboard** | Streamlit |
| **Backend API** | FastAPI, Uvicorn |
| **Database** | SQLite, SQLAlchemy, Pydantic |
| **Transcription Service**| Recall.ai |
| **LLM Engine** | Groq API (Llama-3 models) |

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- [Recall.ai](https://www.recall.ai/) API Key
- [Groq](https://console.groq.com/) API Key (Free)

### Installation

**1. Clone the repository:**
```bash
git clone [https://github.com/yaksh2006/Meet_Mind_Application.git](https://github.com/yaksh2006/Meet_Mind_Application.git)
cd Meet_Mind_Application
