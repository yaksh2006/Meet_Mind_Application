from pydantic import BaseModel, Field
from typing import List, Optional

class TaskItem(BaseModel):
    task_description: str
    assigned_to: str = "Unassigned"
    assigned_by: str = "Host"
    deadline_raw: Optional[str] = "None"
    deadline_normalized: Optional[str] = None
    confidence_score: float = 0.8
    source_context: Optional[str] = "Extracted from meeting"
    is_implicit: bool = False

class ParticipantSummary(BaseModel):
    participant_name: str
    missed_key_points: List[str] = Field(default_factory=list)
    critical_mentions: List[str] = Field(default_factory=list)

class MeetingAnalysisResult(BaseModel):
    meeting_title: str
    executive_summary: str
    tasks: List[TaskItem] = Field(default_factory=list)
    participant_insights: List[ParticipantSummary] = Field(default_factory=list)