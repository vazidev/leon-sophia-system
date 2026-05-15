import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from sqlmodel import Field, SQLModel, Column, Text


class AgentType(str, Enum):
    LEON = "leon"
    SOPHIA = "sophia"


class DebateSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True, unique=True)
    topic: str
    status: str = "active"  # active | converged
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class DebateRound(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    round: int
    agent: AgentType
    content: str = Field(sa_column=Column(Text))


class LeonEvolution(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    round: int
    recommendation_snapshot: str = Field(sa_column=Column(Text))
    evidence_count: int
    claims_added_json: str = Field(default="[]", sa_column=Column("claims_added_json", Text))
    claims_resolved_json: str = Field(default="[]", sa_column=Column("claims_resolved_json", Text))
    scope_keywords_json: str = Field(default="[]", sa_column=Column("scope_keywords_json", Text))
    confidence_score: float
    quality_score: float

    def __init__(self, **data: Any):
        # Accept list values for the three list fields and serialize to JSON
        for field_name in ("claims_added", "claims_resolved", "scope_keywords"):
            if field_name in data:
                value = data.pop(field_name)
                if not isinstance(value, list):
                    raise TypeError(
                        f"{field_name} must be a list, got {type(value).__name__}"
                    )
                data[f"{field_name}_json"] = json.dumps(value)
        super().__init__(**data)

    @property
    def claims_added(self) -> list[str]:
        # Mutating the returned list has no effect — use the setter to update
        return json.loads(self.claims_added_json or "[]")

    @claims_added.setter
    def claims_added(self, v: list) -> None:
        self.claims_added_json = json.dumps(v)

    @property
    def claims_resolved(self) -> list[str]:
        # Mutating the returned list has no effect — use the setter to update
        return json.loads(self.claims_resolved_json or "[]")

    @claims_resolved.setter
    def claims_resolved(self, v: list) -> None:
        self.claims_resolved_json = json.dumps(v)

    @property
    def scope_keywords(self) -> list[str]:
        # Mutating the returned list has no effect — use the setter to update
        return json.loads(self.scope_keywords_json or "[]")

    @scope_keywords.setter
    def scope_keywords(self, v: list) -> None:
        self.scope_keywords_json = json.dumps(v)
