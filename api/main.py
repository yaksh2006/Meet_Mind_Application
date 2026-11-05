from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from db.session import engine, Base

# API Application initialize karna
app = FastAPI(title="MeetMind Core API", version="1.0.0")

# CORS Policy - Taaki Streamlit frontend isse directly data le sake
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production me ise strictly Streamlit URL par set karenge
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup ke time tables verify karna
Base.metadata.create_all(bind=engine)

# Routes ko connect karna
app.include_router(router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"status": "MeetMind Engine is Active 🚀"}