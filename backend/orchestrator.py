import json
from datetime import datetime, timezone
from typing import AsyncGenerator
from sqlmodel import Session, select
import db as _db
from models.debate import DebateSession, DebateRound, LeonEvolution
from models.flags import Flag, Severity
from agents.leon import LeonAgent, LeonTextChunk, LeonChunk
from agents.sophia import SophiaAgent, SophiaTextChunk, SophiaFlagChunk, SophiaReviewChunk, SophiaConvergenceChunk

def _save_evolution(session_id: str, round_num: int, leon: LeonChunk, quality_score: float):
    with Session(_db.engine) as s:
        evo = LeonEvolution(
            session_id=session_id,
            round=round_num,
            recommendation_snapshot=leon.recommendation,
            evidence_count=len(leon.evidence),
            confidence_score=leon.confidence_score,
            quality_score=quality_score,
        )
        evo.claims_added = leon.new_claims
        evo.claims_resolved = leon.resolved_flags
        evo.scope_keywords = leon.scope_keywords
        s.add(evo)
        s.commit()

def _save_flags(session_id: str, round_num: int, flag_chunks: list[SophiaFlagChunk]):
    with Session(_db.engine) as s:
        for f in flag_chunks:
            s.add(Flag(
                session_id=session_id, round=round_num,
                severity=Severity.BLOCKING if f.severity == "blocking" else Severity.ADVISORY,
                claim=f.claim, description=f.description
            ))
        s.commit()

async def run_debate(topic: str, session_id: str) -> AsyncGenerator[dict, None]:
    leon = LeonAgent()
    sophia = SophiaAgent()
    history: list[dict] = []
    round_num = 0
    last_blocking_flags: list[str] = []
    pending_leon: LeonChunk | None = None

    with Session(_db.engine) as s:
        s.add(DebateSession(
            session_id=session_id,
            topic=topic,
            created_at=datetime.now(timezone.utc).isoformat()
        ))
        s.commit()

    while True:
        round_num += 1

        # LEON round
        yield {"event": "round_start", "data": {"round": round_num, "agent": "leon"}}
        leon_text = ""
        pending_leon = None

        async for chunk in leon.stream_response(topic, history, last_blocking_flags):
            if isinstance(chunk, LeonTextChunk):
                leon_text += chunk.text
                yield {"event": "token", "data": {"text": chunk.text}}
            elif isinstance(chunk, LeonChunk):
                pending_leon = chunk

        history.append({"role": "assistant", "content": leon_text})

        # SOPHIA round
        yield {"event": "round_start", "data": {"round": round_num, "agent": "sophia"}}
        sophia_text = ""
        pending_flags: list[SophiaFlagChunk] = []
        sophia_review: SophiaReviewChunk | None = None
        convergence_chunk: SophiaConvergenceChunk | None = None

        async for chunk in sophia.stream_review(
            topic, history,
            pending_leon.recommendation if pending_leon else ""
        ):
            if isinstance(chunk, SophiaTextChunk):
                sophia_text += chunk.text
                yield {"event": "token", "data": {"text": chunk.text}}
            elif isinstance(chunk, SophiaFlagChunk):
                pending_flags.append(chunk)
                yield {"event": "flag", "data": {
                    "severity": chunk.severity,
                    "claim": chunk.claim,
                    "description": chunk.description
                }}
            elif isinstance(chunk, SophiaReviewChunk):
                sophia_review = chunk
                yield {"event": "quality_score", "data": {"score": chunk.quality_score}}
            elif isinstance(chunk, SophiaConvergenceChunk):
                convergence_chunk = chunk
                yield {"event": "quality_score", "data": {"score": chunk.quality_score}}

        history.append({"role": "user", "content": sophia_text})

        # Save evolution snapshot and flags
        quality = (sophia_review.quality_score if sophia_review else
                   convergence_chunk.quality_score if convergence_chunk else 0.0)
        if pending_leon:
            _save_evolution(session_id, round_num, pending_leon, quality)
        _save_flags(session_id, round_num, pending_flags)

        # Convergence exit -- the only exit
        if convergence_chunk:
            with Session(_db.engine) as s:
                sess = s.exec(select(DebateSession).where(
                    DebateSession.session_id == session_id
                )).first()
                if sess:
                    sess.status = "converged"
                    s.commit()

            yield {"event": "convergence", "data": {
                "qualityScore": convergence_chunk.quality_score,
                "finalRecommendation": convergence_chunk.final_recommendation,
                "keyTradeoff": convergence_chunk.key_tradeoff,
                "openAdvisories": convergence_chunk.open_advisories,
                "achievementSteps": convergence_chunk.achievement_steps,
                "predictedMetrics": convergence_chunk.predicted_metrics,
                "predictedNarrative": convergence_chunk.predicted_narrative,
                "overallConfidence": convergence_chunk.overall_confidence,
            }}
            break

        # No convergence -> deepen. Pass blocking flags to LEON next round.
        last_blocking_flags = [f.description for f in pending_flags if f.severity == "blocking"]
