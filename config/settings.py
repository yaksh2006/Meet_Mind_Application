import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "MeetMind Core"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    RECALL_API_KEY: str = os.getenv("RECALL_API_KEY", "")
    RECALL_API_URL: str = os.getenv("RECALL_API_URL", "https://api.recall.ai/api/v1")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./meetmind.db")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

settings = Settings()