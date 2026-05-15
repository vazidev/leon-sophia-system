import json
from typing import Any, Optional
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
                data[f"{field_name}_json"] = json.dumps(value) if isinstance(value, list) else value
        super().__init__(**data)

    @property
    def claims_added(self) -> list:
        return json.loads(self.claims_added_json)

    @claims_added.setter
    def claims_added(self, v: list) -> None:
        self.claims_added_json = json.dumps(v)

    @property
    def claims_resolved(self) -> list:
        return json.loads(self.claims_resolved_json)

    @claims_resolved.setter
    def claims_resolved(self, v: list) -> None:
        self.claims_resolved_json = json.dumps(v)

    @property
    def scope_keywords(self) -> list:
        return json.loads(self.scope_keywords_json)

    @scope_keywords.setter
    def scope_keywords(self, v: list) -> None:
        self.scope_keywords_json = json.dumps(v)
