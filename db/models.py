from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.session import Base

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(String, primary_key=True, index=True)
    meeting_url = Column(String, nullable=True)
    title = Column(String, default="Untitled Meeting")
    executive_summary = Column(Text, nullable=True)
    full_transcript = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tasks = relationship("Task", back_populates="meeting", cascade="all, delete-orphan")
    insights = relationship("ParticipantInsight", back_populates="meeting", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False)
    assigned_to = Column(String, index=True, nullable=False)
    assigned_by = Column(String, nullable=True)
    task_description = Column(Text, nullable=False)
    deadline_raw = Column(String, nullable=True)
    deadline_normalized = Column(String, nullable=True)
    confidence_score = Column(Float, default=1.0)
    source_context = Column(Text, nullable=True)
    is_implicit = Column(Boolean, default=False)
    status = Column(String, default="Pending") # Pending, In Progress, Completed

    meeting = relationship("Meeting", back_populates="tasks")

class ParticipantInsight(Base):
    __tablename__ = "participant_insights"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False)
    participant_name = Column(String, index=True, nullable=False)
    missed_key_points_json = Column(Text, nullable=True) # Serialized list of bullet points
    critical_mentions_json = Column(Text, nullable=True)

    meeting = relationship("Meeting", back_populates="insights")