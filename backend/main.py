
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent import run_agent


app = FastAPI(
    title="Natural Language to SQL AI Agent",
    description="Convert English questions into SQL queries.",
    version="1.0.0"
)


# Allow React frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"]
)


# Request structure
class QuestionRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000
    )


# Home API
@app.get("/")
def home():
    return {
        "message": "Welcome to SQL AI Agent",
        "status": "Backend is running"
    }


# Health check API
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# Main API
@app.post("/ask")
def ask_question(request: QuestionRequest):
    result = run_agent(request.question)
    return result
