from db.session import engine, Base
from db.models import Meeting, Task, ParticipantInsight

def init():
    print("Database tables initialize ho rahi hain...")
    Base.metadata.create_all(bind=engine)
    print("Tables successfully create ho gayi: meetings, tasks, participant_insights")

if __name__ == "__main__":
    init()