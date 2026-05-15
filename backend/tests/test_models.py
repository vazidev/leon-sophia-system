import pytest
from sqlmodel import Session, SQLModel, create_engine
from models.flags import Flag, Severity
from models.debate import DebateSession, DebateRound, LeonEvolution

@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(eng)
    return eng

def test_flag_creation(engine):
    with Session(engine) as s:
        f = Flag(session_id="s1", round=1, severity=Severity.BLOCKING,
                 claim="test claim", description="test desc")
        s.add(f); s.commit(); s.refresh(f)
    assert f.id is not None
    assert f.severity == Severity.BLOCKING

def test_leon_evolution_append_only(engine):
    with Session(engine) as s:
        e1 = LeonEvolution(session_id="s1", round=1,
            recommendation_snapshot="v1", evidence_count=3,
            claims_added=[], claims_resolved=[], scope_keywords=[],
            confidence_score=0.6, quality_score=0.0)
        e2 = LeonEvolution(session_id="s1", round=2,
            recommendation_snapshot="v2", evidence_count=5,
            claims_added=[], claims_resolved=[], scope_keywords=[],
            confidence_score=0.7, quality_score=6.5)
        s.add(e1); s.add(e2); s.commit()
    with Session(engine) as s:
        rows = s.query(LeonEvolution).filter_by(session_id="s1").all()
    assert len(rows) == 2
    assert rows[0].round == 1
    assert rows[1].round == 2
