import pytest
from unittest.mock import patch
from agents.leon import LeonTextChunk, LeonChunk
from agents.sophia import (SophiaTextChunk, SophiaFlagChunk,
                            SophiaReviewChunk, SophiaConvergenceChunk)

@pytest.mark.asyncio
async def test_orchestrator_converges_after_two_rounds(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/test.db")
    import db as db_module
    from sqlmodel import create_engine, SQLModel
    # Import orchestrator first so all SQLModel tables are registered in metadata
    from orchestrator import run_debate  # noqa: E402  (import order intentional)
    new_engine = create_engine(f"sqlite:///{tmp_path}/test.db")
    db_module.engine = new_engine
    SQLModel.metadata.create_all(new_engine)

    async def leon_r1(*a, **kw):
        yield LeonTextChunk("analysis round 1")
        yield LeonChunk("rec1", ["e1"], ["c1"], [], ["kw1"], 0.6)

    async def sophia_r1(*a, **kw):
        yield SophiaTextChunk("needs work")
        yield SophiaFlagChunk("blocking", "c1", "no evidence for c1")
        yield SophiaReviewChunk(5.0, [{"severity":"blocking","claim":"c1","description":"no evidence"}], "low quality", True)

    async def leon_r2(*a, **kw):
        yield LeonTextChunk("deeper analysis")
        yield LeonChunk("rec2", ["e1","e2"], ["c2"], ["c1"], ["kw2"], 0.8)

    async def sophia_r2(*a, **kw):
        yield SophiaTextChunk("good analysis")
        yield SophiaConvergenceChunk(
            quality_score=8.0,
            final_recommendation="rec2",
            key_tradeoff="complexity vs scale",
            open_advisories=[],
            achievement_steps=[{"title":"s1","description":"d","timeline":"1w","owner":"team"}],
            predicted_metrics=[{"label":"latency","value":"50ms","confidence":0.8}],
            predicted_narrative="outcome narrative",
            overall_confidence=0.8
        )

    # side_effect as a list returns the item directly (not calling it), so we
    # wrap in a callable that pops from the list and calls the generator function.
    leon_funcs = [leon_r1, leon_r2]
    sophia_funcs = [sophia_r1, sophia_r2]

    def leon_side_effect(*a, **kw):
        return leon_funcs.pop(0)(*a, **kw)

    def sophia_side_effect(*a, **kw):
        return sophia_funcs.pop(0)(*a, **kw)

    with patch("orchestrator.LeonAgent") as MockLeon, \
         patch("orchestrator.SophiaAgent") as MockSophia:
        MockLeon.return_value.stream_response.side_effect = leon_side_effect
        MockSophia.return_value.stream_review.side_effect = sophia_side_effect
        events = [e async for e in run_debate("test topic", "sess-test-1")]

    event_types = [e["event"] for e in events]
    assert "convergence" in event_types
    assert len([e for e in events if e["event"] == "round_start"]) == 4
    assert events[-1]["event"] == "convergence"
    assert events[-1]["data"]["qualityScore"] == 8.0
    assert events[-1]["data"]["finalRecommendation"] == "rec2"
