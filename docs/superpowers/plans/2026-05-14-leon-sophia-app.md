# LEON–SOPHIA Live Debate App — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a live AI debate PWA where LEON and SOPHIA exchange analysis rounds via Claude API streaming until convergence, with full evolution tracking and installability on Android.

**Architecture:** FastAPI backend serves SSE stream from an infinite deepening loop (LEON → SOPHIA → repeat until quality_score ≥ 7.0 and zero blocking flags). React frontend connects via EventSource, renders rounds live, shows LEON's evolution graphically, and displays the convergence screen. SQLite stores sessions and LeonEvolution snapshots.

**Tech Stack:** Python 3.12, FastAPI, anthropic SDK, SQLModel, SQLite, Server-Sent Events, React 18, TypeScript, Vite, vite-plugin-pwa, Recharts, Vitest, pytest, pytest-asyncio

---

## File Map

**Backend (create all):**
- `backend/requirements.txt`
- `backend/.env.example`
- `backend/main.py` — FastAPI app, CORS, routes
- `backend/db.py` — SQLModel engine + session factory
- `backend/models/flags.py` — Flag, Severity enum
- `backend/models/debate.py` — DebateSession, DebateRound, LeonEvolution
- `backend/agents/leon.py` — LeonAgent class, submit_analysis tool
- `backend/agents/sophia.py` — SophiaAgent class, submit_review + submit_convergence tools
- `backend/orchestrator.py` — infinite deepening loop, SSE event generator
- `backend/analysis.py` — placeholder pandas tool
- `backend/tests/test_models.py`
- `backend/tests/test_orchestrator.py`

**Frontend (create all):**
- `frontend/package.json`
- `frontend/vite.config.ts`
- `frontend/index.html`
- `frontend/public/manifest.json`
- `frontend/public/icon-512.svg`
- `frontend/src/types/debate.ts`
- `frontend/src/hooks/useDebate.ts`
- `frontend/src/hooks/useEvolution.ts`
- `frontend/src/global.css`
- `frontend/src/App.tsx`
- `frontend/src/components/TopBar.tsx`
- `frontend/src/components/InputBar.tsx`
- `frontend/src/components/TimelineSidebar.tsx`
- `frontend/src/components/DetailPanel.tsx`
- `frontend/src/components/evolution/ScoreTimeline.tsx`
- `frontend/src/components/evolution/PositionDiff.tsx`
- `frontend/src/components/evolution/ScopeMap.tsx`
- `frontend/src/components/evolution/RadarChart.tsx`
- `frontend/src/components/evolution/EvidenceGrowth.tsx`
- `frontend/src/components/evolution/EvolutionPanel.tsx`
- `frontend/src/components/convergence/FinalDecision.tsx`
- `frontend/src/components/convergence/AchievementGuide.tsx`
- `frontend/src/components/convergence/PredictedOutcome.tsx`
- `frontend/src/components/convergence/ConvergenceScreen.tsx`
- `frontend/src/components/ServiceWorkerRegister.tsx`
- `frontend/src/sw.ts`
- `frontend/src/tests/useDebate.test.ts`
- `frontend/src/tests/ConvergenceScreen.test.tsx`

---

## Task 1: Backend Scaffolding

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/main.py`

- [ ] **Step 1: Write requirements.txt**

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
anthropic==0.34.0
sqlmodel==0.0.21
python-dotenv==1.0.1
sse-starlette==2.1.3
pandas==2.2.2
numpy==2.1.1
pytest==8.3.3
pytest-asyncio==0.24.0
httpx==0.27.2
```

- [ ] **Step 2: Write .env.example**

```
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=sqlite:///./debate.db
FRONTEND_ORIGIN=http://localhost:5173
```

- [ ] **Step 3: Write the failing test for main.py health check**

Create `backend/tests/test_main.py`:
```python
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
```

- [ ] **Step 4: Run test to verify it fails**

```
cd backend
pip install -r requirements.txt
pytest tests/test_main.py -v
```
Expected: ImportError or 404

- [ ] **Step 5: Write main.py**

```python
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="LEON-SOPHIA Debate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 6: Run test to verify it passes**

```
pytest tests/test_main.py -v
```
Expected: PASSED

- [ ] **Step 7: Commit**

```
git add backend/
git commit -m "feat: backend scaffolding — FastAPI app + requirements"
```

---

## Task 2: Data Models

**Files:**
- Create: `backend/db.py`
- Create: `backend/models/flags.py`
- Create: `backend/models/debate.py`
- Create: `backend/tests/test_models.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_models.py
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
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/test_models.py -v
```
Expected: ModuleNotFoundError

- [ ] **Step 3: Write models/flags.py**

```python
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel

class Severity(str, Enum):
    BLOCKING = "blocking"
    ADVISORY = "advisory"

class Flag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    round: int
    severity: Severity
    claim: str
    description: str
    resolved: bool = False
    resolved_round: Optional[int] = None
```

- [ ] **Step 4: Write models/debate.py**

```python
import json
from typing import Optional
from sqlmodel import Field, SQLModel, Column, Text

class DebateSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True, unique=True)
    topic: str
    status: str = "active"  # active | converged
    created_at: str = ""

class DebateRound(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    round: int
    agent: str  # "leon" | "sophia"
    content: str = Field(sa_column=Column(Text))

class LeonEvolution(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    round: int
    recommendation_snapshot: str = Field(sa_column=Column(Text))
    evidence_count: int
    _claims_added: str = Field(default="[]", sa_column=Column(Text))
    _claims_resolved: str = Field(default="[]", sa_column=Column(Text))
    _scope_keywords: str = Field(default="[]", sa_column=Column(Text))
    confidence_score: float
    quality_score: float

    @property
    def claims_added(self) -> list[str]:
        return json.loads(self._claims_added)

    @claims_added.setter
    def claims_added(self, v: list[str]):
        self._claims_added = json.dumps(v)

    @property
    def claims_resolved(self) -> list[str]:
        return json.loads(self._claims_resolved)

    @claims_resolved.setter
    def claims_resolved(self, v: list[str]):
        self._claims_resolved = json.dumps(v)

    @property
    def scope_keywords(self) -> list[str]:
        return json.loads(self._scope_keywords)

    @scope_keywords.setter
    def scope_keywords(self, v: list[str]):
        self._scope_keywords = json.dumps(v)
```

- [ ] **Step 5: Write db.py**

```python
import os
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./debate.db")
engine = create_engine(DATABASE_URL, echo=False)

def create_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

- [ ] **Step 6: Run tests to verify they pass**

```
pytest tests/test_models.py -v
```
Expected: 2 PASSED

- [ ] **Step 7: Commit**

```
git add backend/models/ backend/db.py backend/tests/test_models.py
git commit -m "feat: data models — Flag, DebateSession, DebateRound, LeonEvolution"
```

---

## Task 3: LEON Agent

**Files:**
- Create: `backend/agents/leon.py`
- Create: `backend/agents/__init__.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_leon.py`:
```python
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from agents.leon import LeonAgent, LeonTextChunk, LeonChunk

@pytest.mark.asyncio
async def test_leon_emits_chunks():
    agent = LeonAgent(api_key="test")

    tool_input = {
        "recommendation": "Use microservices",
        "evidence": ["e1", "e2"],
        "new_claims": ["c1"],
        "resolved_flags": [],
        "scope_keywords": ["scale", "latency"],
        "confidence_score": 0.75
    }

    fake_events = [
        MagicMock(type="content_block_delta",
                  delta=MagicMock(type="text_delta", text="Use micro")),
        MagicMock(type="content_block_delta",
                  delta=MagicMock(type="text_delta", text="services")),
        MagicMock(type="content_block_delta",
                  delta=MagicMock(type="input_json_delta",
                                  partial_json=json.dumps(tool_input))),
        MagicMock(type="message_stop"),
    ]

    async def mock_stream(*args, **kwargs):
        for evt in fake_events:
            yield evt

    with patch.object(agent._client.messages, "stream", new=mock_stream):
        chunks = [c async for c in agent.stream_response("test topic", [], [])]

    text_chunks = [c for c in chunks if isinstance(c, LeonTextChunk)]
    meta_chunks = [c for c in chunks if isinstance(c, LeonChunk)]
    assert len(text_chunks) == 2
    assert text_chunks[0].text == "Use micro"
    assert len(meta_chunks) == 1
    assert meta_chunks[0].recommendation == "Use microservices"
    assert meta_chunks[0].confidence_score == 0.75
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/test_leon.py -v
```
Expected: ModuleNotFoundError

- [ ] **Step 3: Write backend/agents/__init__.py**

```python
```
(empty file)

- [ ] **Step 4: Write backend/agents/leon.py**

```python
import os
import json
from dataclasses import dataclass
from typing import AsyncGenerator
import anthropic

LEON_SYSTEM = """You are LEON, a forward-planning strategic analyst.
Your role: produce well-evidenced analysis and concrete recommendations.
You respond to SOPHIA's critique by deepening your analysis — expanding evidence,
broadening scope, resolving flagged claims. You never concede without evidence.

Use the submit_analysis tool to submit your structured output at the end of your response."""

SUBMIT_ANALYSIS_TOOL = {
    "name": "submit_analysis",
    "description": "Submit LEON's structured analysis for this round.",
    "input_schema": {
        "type": "object",
        "properties": {
            "recommendation": {"type": "string", "description": "LEON's current top recommendation"},
            "evidence": {"type": "array", "items": {"type": "string"}, "description": "Evidence items supporting the recommendation"},
            "new_claims": {"type": "array", "items": {"type": "string"}, "description": "New claims introduced this round"},
            "resolved_flags": {"type": "array", "items": {"type": "string"}, "description": "SOPHIA flag descriptions that LEON has addressed"},
            "scope_keywords": {"type": "array", "items": {"type": "string"}, "description": "New topic areas LEON expanded into this round"},
            "confidence_score": {"type": "number", "description": "LEON's self-assessed confidence 0.0–1.0"}
        },
        "required": ["recommendation", "evidence", "new_claims", "resolved_flags", "scope_keywords", "confidence_score"]
    }
}

@dataclass
class LeonTextChunk:
    text: str

@dataclass
class LeonChunk:
    recommendation: str
    evidence: list[str]
    new_claims: list[str]
    resolved_flags: list[str]
    scope_keywords: list[str]
    confidence_score: float

class LeonAgent:
    def __init__(self, api_key: str | None = None):
        self._client = anthropic.Anthropic(api_key=api_key or os.environ["ANTHROPIC_API_KEY"])

    async def stream_response(
        self,
        topic: str,
        history: list[dict],
        sophia_flags: list[str],
    ) -> AsyncGenerator[LeonTextChunk | LeonChunk, None]:
        messages = list(history)
        flag_context = ""
        if sophia_flags:
            flag_context = "\n\nSOPHIA's blocking flags you must address:\n" + "\n".join(f"- {f}" for f in sophia_flags)

        messages.append({
            "role": "user",
            "content": f"Topic: {topic}{flag_context}\n\nProvide your analysis."
        })

        tool_json_buffer = ""
        collecting_tool = False

        async with self._client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=LEON_SYSTEM,
            messages=messages,
            tools=[SUBMIT_ANALYSIS_TOOL],
        ) as stream:
            async for event in stream:
                if event.type == "content_block_delta":
                    if event.delta.type == "text_delta":
                        yield LeonTextChunk(text=event.delta.text)
                    elif event.delta.type == "input_json_delta":
                        collecting_tool = True
                        tool_json_buffer += event.delta.partial_json
                elif event.type == "message_stop":
                    if collecting_tool:
                        data = json.loads(tool_json_buffer)
                        yield LeonChunk(
                            recommendation=data["recommendation"],
                            evidence=data["evidence"],
                            new_claims=data["new_claims"],
                            resolved_flags=data["resolved_flags"],
                            scope_keywords=data["scope_keywords"],
                            confidence_score=data["confidence_score"],
                        )
```

- [ ] **Step 5: Run tests to verify they pass**

```
pytest tests/test_leon.py -v
```
Expected: PASSED

- [ ] **Step 6: Commit**

```
git add backend/agents/ backend/tests/test_leon.py
git commit -m "feat: LEON agent — streaming analysis with submit_analysis tool"
```

---

## Task 4: SOPHIA Agent

**Files:**
- Create: `backend/agents/sophia.py`

- [ ] **Step 1: Write the failing test**

Create `backend/tests/test_sophia.py`:
```python
import pytest
import json
from unittest.mock import MagicMock, patch
from agents.sophia import SophiaAgent, SophiaFlagChunk, SophiaReviewChunk, SophiaConvergenceChunk

@pytest.mark.asyncio
async def test_sophia_review_emits_flags_and_review():
    agent = SophiaAgent(api_key="test")

    review_input = {
        "quality_score": 5.5,
        "flags": [
            {"severity": "blocking", "claim": "microservices claim",
             "description": "No latency evidence provided"}
        ],
        "summary": "Analysis lacks evidence depth"
    }

    fake_events = [
        MagicMock(type="content_block_delta",
                  delta=MagicMock(type="text_delta", text="Needs work.")),
        MagicMock(type="content_block_delta",
                  delta=MagicMock(type="input_json_delta",
                                  partial_json=json.dumps(review_input))),
        MagicMock(type="message_stop"),
    ]

    async def mock_stream(*args, **kwargs):
        for evt in fake_events:
            yield evt

    with patch.object(agent._client.messages, "stream", new=mock_stream):
        chunks = [c async for c in agent.stream_review("test topic", [], "LEON rec")]

    flag_chunks = [c for c in chunks if isinstance(c, SophiaFlagChunk)]
    review_chunks = [c for c in chunks if isinstance(c, SophiaReviewChunk)]
    assert len(flag_chunks) == 1
    assert flag_chunks[0].severity == "blocking"
    assert review_chunks[0].quality_score == 5.5
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/test_sophia.py -v
```
Expected: ModuleNotFoundError

- [ ] **Step 3: Write backend/agents/sophia.py**

```python
import os
import json
from dataclasses import dataclass, field
from typing import AsyncGenerator
import anthropic

SOPHIA_SYSTEM = """You are SOPHIA, an adversarial critic and ethics governor.
Your role: rigorously evaluate LEON's analysis for logical gaps, unsupported claims,
ethical issues, and scope blindness. Issue blocking flags for each unresolved problem.
When analysis quality reaches 7.0/10 with zero blocking flags, trigger convergence.

Use submit_review for normal reviews. Use submit_convergence only when converged."""

SUBMIT_REVIEW_TOOL = {
    "name": "submit_review",
    "description": "Submit SOPHIA's structured review. Use when quality < 7.0 or blocking flags remain.",
    "input_schema": {
        "type": "object",
        "properties": {
            "quality_score": {"type": "number", "description": "Analysis quality 0.0–10.0"},
            "flags": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "severity": {"type": "string", "enum": ["blocking", "advisory"]},
                        "claim": {"type": "string"},
                        "description": {"type": "string"}
                    },
                    "required": ["severity", "claim", "description"]
                }
            },
            "summary": {"type": "string"}
        },
        "required": ["quality_score", "flags", "summary"]
    }
}

SUBMIT_CONVERGENCE_TOOL = {
    "name": "submit_convergence",
    "description": "Trigger convergence. Use ONLY when quality_score >= 7.0 and zero blocking flags remain.",
    "input_schema": {
        "type": "object",
        "properties": {
            "quality_score": {"type": "number"},
            "final_recommendation": {"type": "string"},
            "key_tradeoff": {"type": "string"},
            "open_advisories": {"type": "array", "items": {"type": "string"}},
            "achievement_steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "timeline": {"type": "string"},
                        "owner": {"type": "string"}
                    },
                    "required": ["title", "description", "timeline", "owner"]
                }
            },
            "predicted_metrics": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string"},
                        "value": {"type": "string"},
                        "confidence": {"type": "number"}
                    },
                    "required": ["label", "value", "confidence"]
                }
            },
            "predicted_narrative": {"type": "string"},
            "overall_confidence": {"type": "number"}
        },
        "required": ["quality_score", "final_recommendation", "key_tradeoff",
                     "open_advisories", "achievement_steps", "predicted_metrics",
                     "predicted_narrative", "overall_confidence"]
    }
}

@dataclass
class SophiaTextChunk:
    text: str

@dataclass
class SophiaFlagChunk:
    severity: str
    claim: str
    description: str

@dataclass
class SophiaReviewChunk:
    quality_score: float
    flags: list[dict]
    summary: str
    is_blocking: bool

@dataclass
class SophiaConvergenceChunk:
    quality_score: float
    final_recommendation: str
    key_tradeoff: str
    open_advisories: list[str]
    achievement_steps: list[dict]
    predicted_metrics: list[dict]
    predicted_narrative: str
    overall_confidence: float

class SophiaAgent:
    def __init__(self, api_key: str | None = None):
        self._client = anthropic.Anthropic(api_key=api_key or os.environ["ANTHROPIC_API_KEY"])

    async def stream_review(
        self,
        topic: str,
        history: list[dict],
        leon_recommendation: str,
    ) -> AsyncGenerator[SophiaTextChunk | SophiaFlagChunk | SophiaReviewChunk | SophiaConvergenceChunk, None]:
        messages = list(history)
        messages.append({
            "role": "user",
            "content": f"Topic: {topic}\n\nLEON's latest recommendation:\n{leon_recommendation}\n\nReview this analysis."
        })

        tool_json_buffer = ""
        active_tool = None

        async with self._client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=SOPHIA_SYSTEM,
            messages=messages,
            tools=[SUBMIT_REVIEW_TOOL, SUBMIT_CONVERGENCE_TOOL],
        ) as stream:
            async for event in stream:
                if event.type == "content_block_start":
                    if hasattr(event.content_block, "name"):
                        active_tool = event.content_block.name
                        tool_json_buffer = ""
                elif event.type == "content_block_delta":
                    if event.delta.type == "text_delta":
                        yield SophiaTextChunk(text=event.delta.text)
                    elif event.delta.type == "input_json_delta":
                        tool_json_buffer += event.delta.partial_json
                elif event.type == "content_block_stop":
                    if active_tool and tool_json_buffer:
                        data = json.loads(tool_json_buffer)
                        if active_tool == "submit_review":
                            blocking = any(f["severity"] == "blocking" for f in data["flags"])
                            for f in data["flags"]:
                                yield SophiaFlagChunk(
                                    severity=f["severity"],
                                    claim=f["claim"],
                                    description=f["description"]
                                )
                            yield SophiaReviewChunk(
                                quality_score=data["quality_score"],
                                flags=data["flags"],
                                summary=data["summary"],
                                is_blocking=blocking
                            )
                        elif active_tool == "submit_convergence":
                            yield SophiaConvergenceChunk(
                                quality_score=data["quality_score"],
                                final_recommendation=data["final_recommendation"],
                                key_tradeoff=data["key_tradeoff"],
                                open_advisories=data["open_advisories"],
                                achievement_steps=data["achievement_steps"],
                                predicted_metrics=data["predicted_metrics"],
                                predicted_narrative=data["predicted_narrative"],
                                overall_confidence=data["overall_confidence"]
                            )
                        active_tool = None
                        tool_json_buffer = ""
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/test_sophia.py -v
```
Expected: PASSED

- [ ] **Step 5: Commit**

```
git add backend/agents/sophia.py backend/tests/test_sophia.py
git commit -m "feat: SOPHIA agent — streaming review with submit_review + submit_convergence tools"
```

---

## Task 5: Orchestrator

**Files:**
- Create: `backend/orchestrator.py`
- Create: `backend/tests/test_orchestrator.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_orchestrator.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from agents.leon import LeonTextChunk, LeonChunk
from agents.sophia import SophiaTextChunk, SophiaFlagChunk, SophiaReviewChunk, SophiaConvergenceChunk

@pytest.mark.asyncio
async def test_orchestrator_converges_after_two_rounds(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/test.db")
    from db import engine
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)

    from orchestrator import run_debate

    leon_round1 = [LeonTextChunk("analysis"), LeonChunk("rec1", ["e1"], ["c1"], [], ["kw1"], 0.6)]
    sophia_round1 = [SophiaTextChunk("needs work"), SophiaFlagChunk("blocking", "c1", "desc"), SophiaReviewChunk(5.0, [], "low", True)]
    leon_round2 = [LeonTextChunk("better analysis"), LeonChunk("rec2", ["e1","e2"], ["c2"], ["c1"], ["kw2"], 0.8)]
    sophia_conv = [SophiaTextChunk("good"), SophiaConvergenceChunk(8.0, "rec2", "tradeoff", [], [{"title":"s1","description":"d","timeline":"1w","owner":"team"}], [{"label":"latency","value":"50ms","confidence":0.8}], "narrative", 0.8)]

    async def leon_stream_r1(*a, **kw):
        for c in leon_round1: yield c
    async def sophia_stream_r1(*a, **kw):
        for c in sophia_round1: yield c
    async def leon_stream_r2(*a, **kw):
        for c in leon_round2: yield c
    async def sophia_stream_r2(*a, **kw):
        for c in sophia_conv: yield c

    leon_calls = [leon_stream_r1, leon_stream_r2]
    sophia_calls = [sophia_stream_r1, sophia_stream_r2]

    with patch("orchestrator.LeonAgent") as MockLeon, \
         patch("orchestrator.SophiaAgent") as MockSophia:
        MockLeon.return_value.stream_response.side_effect = leon_calls
        MockSophia.return_value.stream_review.side_effect = sophia_calls

        events = [e async for e in run_debate("test topic", "sess-1")]

    event_types = [e["event"] for e in events]
    assert "convergence" in event_types
    assert event_types.count("round_start") == 4  # 2 LEON + 2 SOPHIA
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/test_orchestrator.py -v
```
Expected: ModuleNotFoundError

- [ ] **Step 3: Write backend/orchestrator.py**

```python
import json
from datetime import datetime
from typing import AsyncGenerator
from sqlmodel import Session, select
from db import engine
from models.debate import DebateSession, DebateRound, LeonEvolution
from models.flags import Flag, Severity
from agents.leon import LeonAgent, LeonTextChunk, LeonChunk
from agents.sophia import SophiaAgent, SophiaTextChunk, SophiaFlagChunk, SophiaReviewChunk, SophiaConvergenceChunk

def _save_evolution(session_id: str, round_num: int, leon: LeonChunk, quality_score: float):
    with Session(engine) as s:
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
    with Session(engine) as s:
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
    history = []
    round_num = 0
    last_blocking_flags: list[str] = []
    pending_flags: list[SophiaFlagChunk] = []
    pending_leon: LeonChunk | None = None

    with Session(engine) as s:
        s.add(DebateSession(session_id=session_id, topic=topic,
                            created_at=datetime.utcnow().isoformat()))
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
        round_num_sophia = round_num
        yield {"event": "round_start", "data": {"round": round_num_sophia, "agent": "sophia"}}
        sophia_text = ""
        pending_flags = []
        sophia_review = None
        convergence_chunk = None

        async for chunk in sophia.stream_review(topic, history, pending_leon.recommendation if pending_leon else ""):
            if isinstance(chunk, SophiaTextChunk):
                sophia_text += chunk.text
                yield {"event": "token", "data": {"text": chunk.text}}
            elif isinstance(chunk, SophiaFlagChunk):
                pending_flags.append(chunk)
                yield {"event": "flag", "data": {"severity": chunk.severity, "claim": chunk.claim, "description": chunk.description}}
            elif isinstance(chunk, SophiaReviewChunk):
                sophia_review = chunk
                yield {"event": "quality_score", "data": {"score": chunk.quality_score}}
            elif isinstance(chunk, SophiaConvergenceChunk):
                convergence_chunk = chunk
                yield {"event": "quality_score", "data": {"score": chunk.quality_score}}

        history.append({"role": "user", "content": sophia_text})

        # Save evolution snapshot
        quality = (sophia_review.quality_score if sophia_review else
                   convergence_chunk.quality_score if convergence_chunk else 0.0)
        if pending_leon:
            _save_evolution(session_id, round_num, pending_leon, quality)
        _save_flags(session_id, round_num, pending_flags)

        # Convergence check
        if convergence_chunk:
            with Session(engine) as s:
                sess = s.exec(select(DebateSession).where(DebateSession.session_id == session_id)).first()
                if sess:
                    sess.status = "converged"
                    s.commit()

            conv_data = {
                "qualityScore": convergence_chunk.quality_score,
                "finalRecommendation": convergence_chunk.final_recommendation,
                "keyTradeoff": convergence_chunk.key_tradeoff,
                "openAdvisories": convergence_chunk.open_advisories,
                "achievementSteps": convergence_chunk.achievement_steps,
                "predictedMetrics": convergence_chunk.predicted_metrics,
                "predictedNarrative": convergence_chunk.predicted_narrative,
                "overallConfidence": convergence_chunk.overall_confidence,
            }
            yield {"event": "convergence", "data": conv_data}
            break

        # No convergence — deepen
        last_blocking_flags = [f.description for f in pending_flags if f.severity == "blocking"]
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/test_orchestrator.py -v
```
Expected: PASSED

- [ ] **Step 5: Commit**

```
git add backend/orchestrator.py backend/tests/test_orchestrator.py
git commit -m "feat: infinite deepening orchestrator — convergence-only exit"
```

---

## Task 6: FastAPI Routes + SSE

**Files:**
- Modify: `backend/main.py`
- Create: `backend/tests/test_routes.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_routes.py
import pytest
import json
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_start_debate(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/test.db")
    from db import create_db
    create_db()

    with patch("main.run_debate") as mock_run:
        async def fake_debate(topic, sid):
            yield {"event": "round_start", "data": {"round": 1, "agent": "leon"}}

        mock_run.return_value = fake_debate("test", "sid")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.post("/api/debate/start", json={"topic": "test topic"})

    assert r.status_code == 200
    assert "session_id" in r.json()
```

- [ ] **Step 2: Run test to verify it fails**

```
pytest tests/test_routes.py -v
```
Expected: 404 or AttributeError

- [ ] **Step 3: Update main.py with full routes**

```python
import os
import json
import uuid
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session, select
from dotenv import load_dotenv
from db import engine, create_db, get_session
from models.debate import DebateSession, LeonEvolution
from orchestrator import run_debate

load_dotenv()
create_db()

app = FastAPI(title="LEON-SOPHIA Debate API")

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
async def stream_debate(session_id: str, topic: str):
    async def event_generator():
        async for event in run_debate(topic, session_id):
            yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.get("/api/debate/{session_id}/state")
async def get_state(session_id: str, s: Session = Depends(get_session)):
    sess = s.exec(select(DebateSession).where(DebateSession.session_id == session_id)).first()
    return sess or {}

@app.get("/api/debate/{session_id}/evolution")
async def get_evolution(session_id: str, s: Session = Depends(get_session)):
    rows = s.exec(select(LeonEvolution).where(LeonEvolution.session_id == session_id)).all()
    return [{"round": r.round, "recommendationSnapshot": r.recommendation_snapshot,
             "evidenceCount": r.evidence_count, "claimsAdded": r.claims_added,
             "scopeKeywords": r.scope_keywords, "confidenceScore": r.confidence_score,
             "qualityScore": r.quality_score} for r in rows]
```

- [ ] **Step 4: Run tests to verify they pass**

```
pytest tests/test_routes.py tests/test_main.py -v
```
Expected: all PASSED

- [ ] **Step 5: Smoke test the running server**

```
cd backend && uvicorn main:app --reload
# In another terminal:
curl http://localhost:8000/health
```
Expected: `{"status":"ok"}`

- [ ] **Step 6: Commit**

```
git add backend/main.py backend/tests/test_routes.py
git commit -m "feat: FastAPI routes — start, stream SSE, state, evolution endpoints"
```

---

## Task 7: Frontend Scaffolding + TypeScript Types

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/types/debate.ts`

- [ ] **Step 1: Write frontend/package.json**

```json
{
  "name": "leon-sophia-ui",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest run"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "recharts": "^2.12.7"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "typescript": "^5.5.3",
    "vite": "^5.4.2",
    "vite-plugin-pwa": "^0.20.5",
    "vitest": "^2.0.5",
    "@testing-library/react": "^16.0.0",
    "@testing-library/jest-dom": "^6.4.8",
    "jsdom": "^25.0.0"
  }
}
```

- [ ] **Step 2: Write frontend/vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'LEON · SOPHIA',
        short_name: 'LEON·SOPHIA',
        start_url: '/',
        display: 'standalone',
        background_color: '#f6f8fa',
        theme_color: '#0969da',
        icons: [{ src: '/icon-512.svg', sizes: '512x512', type: 'image/svg+xml' }]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: []
      }
    })
  ],
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.ts']
  }
})
```

- [ ] **Step 3: Write frontend/index.html**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#0969da" />
    <link rel="manifest" href="/manifest.json" />
    <title>LEON · SOPHIA</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 4: Write frontend/src/types/debate.ts**

```typescript
export type Severity = 'blocking' | 'advisory'

export interface DebateFlag {
  severity: Severity
  claim: string
  description: string
}

export interface RoundEntry {
  round: number
  agent: 'leon' | 'sophia'
  text: string
  flags: DebateFlag[]
  qualityScore?: number
  streaming: boolean
}

export interface AchievementStep {
  title: string
  description: string
  timeline: string
  owner: string
}

export interface PredictedMetric {
  label: string
  value: string
  confidence: number
}

export interface ConvergenceData {
  qualityScore: number
  finalRecommendation: string
  keyTradeoff: string
  openAdvisories: string[]
  achievementSteps: AchievementStep[]
  predictedMetrics: PredictedMetric[]
  predictedNarrative: string
  overallConfidence: number
}

export interface LeonEvolutionRow {
  round: number
  recommendationSnapshot: string
  evidenceCount: number
  claimsAdded: string[]
  scopeKeywords: string[]
  confidenceScore: number
  qualityScore: number
}

export type DebateState =
  | { phase: 'idle' }
  | { phase: 'running'; sessionId: string; topic: string; rounds: RoundEntry[] }
  | { phase: 'converged'; sessionId: string; topic: string; rounds: RoundEntry[]; convergence: ConvergenceData }
```

- [ ] **Step 5: Install dependencies**

```
cd frontend
npm install
```

- [ ] **Step 6: Verify TypeScript compiles**

```
cd frontend
npx tsc --noEmit
```
Expected: no errors

- [ ] **Step 7: Commit**

```
git add frontend/
git commit -m "feat: frontend scaffold — Vite+React+TS, PWA config, debate types"
```

---

## Task 8: useDebate + useEvolution Hooks

**Files:**
- Create: `frontend/src/hooks/useDebate.ts`
- Create: `frontend/src/hooks/useEvolution.ts`
- Create: `frontend/src/tests/setup.ts`
- Create: `frontend/src/tests/useDebate.test.ts`

- [ ] **Step 1: Write frontend/src/tests/setup.ts**

```typescript
import '@testing-library/jest-dom'
```

- [ ] **Step 2: Write the failing test**

```typescript
// frontend/src/tests/useDebate.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useDebate } from '../hooks/useDebate'

describe('useDebate', () => {
  it('starts in idle phase', () => {
    const { result } = renderHook(() => useDebate())
    expect(result.current.state.phase).toBe('idle')
  })

  it('transitions to running phase on startDebate', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      json: async () => ({ session_id: 'test-session' })
    }) as any

    const mockES = {
      addEventListener: vi.fn(),
      close: vi.fn(),
    }
    global.EventSource = vi.fn(() => mockES) as any

    const { result } = renderHook(() => useDebate())

    await act(async () => {
      await result.current.startDebate('test topic')
    })

    expect(result.current.state.phase).toBe('running')
  })
})
```

- [ ] **Step 3: Run test to verify it fails**

```
cd frontend && npm test
```
Expected: cannot find module

- [ ] **Step 4: Write frontend/src/hooks/useDebate.ts**

```typescript
import { useState, useRef, useCallback } from 'react'
import type { DebateState, RoundEntry, DebateFlag, ConvergenceData } from '../types/debate'

export function useDebate() {
  const [state, setState] = useState<DebateState>({ phase: 'idle' })
  const esRef = useRef<EventSource | null>(null)

  const startDebate = useCallback(async (topic: string) => {
    const res = await fetch('/api/debate/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic })
    })
    const { session_id } = await res.json()

    setState({ phase: 'running', sessionId: session_id, topic, rounds: [] })

    const es = new EventSource(`/api/debate/${session_id}/stream?topic=${encodeURIComponent(topic)}`)
    esRef.current = es

    const getRounds = () => {
      let rounds: RoundEntry[] = []
      setState(s => { if (s.phase === 'running' || s.phase === 'converged') rounds = s.rounds; return s })
      return rounds
    }

    es.addEventListener('round_start', (e) => {
      const { round, agent } = JSON.parse((e as MessageEvent).data)
      setState(s => {
        if (s.phase !== 'running') return s
        return {
          ...s,
          rounds: [...s.rounds, { round, agent, text: '', flags: [], streaming: true }]
        }
      })
    })

    es.addEventListener('token', (e) => {
      const { text } = JSON.parse((e as MessageEvent).data)
      setState(s => {
        if (s.phase !== 'running') return s
        const rounds = [...s.rounds]
        if (rounds.length === 0) return s
        const last = { ...rounds[rounds.length - 1] }
        last.text += text
        rounds[rounds.length - 1] = last
        return { ...s, rounds }
      })
    })

    es.addEventListener('flag', (e) => {
      const flag: DebateFlag = JSON.parse((e as MessageEvent).data)
      setState(s => {
        if (s.phase !== 'running') return s
        const rounds = [...s.rounds]
        if (rounds.length === 0) return s
        const last = { ...rounds[rounds.length - 1] }
        last.flags = [...last.flags, flag]
        rounds[rounds.length - 1] = last
        return { ...s, rounds }
      })
    })

    es.addEventListener('quality_score', (e) => {
      const { score } = JSON.parse((e as MessageEvent).data)
      setState(s => {
        if (s.phase !== 'running') return s
        const rounds = [...s.rounds]
        if (rounds.length === 0) return s
        const last = { ...rounds[rounds.length - 1] }
        last.qualityScore = score
        last.streaming = false
        rounds[rounds.length - 1] = last
        return { ...s, rounds }
      })
    })

    es.addEventListener('convergence', (e) => {
      const convergence: ConvergenceData = JSON.parse((e as MessageEvent).data)
      es.close()
      setState(s => {
        if (s.phase !== 'running') return s
        return { phase: 'converged', sessionId: s.sessionId, topic: s.topic, rounds: s.rounds, convergence }
      })
    })

    es.onerror = () => {
      es.close()
    }
  }, [])

  const reset = useCallback(() => {
    esRef.current?.close()
    setState({ phase: 'idle' })
  }, [])

  return { state, startDebate, reset }
}
```

- [ ] **Step 5: Write frontend/src/hooks/useEvolution.ts**

```typescript
import { useState, useEffect } from 'react'
import type { LeonEvolutionRow } from '../types/debate'

export function useEvolution(sessionId: string | null) {
  const [evolution, setEvolution] = useState<LeonEvolutionRow[]>([])

  useEffect(() => {
    if (!sessionId) return
    const interval = setInterval(async () => {
      const res = await fetch(`/api/debate/${sessionId}/evolution`)
      if (res.ok) setEvolution(await res.json())
    }, 2000)
    return () => clearInterval(interval)
  }, [sessionId])

  return evolution
}
```

- [ ] **Step 6: Run tests to verify they pass**

```
cd frontend && npm test
```
Expected: all PASSED

- [ ] **Step 7: Commit**

```
git add frontend/src/hooks/ frontend/src/tests/
git commit -m "feat: useDebate + useEvolution hooks — SSE EventSource management"
```

---

## Task 9: App Shell — global.css, TopBar, InputBar, App.tsx

**Files:**
- Create: `frontend/src/global.css`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/components/TopBar.tsx`
- Create: `frontend/src/components/InputBar.tsx`

- [ ] **Step 1: Write frontend/src/global.css**

```css
:root {
  --bg: #f6f8fa;
  --surface: #ffffff;
  --border: #d0d7de;
  --leon: #0969da;
  --sophia: #cf222e;
  --converged: #1a7f37;
  --advisory: #d29922;
  --text: #1f2328;
  --text-secondary: #57606a;
  --radius: 8px;
  --radius-chip: 20px;
  font-family: 'Segoe UI', -apple-system, sans-serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body { background: var(--bg); color: var(--text); height: 100dvh; overflow: hidden; }

#root { height: 100dvh; display: flex; flex-direction: column; }

.surface { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); }

.chip {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 10px; border-radius: var(--radius-chip);
  font-size: 12px; font-weight: 500;
}
.chip-leon { background: #dbeafe; color: var(--leon); }
.chip-sophia { background: #fee2e2; color: var(--sophia); }
.chip-converged { background: #dcfce7; color: var(--converged); }
.chip-blocking { background: #fee2e2; color: var(--sophia); }
.chip-advisory { background: #fef9c3; color: var(--advisory); }
```

- [ ] **Step 2: Write frontend/src/main.tsx**

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import './global.css'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

- [ ] **Step 3: Write frontend/src/components/TopBar.tsx**

```tsx
import React from 'react'

interface Props {
  topic: string
  status: 'idle' | 'running' | 'converged'
}

export function TopBar({ topic, status }: Props) {
  const statusText = status === 'idle' ? 'Ready' : status === 'running' ? 'Debating...' : 'Converged'
  const statusColor = status === 'idle' ? 'var(--text-secondary)' : status === 'running' ? 'var(--leon)' : 'var(--converged)'

  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '12px 20px', background: 'var(--surface)',
      borderBottom: '1px solid var(--border)', flexShrink: 0
    }}>
      <span style={{ fontWeight: 700, fontSize: 18 }}>LEON · SOPHIA</span>
      {topic && <span style={{ fontSize: 14, color: 'var(--text-secondary)', maxWidth: 400, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{topic}</span>}
      <span style={{ fontSize: 13, color: statusColor, fontWeight: 500 }}>{statusText}</span>
    </div>
  )
}
```

- [ ] **Step 4: Write frontend/src/components/InputBar.tsx**

```tsx
import React, { useState } from 'react'

interface Props {
  onStart: (topic: string) => void
  onReset: () => void
  disabled: boolean
}

export function InputBar({ onStart, onReset, disabled }: Props) {
  const [topic, setTopic] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (topic.trim()) onStart(topic.trim())
  }

  return (
    <form onSubmit={handleSubmit} style={{
      display: 'flex', gap: 8, padding: '12px 20px',
      background: 'var(--surface)', borderTop: '1px solid var(--border)', flexShrink: 0
    }}>
      <input
        value={topic}
        onChange={e => setTopic(e.target.value)}
        placeholder="Enter debate topic..."
        disabled={disabled}
        style={{
          flex: 1, padding: '8px 12px', borderRadius: 'var(--radius)',
          border: '1px solid var(--border)', fontSize: 14, outline: 'none',
          background: disabled ? 'var(--bg)' : 'var(--surface)'
        }}
      />
      <button type="submit" disabled={disabled || !topic.trim()} style={{
        padding: '8px 16px', borderRadius: 'var(--radius)',
        background: 'var(--leon)', color: '#fff', border: 'none',
        cursor: disabled ? 'not-allowed' : 'pointer', fontWeight: 600
      }}>
        Start Debate
      </button>
      <button type="button" onClick={onReset} style={{
        padding: '8px 16px', borderRadius: 'var(--radius)',
        background: 'var(--bg)', border: '1px solid var(--border)',
        cursor: 'pointer', fontWeight: 500
      }}>
        New Debate
      </button>
    </form>
  )
}
```

- [ ] **Step 5: Write frontend/src/App.tsx**

```tsx
import React, { useState } from 'react'
import { TopBar } from './components/TopBar'
import { InputBar } from './components/InputBar'
import { TimelineSidebar } from './components/TimelineSidebar'
import { DetailPanel } from './components/DetailPanel'
import { EvolutionPanel } from './components/evolution/EvolutionPanel'
import { ConvergenceScreen } from './components/convergence/ConvergenceScreen'
import { useDebate } from './hooks/useDebate'
import { useEvolution } from './hooks/useEvolution'
import type { RoundEntry } from './types/debate'

export default function App() {
  const { state, startDebate, reset } = useDebate()
  const [selectedRound, setSelectedRound] = useState<RoundEntry | null>(null)
  const [activeTab, setActiveTab] = useState<'debate' | 'evolution'>('debate')

  const sessionId = state.phase !== 'idle' ? state.sessionId : null
  const evolution = useEvolution(sessionId)
  const rounds = state.phase !== 'idle' ? state.rounds : []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100dvh' }}>
      <TopBar
        topic={state.phase !== 'idle' ? state.topic : ''}
        status={state.phase}
      />

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Sidebar */}
        <div style={{ width: 220, borderRight: '1px solid var(--border)', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', borderBottom: '1px solid var(--border)' }}>
            {(['debate', 'evolution'] as const).map(tab => (
              <button key={tab} onClick={() => setActiveTab(tab)} style={{
                flex: 1, padding: '8px', border: 'none', cursor: 'pointer',
                background: activeTab === tab ? 'var(--surface)' : 'var(--bg)',
                fontWeight: activeTab === tab ? 600 : 400,
                borderBottom: activeTab === tab ? '2px solid var(--leon)' : '2px solid transparent',
                fontSize: 13
              }}>
                {tab === 'debate' ? 'Timeline' : 'Evolution'}
              </button>
            ))}
          </div>
          {activeTab === 'debate' ? (
            <TimelineSidebar
              rounds={rounds}
              selectedRound={selectedRound}
              onSelect={setSelectedRound}
            />
          ) : (
            <EvolutionPanel evolution={evolution} />
          )}
        </div>

        {/* Detail area */}
        <div style={{ flex: 1, overflow: 'auto' }}>
          {state.phase === 'converged' && !selectedRound ? (
            <ConvergenceScreen
              convergence={state.convergence}
              onViewDebate={() => rounds.length > 0 && setSelectedRound(rounds[0])}
              onNewDebate={reset}
            />
          ) : (
            <DetailPanel round={selectedRound || rounds[rounds.length - 1] || null} />
          )}
        </div>
      </div>

      <InputBar
        onStart={startDebate}
        onReset={reset}
        disabled={state.phase === 'running'}
      />
    </div>
  )
}
```

- [ ] **Step 6: Verify TypeScript compiles**

```
cd frontend && npx tsc --noEmit
```
Expected: no errors (components referenced but not yet created will show import errors — expected at this stage)

- [ ] **Step 7: Commit**

```
git add frontend/src/
git commit -m "feat: app shell — TopBar, InputBar, App layout with tab switching"
```

---

## Task 10: TimelineSidebar + DetailPanel

**Files:**
- Create: `frontend/src/components/TimelineSidebar.tsx`
- Create: `frontend/src/components/DetailPanel.tsx`

- [ ] **Step 1: Write frontend/src/components/TimelineSidebar.tsx**

```tsx
import React from 'react'
import type { RoundEntry } from '../types/debate'

interface Props {
  rounds: RoundEntry[]
  selectedRound: RoundEntry | null
  onSelect: (round: RoundEntry) => void
}

export function TimelineSidebar({ rounds, selectedRound, onSelect }: Props) {
  return (
    <div style={{ flex: 1, overflowY: 'auto', padding: 8 }}>
      {rounds.length === 0 && (
        <p style={{ color: 'var(--text-secondary)', fontSize: 13, padding: 8 }}>
          Debate rounds will appear here.
        </p>
      )}
      {rounds.map((r, i) => {
        const isSelected = selectedRound === r
        const isLeon = r.agent === 'leon'
        return (
          <div
            key={i}
            onClick={() => onSelect(r)}
            style={{
              padding: '8px 10px', marginBottom: 4, borderRadius: 'var(--radius)',
              cursor: 'pointer', border: isSelected ? `2px solid ${isLeon ? 'var(--leon)' : 'var(--sophia)'}` : '1px solid var(--border)',
              background: isSelected ? (isLeon ? '#eff6ff' : '#fff1f2') : 'var(--surface)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <span className={`chip chip-${r.agent}`}>{r.agent.toUpperCase()}</span>
              <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>R{r.round}</span>
              {r.streaming && <span style={{ fontSize: 11, color: 'var(--leon)' }}>●</span>}
            </div>
            {r.qualityScore !== undefined && (
              <div style={{ fontSize: 12, marginTop: 4, color: r.qualityScore >= 7 ? 'var(--converged)' : 'var(--text-secondary)' }}>
                Score: {r.qualityScore.toFixed(1)}
              </div>
            )}
            {r.flags.length > 0 && (
              <div style={{ fontSize: 11, marginTop: 3, color: r.flags.some(f => f.severity === 'blocking') ? 'var(--sophia)' : 'var(--advisory)' }}>
                {r.flags.length} flag{r.flags.length > 1 ? 's' : ''}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
```

- [ ] **Step 2: Write frontend/src/components/DetailPanel.tsx**

```tsx
import React from 'react'
import type { RoundEntry } from '../types/debate'

interface Props {
  round: RoundEntry | null
}

export function DetailPanel({ round }: Props) {
  if (!round) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-secondary)' }}>
        <p>Select a round or start a debate.</p>
      </div>
    )
  }

  const isLeon = round.agent === 'leon'
  const accentColor = isLeon ? 'var(--leon)' : 'var(--sophia)'

  return (
    <div style={{ padding: 24, maxWidth: 860, margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <span className={`chip chip-${round.agent}`}>{round.agent.toUpperCase()}</span>
        <span style={{ fontSize: 16, fontWeight: 600 }}>Round {round.round}</span>
        {round.qualityScore !== undefined && (
          <span style={{ marginLeft: 'auto', fontWeight: 600, color: round.qualityScore >= 7 ? 'var(--converged)' : 'var(--text-secondary)' }}>
            Quality: {round.qualityScore.toFixed(1)} / 10
          </span>
        )}
      </div>

      {/* Score bar */}
      {round.qualityScore !== undefined && (
        <div style={{ height: 6, background: 'var(--border)', borderRadius: 3, marginBottom: 16 }}>
          <div style={{
            height: '100%', borderRadius: 3,
            width: `${(round.qualityScore / 10) * 100}%`,
            background: round.qualityScore >= 7 ? 'var(--converged)' : accentColor,
            transition: 'width 0.4s ease'
          }} />
        </div>
      )}

      {/* Main text */}
      <div style={{ fontSize: 15, lineHeight: 1.7, whiteSpace: 'pre-wrap', marginBottom: 16 }}>
        {round.text}
        {round.streaming && <span style={{ display: 'inline-block', width: 2, height: '1em', background: accentColor, marginLeft: 2, animation: 'blink 1s step-end infinite', verticalAlign: 'text-bottom' }} />}
      </div>

      {/* Flags */}
      {round.flags.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8, color: 'var(--text-secondary)' }}>SOPHIA Flags</div>
          {round.flags.map((f, i) => (
            <div key={i} style={{
              padding: '10px 14px', borderRadius: 'var(--radius)', marginBottom: 6,
              borderLeft: `3px solid ${f.severity === 'blocking' ? 'var(--sophia)' : 'var(--advisory)'}`,
              background: f.severity === 'blocking' ? '#fff1f2' : '#fefce8'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                <span className={`chip chip-${f.severity}`}>{f.severity.toUpperCase()}</span>
                <span style={{ fontSize: 13, fontWeight: 500 }}>{f.claim}</span>
              </div>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{f.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 3: Add CSS blink keyframe to global.css**

Append to `frontend/src/global.css`:
```css
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
```

- [ ] **Step 4: Commit**

```
git add frontend/src/components/TimelineSidebar.tsx frontend/src/components/DetailPanel.tsx frontend/src/global.css
git commit -m "feat: TimelineSidebar + DetailPanel — round list + streaming detail view"
```

---

## Task 11: Evolution Panel

**Files:**
- Create: `frontend/src/components/evolution/ScoreTimeline.tsx`
- Create: `frontend/src/components/evolution/PositionDiff.tsx`
- Create: `frontend/src/components/evolution/ScopeMap.tsx`
- Create: `frontend/src/components/evolution/EvidenceGrowth.tsx`
- Create: `frontend/src/components/evolution/RadarChart.tsx`
- Create: `frontend/src/components/evolution/EvolutionPanel.tsx`

- [ ] **Step 1: Write ScoreTimeline.tsx**

```tsx
import React from 'react'
import type { LeonEvolutionRow } from '../../types/debate'

interface Props { evolution: LeonEvolutionRow[] }

export function ScoreTimeline({ evolution }: Props) {
  if (evolution.length === 0) return <p style={{ color: 'var(--text-secondary)', fontSize: 12 }}>No rounds yet.</p>

  const w = 180; const h = 80; const pad = 10
  const plotW = w - pad * 2; const plotH = h - pad * 2
  const maxScore = 10
  const pts = evolution.map((r, i) => ({
    x: pad + (i / Math.max(evolution.length - 1, 1)) * plotW,
    y: pad + plotH - (r.qualityScore / maxScore) * plotH
  }))
  const polyline = pts.map(p => `${p.x},${p.y}`).join(' ')

  return (
    <svg width={w} height={h} style={{ width: '100%' }}>
      {/* threshold line at 7.0 */}
      <line x1={pad} y1={pad + plotH - (7 / maxScore) * plotH} x2={w - pad} y2={pad + plotH - (7 / maxScore) * plotH}
        stroke="var(--converged)" strokeWidth={1} strokeDasharray="3,3" />
      <polyline fill="none" stroke="var(--leon)" strokeWidth={2} points={polyline} />
      {pts.map((p, i) => (
        <circle key={i} cx={p.x} cy={p.y} r={3}
          fill={evolution[i].qualityScore >= 7 ? 'var(--converged)' : 'var(--leon)'} />
      ))}
    </svg>
  )
}
```

- [ ] **Step 2: Write PositionDiff.tsx**

```tsx
import React from 'react'
import type { LeonEvolutionRow } from '../../types/debate'

interface Props { evolution: LeonEvolutionRow[] }

export function PositionDiff({ evolution }: Props) {
  return (
    <div style={{ fontSize: 12, lineHeight: 1.5 }}>
      {evolution.map((r) => (
        <div key={r.round} style={{ marginBottom: 10, padding: '6px 8px', borderLeft: '3px solid var(--leon)', background: '#eff6ff', borderRadius: '0 var(--radius) var(--radius) 0' }}>
          <div style={{ display: 'flex', gap: 6, marginBottom: 4 }}>
            <span className="chip chip-leon">R{r.round}</span>
            <span style={{ color: 'var(--text-secondary)' }}>Score: {r.qualityScore.toFixed(1)}</span>
          </div>
          <p style={{ fontSize: 11, color: 'var(--text)', margin: 0 }}>
            {r.recommendationSnapshot.slice(0, 120)}{r.recommendationSnapshot.length > 120 ? '...' : ''}
          </p>
          {r.claimsAdded.length > 0 && (
            <div style={{ marginTop: 4 }}>
              {r.claimsAdded.map((c, i) => <span key={i} style={{ fontSize: 10, background: '#dcfce7', color: 'var(--converged)', borderRadius: 4, padding: '1px 4px', marginRight: 3 }}>+{c}</span>)}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
```

- [ ] **Step 3: Write ScopeMap.tsx**

```tsx
import React from 'react'
import type { LeonEvolutionRow } from '../../types/debate'

interface Props { evolution: LeonEvolutionRow[] }

export function ScopeMap({ evolution }: Props) {
  const allKeywords = evolution.flatMap(r => r.scopeKeywords.map(kw => ({ kw, round: r.round })))
  const cx = 90; const cy = 90; const r = 70

  return (
    <svg width={180} height={180} style={{ width: '100%' }}>
      <circle cx={cx} cy={cy} r={20} fill="var(--leon)" />
      <text x={cx} y={cy + 5} textAnchor="middle" fill="#fff" fontSize={9} fontWeight="bold">TOPIC</text>
      {allKeywords.slice(0, 8).map((item, i) => {
        const angle = (i / Math.min(allKeywords.length, 8)) * 2 * Math.PI - Math.PI / 2
        const nx = cx + r * Math.cos(angle)
        const ny = cy + r * Math.sin(angle)
        return (
          <g key={i}>
            <line x1={cx} y1={cy} x2={nx} y2={ny} stroke="var(--border)" strokeWidth={1} />
            <circle cx={nx} cy={ny} r={12} fill="#eff6ff" stroke="var(--leon)" strokeWidth={1} />
            <text x={nx} y={ny + 4} textAnchor="middle" fill="var(--leon)" fontSize={7}>{item.kw.slice(0, 6)}</text>
          </g>
        )
      })}
    </svg>
  )
}
```

- [ ] **Step 4: Write EvidenceGrowth.tsx**

```tsx
import React from 'react'
import type { LeonEvolutionRow } from '../../types/debate'

interface Props { evolution: LeonEvolutionRow[] }

export function EvidenceGrowth({ evolution }: Props) {
  if (evolution.length === 0) return null
  const maxEvidence = Math.max(...evolution.map(r => r.evidenceCount), 1)

  return (
    <div>
      {evolution.map(r => (
        <div key={r.round} style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4, fontSize: 11 }}>
          <span style={{ width: 24, color: 'var(--text-secondary)', textAlign: 'right' }}>R{r.round}</span>
          <div style={{ flex: 1, height: 12, background: 'var(--bg)', borderRadius: 6, overflow: 'hidden' }}>
            <div style={{ height: '100%', background: 'var(--leon)', width: `${(r.evidenceCount / maxEvidence) * 100}%`, borderRadius: 6 }} />
          </div>
          <span style={{ width: 20, color: 'var(--text-secondary)' }}>{r.evidenceCount}</span>
        </div>
      ))}
    </div>
  )
}
```

- [ ] **Step 5: Write RadarChart.tsx**

```tsx
import React from 'react'
import type { LeonEvolutionRow } from '../../types/debate'

interface Props { evolution: LeonEvolutionRow[] }

const AXES = ['Evidence', 'Scope', 'Confidence', 'Depth', 'Specificity', 'Risk']

function polarToXY(angle: number, radius: number, cx: number, cy: number) {
  return { x: cx + radius * Math.cos(angle - Math.PI / 2), y: cy + radius * Math.sin(angle - Math.PI / 2) }
}

export function RadarChart({ evolution }: Props) {
  if (evolution.length === 0) return null
  const first = evolution[0]
  const last = evolution[evolution.length - 1]
  const cx = 90; const cy = 90; const R = 70

  function getValues(row: LeonEvolutionRow) {
    return [
      row.evidenceCount / 10,
      row.scopeKeywords.length / 5,
      row.confidenceScore,
      row.claimsAdded.length / 5,
      row.qualityScore / 10,
      1 - row.confidenceScore
    ].map(v => Math.min(v, 1))
  }

  function toPath(values: number[]) {
    return values.map((v, i) => {
      const angle = (i / AXES.length) * 2 * Math.PI
      const pt = polarToXY(angle, v * R, cx, cy)
      return `${i === 0 ? 'M' : 'L'}${pt.x},${pt.y}`
    }).join(' ') + 'Z'
  }

  const axisLines = AXES.map((label, i) => {
    const angle = (i / AXES.length) * 2 * Math.PI
    const end = polarToXY(angle, R, cx, cy)
    const labelPt = polarToXY(angle, R + 14, cx, cy)
    return { x1: cx, y1: cy, x2: end.x, y2: end.y, labelPt, label }
  })

  return (
    <svg width={180} height={180} style={{ width: '100%' }}>
      {axisLines.map((a, i) => (
        <g key={i}>
          <line x1={a.x1} y1={a.y1} x2={a.x2} y2={a.y2} stroke="var(--border)" strokeWidth={1} />
          <text x={a.labelPt.x} y={a.labelPt.y + 4} textAnchor="middle" fontSize={8} fill="var(--text-secondary)">{a.label}</text>
        </g>
      ))}
      <path d={toPath(getValues(first))} fill="rgba(9,105,218,0.15)" stroke="var(--leon)" strokeWidth={1.5} strokeDasharray="3,2" />
      <path d={toPath(getValues(last))} fill="rgba(9,105,218,0.25)" stroke="var(--leon)" strokeWidth={2} />
    </svg>
  )
}
```

- [ ] **Step 6: Write EvolutionPanel.tsx**

```tsx
import React from 'react'
import type { LeonEvolutionRow } from '../../types/debate'
import { ScoreTimeline } from './ScoreTimeline'
import { PositionDiff } from './PositionDiff'
import { ScopeMap } from './ScopeMap'
import { EvidenceGrowth } from './EvidenceGrowth'
import { RadarChart } from './RadarChart'

interface Props { evolution: LeonEvolutionRow[] }

export function EvolutionPanel({ evolution }: Props) {
  return (
    <div style={{ flex: 1, overflowY: 'auto', padding: 12 }}>
      <section style={{ marginBottom: 16 }}>
        <h4 style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 6 }}>Score Timeline</h4>
        <ScoreTimeline evolution={evolution} />
      </section>
      <section style={{ marginBottom: 16 }}>
        <h4 style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 6 }}>Scope Growth</h4>
        <ScopeMap evolution={evolution} />
      </section>
      <section style={{ marginBottom: 16 }}>
        <h4 style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 6 }}>Evidence Growth</h4>
        <EvidenceGrowth evolution={evolution} />
      </section>
      <section style={{ marginBottom: 16 }}>
        <h4 style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 6 }}>Dimensions (R1 vs Latest)</h4>
        <RadarChart evolution={evolution} />
      </section>
      <section>
        <h4 style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 6 }}>Position Diff</h4>
        <PositionDiff evolution={evolution} />
      </section>
    </div>
  )
}
```

- [ ] **Step 7: Commit**

```
git add frontend/src/components/evolution/
git commit -m "feat: evolution panel — score timeline, scope map, evidence growth, radar, position diff"
```

---

## Task 12: Convergence Screen

**Files:**
- Create: `frontend/src/components/convergence/FinalDecision.tsx`
- Create: `frontend/src/components/convergence/AchievementGuide.tsx`
- Create: `frontend/src/components/convergence/PredictedOutcome.tsx`
- Create: `frontend/src/components/convergence/ConvergenceScreen.tsx`
- Create: `frontend/src/tests/ConvergenceScreen.test.tsx`

- [ ] **Step 1: Write the failing test**

```tsx
// frontend/src/tests/ConvergenceScreen.test.tsx
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ConvergenceScreen } from '../components/convergence/ConvergenceScreen'
import type { ConvergenceData } from '../types/debate'

const mockData: ConvergenceData = {
  qualityScore: 8.2,
  finalRecommendation: 'Adopt microservices for the data pipeline.',
  keyTradeoff: 'Complexity vs. scalability — accepted.',
  openAdvisories: ['Monitor latency after rollout'],
  achievementSteps: [{ title: 'Phase 1', description: 'Set up services', timeline: '2 weeks', owner: 'Platform team' }],
  predictedMetrics: [{ label: 'Latency', value: '50ms', confidence: 0.8 }],
  predictedNarrative: 'The migration will reduce latency by 40% within 3 months.',
  overallConfidence: 0.82
}

describe('ConvergenceScreen', () => {
  it('renders the final recommendation', () => {
    render(<ConvergenceScreen convergence={mockData} onViewDebate={vi.fn()} onNewDebate={vi.fn()} />)
    expect(screen.getByText('Adopt microservices for the data pipeline.')).toBeInTheDocument()
  })

  it('renders quality score', () => {
    render(<ConvergenceScreen convergence={mockData} onViewDebate={vi.fn()} onNewDebate={vi.fn()} />)
    expect(screen.getByText(/8\.2/)).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

```
cd frontend && npm test
```
Expected: cannot find module

- [ ] **Step 3: Write FinalDecision.tsx**

```tsx
import React from 'react'
import type { ConvergenceData } from '../../types/debate'

interface Props { convergence: ConvergenceData }

export function FinalDecision({ convergence }: Props) {
  return (
    <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <span style={{ fontSize: 22 }}>⚖️</span>
        <h2 style={{ fontSize: 20, fontWeight: 700 }}>Final Decision</h2>
        <span style={{ marginLeft: 'auto', fontWeight: 700, color: 'var(--converged)', fontSize: 18 }}>
          {convergence.qualityScore.toFixed(1)} / 10
        </span>
      </div>

      <p style={{ fontSize: 16, lineHeight: 1.7, marginBottom: 16 }}>{convergence.finalRecommendation}</p>

      <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
        <span className="chip chip-converged">Ethics ✓</span>
        <span className="chip chip-converged">Bias ✓</span>
        <span className="chip chip-converged">Evidence Tier A</span>
      </div>

      <div style={{ padding: '10px 14px', background: '#fffbeb', borderRadius: 'var(--radius)', borderLeft: '3px solid var(--advisory)', marginBottom: 12 }}>
        <strong style={{ fontSize: 13 }}>Key Trade-off Accepted:</strong>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>{convergence.keyTradeoff}</p>
      </div>

      {convergence.openAdvisories.length > 0 && (
        <div>
          <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 6 }}>Open Advisories</div>
          {convergence.openAdvisories.map((a, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, marginBottom: 4 }}>
              <span style={{ color: 'var(--advisory)' }}>⚠</span>
              <span>{a}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 4: Write AchievementGuide.tsx**

```tsx
import React from 'react'
import type { ConvergenceData } from '../../types/debate'

interface Props { convergence: ConvergenceData }

export function AchievementGuide({ convergence }: Props) {
  return (
    <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <span style={{ fontSize: 22 }}>🗺️</span>
        <h2 style={{ fontSize: 20, fontWeight: 700 }}>How to Achieve This</h2>
      </div>
      {convergence.achievementSteps.map((step, i) => (
        <div key={i} style={{ display: 'flex', gap: 14, marginBottom: 14 }}>
          <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'var(--leon)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 13, flexShrink: 0, marginTop: 2 }}>
            {i + 1}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <span style={{ fontWeight: 600, fontSize: 14 }}>{step.title}</span>
              <span className="chip" style={{ background: '#eff6ff', color: 'var(--leon)', fontSize: 11 }}>{step.timeline}</span>
              <span className="chip" style={{ background: 'var(--bg)', color: 'var(--text-secondary)', fontSize: 11 }}>{step.owner}</span>
            </div>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>{step.description}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
```

- [ ] **Step 5: Write PredictedOutcome.tsx**

```tsx
import React from 'react'
import type { ConvergenceData } from '../../types/debate'

interface Props { convergence: ConvergenceData }

export function PredictedOutcome({ convergence }: Props) {
  return (
    <div style={{ padding: '20px 24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <span style={{ fontSize: 22 }}>🔭</span>
        <h2 style={{ fontSize: 20, fontWeight: 700 }}>Best Predicted Outcome</h2>
      </div>

      <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap' }}>
        {convergence.predictedMetrics.map((m, i) => (
          <div key={i} style={{ padding: '12px 16px', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', minWidth: 120, textAlign: 'center' }}>
            <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--leon)' }}>{m.value}</div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 4 }}>{m.label}</div>
            <div style={{ fontSize: 11, color: 'var(--converged)' }}>{Math.round(m.confidence * 100)}% confidence</div>
          </div>
        ))}
      </div>

      <p style={{ fontSize: 14, lineHeight: 1.7, marginBottom: 16 }}>{convergence.predictedNarrative}</p>

      <div style={{ padding: '10px 14px', background: 'var(--bg)', borderRadius: 'var(--radius)', fontSize: 13, color: 'var(--text-secondary)' }}>
        Overall prediction confidence: <strong style={{ color: 'var(--text)' }}>{Math.round(convergence.overallConfidence * 100)}%</strong>
      </div>
    </div>
  )
}
```

- [ ] **Step 6: Write ConvergenceScreen.tsx**

```tsx
import React from 'react'
import type { ConvergenceData } from '../../types/debate'
import { FinalDecision } from './FinalDecision'
import { AchievementGuide } from './AchievementGuide'
import { PredictedOutcome } from './PredictedOutcome'

interface Props {
  convergence: ConvergenceData
  onViewDebate: () => void
  onNewDebate: () => void
}

export function ConvergenceScreen({ convergence, onViewDebate, onNewDebate }: Props) {
  const exportDecision = () => {
    const content = `# Decision Log\n\n**Date:** ${new Date().toISOString()}\n\n## Final Decision\n${convergence.finalRecommendation}\n\n## Key Trade-off\n${convergence.keyTradeoff}\n\n## Achievement Steps\n${convergence.achievementSteps.map((s, i) => `${i + 1}. **${s.title}** (${s.timeline}, ${s.owner}): ${s.description}`).join('\n')}\n\n## Predicted Outcomes\n${convergence.predictedMetrics.map(m => `- ${m.label}: ${m.value} (${Math.round(m.confidence * 100)}% confidence)`).join('\n')}\n\n${convergence.predictedNarrative}\n`
    const blob = new Blob([content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'decision-log.md'; a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div style={{ height: '100%', overflowY: 'auto' }}>
      <div style={{ background: 'linear-gradient(135deg, #dcfce7, #eff6ff)', padding: '16px 24px', borderBottom: '1px solid var(--border)', display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 24 }}>✅</span>
        <div>
          <div style={{ fontWeight: 700, fontSize: 16, color: 'var(--converged)' }}>Analysis Converged</div>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>LEON and SOPHIA reached consensus — quality score {convergence.qualityScore.toFixed(1)}/10</div>
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
          <button onClick={exportDecision} style={{ padding: '8px 14px', borderRadius: 'var(--radius)', background: 'var(--converged)', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: 13 }}>
            Export Decision
          </button>
          <button onClick={onViewDebate} style={{ padding: '8px 14px', borderRadius: 'var(--radius)', background: 'var(--surface)', border: '1px solid var(--border)', cursor: 'pointer', fontSize: 13 }}>
            View Full Debate
          </button>
          <button onClick={onNewDebate} style={{ padding: '8px 14px', borderRadius: 'var(--radius)', background: 'var(--bg)', border: '1px solid var(--border)', cursor: 'pointer', fontSize: 13 }}>
            New Debate
          </button>
        </div>
      </div>

      <div style={{ maxWidth: 860, margin: '0 auto' }}>
        <FinalDecision convergence={convergence} />
        <AchievementGuide convergence={convergence} />
        <PredictedOutcome convergence={convergence} />
      </div>
    </div>
  )
}
```

- [ ] **Step 7: Run tests to verify they pass**

```
cd frontend && npm test
```
Expected: all PASSED

- [ ] **Step 8: Commit**

```
git add frontend/src/components/convergence/ frontend/src/tests/ConvergenceScreen.test.tsx
git commit -m "feat: convergence screen — FinalDecision, AchievementGuide, PredictedOutcome"
```

---

## Task 13: PWA Config + End-to-End Smoke Test

**Files:**
- Create: `frontend/public/manifest.json`
- Create: `frontend/public/icon-512.svg`
- Create: `frontend/src/components/ServiceWorkerRegister.tsx`

- [ ] **Step 1: Write frontend/public/manifest.json**

```json
{
  "name": "LEON · SOPHIA",
  "short_name": "LEON·SOPHIA",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#f6f8fa",
  "theme_color": "#0969da",
  "icons": [
    {
      "src": "/icon-512.svg",
      "sizes": "512x512",
      "type": "image/svg+xml",
      "purpose": "any maskable"
    }
  ]
}
```

- [ ] **Step 2: Write frontend/public/icon-512.svg**

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="80" fill="#0969da"/>
  <text x="256" y="220" text-anchor="middle" font-family="'Segoe UI',sans-serif" font-size="140" font-weight="bold" fill="white">L·S</text>
  <text x="256" y="340" text-anchor="middle" font-family="'Segoe UI',sans-serif" font-size="60" fill="rgba(255,255,255,0.7)">debate</text>
</svg>
```

- [ ] **Step 3: Write ServiceWorkerRegister.tsx** (used by vite-plugin-pwa's auto-update)

```tsx
import { useEffect } from 'react'

export function ServiceWorkerRegister() {
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').catch(() => {})
      })
    }
  }, [])
  return null
}
```

- [ ] **Step 4: Full end-to-end smoke test**

Run backend:
```
cd backend
export ANTHROPIC_API_KEY=<your-key>
uvicorn main:app --reload --port 8000
```

Run frontend:
```
cd frontend
npm run dev
```

Open `http://localhost:5173` in browser. Verify:
- [ ] Page loads with TopBar "LEON · SOPHIA" + "Ready" status
- [ ] Input bar is visible and enabled
- [ ] Type a topic, click "Start Debate"
- [ ] TopBar shows "Debating..."
- [ ] Timeline sidebar shows rounds appearing (R1 LEON, R1 SOPHIA, R2 LEON...)
- [ ] Clicking a round shows streaming text in DetailPanel with blinking cursor
- [ ] Flags appear with BLOCKING / ADVISORY chips
- [ ] Score bar updates after each SOPHIA round
- [ ] Evolution tab shows score timeline, scope map, evidence growth
- [ ] When SOPHIA converges: green banner appears, ConvergenceScreen renders
- [ ] Export Decision downloads a .md file

- [ ] **Step 5: Test Android PWA install**

On Android device (same network):
```
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000
cd frontend && npm run build && npx vite preview --host 0.0.0.0 --port 5173
```
Open Chrome → navigate to `http://<your-machine-ip>:5173` → ⋮ → "Add to Home Screen" → confirm install → open from home screen → confirm standalone mode (no browser chrome)

- [ ] **Step 6: Build for production**

```
cd frontend && npm run build
```
Expected: `dist/` folder created, no TypeScript errors, no build errors

- [ ] **Step 7: Final commit**

```
git add frontend/public/ frontend/src/components/ServiceWorkerRegister.tsx
git commit -m "feat: PWA config — manifest, icon, service worker — LEON-SOPHIA app complete"
```

---

## Implementation Checklist

- [ ] Task 1: Backend scaffolding
- [ ] Task 2: Data models
- [ ] Task 3: LEON agent
- [ ] Task 4: SOPHIA agent
- [ ] Task 5: Orchestrator
- [ ] Task 6: FastAPI routes + SSE
- [ ] Task 7: Frontend scaffolding + types
- [ ] Task 8: useDebate + useEvolution hooks
- [ ] Task 9: App shell
- [ ] Task 10: TimelineSidebar + DetailPanel
- [ ] Task 11: Evolution panel
- [ ] Task 12: Convergence screen
- [ ] Task 13: PWA config + smoke test
