import sys
import os

# Project root directory ko system path me add karna taaki 'config' mil sake
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
import json

# Database connection
from config.settings import settings
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Set page config
st.set_page_config(page_title="MeetMind Dashboard", layout="wide", page_icon="🧠")

st.title("🧠 MeetMind - Team Intelligence Portal")

# Sidebar: Dispatch Bot
with st.sidebar:
    st.header("Join New Meeting")
    meet_url = st.text_input("Meeting Link (Google Meet / Zoom)")
    if st.button("Send MeetMind Bot", type="primary"):
        if meet_url:
            with st.spinner("Dispatching Bot..."):
                try:
                    res = httpx.post("http://localhost:8000/api/v1/meetings/start", json={"meeting_url": meet_url})
                    if res.status_code == 200:
                        st.success(f"Bot sent! ID: {res.json().get('bot_id')}")
                    else:
                        st.error(f"Failed: {res.text}")
                except Exception as e:
                    st.error(f"Backend offline: {e}")
        else:
            st.warning("Please enter a meeting link.")

# Fetch unique users from the database for the filter
def get_unique_users():
    db = SessionLocal()
    try:
        # Fixed: using text() for raw SQL
        result = db.execute(
            text("SELECT DISTINCT assigned_to FROM tasks WHERE assigned_to IS NOT NULL")
        ).fetchall()
        return [row[0] for row in result] if result else []
    finally:
        db.close()

all_users = get_unique_users()
user_options = ["All Tasks"] + all_users

# Top Filter
selected_user = st.selectbox("View Dashboard As:", user_options)
st.divider()

# Pandas ke through secure database connection open karna
try:
    with engine.connect() as conn:
        if selected_user == "All Tasks":
            st.subheader("📋 Overall Team Tasks")
            
            # Fixed: using text() and connection parameter
            tasks_query = text("""
                SELECT tasks.assigned_to, tasks.task_description, tasks.deadline_raw, tasks.status, meetings.title 
                FROM tasks 
                JOIN meetings ON tasks.meeting_id = meetings.id
            """)
            tasks = pd.read_sql(tasks_query, conn)
            
            if not tasks.empty:
                st.dataframe(tasks, use_container_width=True)
            else:
                st.info("No tasks recorded yet.")
                
        else:
            st.subheader(f"👤 {selected_user}'s Personal Dashboard")
            
            # 1. Show Tasks specifically for the selected user
            st.markdown("### Your Action Items")
            
            # Use parameter binding to prevent SQL injection & formatting errors
            user_tasks_query = text("""
                SELECT tasks.id, tasks.task_description, tasks.deadline_raw, tasks.source_context, tasks.status, meetings.title 
                FROM tasks 
                JOIN meetings ON tasks.meeting_id = meetings.id 
                WHERE LOWER(tasks.assigned_to) = LOWER(:username)
            """)
            user_tasks = pd.read_sql(user_tasks_query, conn, params={"username": selected_user})
            
            if not user_tasks.empty:
                for _, task in user_tasks.iterrows():
                    with st.container(border=True):
                        col1, col2 = st.columns([0.7, 0.3])
                        with col1:
                            st.markdown(f"**Task:** {task['task_description']}")
                            st.caption(f"Context: \"{task['source_context']}\"")
                        with col2:
                            st.write(f"⏳ Deadline: `{task['deadline_raw'] or 'N/A'}`")
                            # Streamlit doesn't have st.badge, using HTML style write
                            st.markdown(f"`Status: {task['status']}`")
            else:
                st.info("You have no assigned tasks.")

            # 2. Show missed points/insights for the selected user
            st.markdown("### What You Missed (Key Context)")
            
            insights_query = text("""
                SELECT missed_key_points_json, critical_mentions_json, meetings.title 
                FROM participant_insights 
                JOIN meetings ON participant_insights.meeting_id = meetings.id 
                WHERE LOWER(participant_name) = LOWER(:username)
            """)
            insights_df = pd.read_sql(insights_query, conn, params={"username": selected_user})
            
            if not insights_df.empty:
                for _, insight in insights_df.iterrows():
                    with st.expander(f"Meeting Context: {insight['title']}", expanded=True):
                        missed_points = json.loads(insight['missed_key_points_json'] or "[]")
                        mentions = json.loads(insight['critical_mentions_json'] or "[]")
                        
                        if missed_points:
                            st.markdown("**Critical Decisions You Missed:**")
                            for point in missed_points:
                                st.markdown(f"- {point}")
                        if mentions:
                            st.markdown("**Critical Mentions of You:**")
                            for mention in mentions:
                                st.markdown(f"- {mention}")
                        if not missed_points and not mentions:
                            st.write("No critical missed context for this meeting.")
            else:
                st.info("No missed context recorded for you.")

except Exception as e:
    st.error(f"Database error: {e}")