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
