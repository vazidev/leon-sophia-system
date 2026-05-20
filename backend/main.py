import os
import json
import uuid
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session, select
from dotenv import load_dotenv
from db import engine, create_db, get_session
from models.debate import DebateSession, LeonEvolution
from orchestrator import run_debate

load_dotenv()

app = FastAPI(title="LEON-SOPHIA Debate API")


@app.on_event("startup")
async def startup_event():
    try:
        create_db()
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


class StartRequest(BaseModel):
    topic: str


@app.post("/api/debate/start")
async def start_debate(req: StartRequest):
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}


@app.get("/api/debate/{session_id}/stream")
async def stream_debate(session_id: str, topic: str = Query(...)):
    async def event_generator():
        async for event in run_debate(topic, session_id):
            yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/debate/{session_id}/state")
async def get_state(session_id: str, s: Session = Depends(get_session)):
    sess = s.exec(
        select(DebateSession).where(DebateSession.session_id == session_id)
    ).first()
    return sess or {}


@app.get("/api/debate/{session_id}/evolution")
async def get_evolution(session_id: str, s: Session = Depends(get_session)):
    rows = s.exec(
        select(LeonEvolution).where(LeonEvolution.session_id == session_id)
    ).all()
    return [
        {
            "round": r.round,
            "recommendationSnapshot": r.recommendation_snapshot,
            "evidenceCount": r.evidence_count,
            "claimsAdded": r.claims_added,
            "scopeKeywords": r.scope_keywords,
            "confidenceScore": r.confidence_score,
            "qualityScore": r.quality_score,
        }
        for r in rows
    ]
