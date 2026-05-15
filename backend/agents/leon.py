import os
import json
from dataclasses import dataclass
from typing import AsyncGenerator
import anthropic

LEON_MODEL = "claude-sonnet-4-6"

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
        self._client = anthropic.AsyncAnthropic(
            api_key=api_key or os.environ["ANTHROPIC_API_KEY"]
        )

    async def stream_response(
        self,
        topic: str,
        history: list[dict],
        sophia_flags: list[str],
    ) -> AsyncGenerator[LeonTextChunk | LeonChunk, None]:
        messages = list(history)
        flag_context = ""
        if sophia_flags:
            flag_context = "\n\nSOPHIA's blocking flags you must address:\n" + "\n".join(
                f"- {f}" for f in sophia_flags
            )

        messages.append({
            "role": "user",
            "content": f"Topic: {topic}{flag_context}\n\nProvide your analysis."
        })

        tool_json_buffer = ""
        collecting_tool = False

        async with self._client.messages.stream(
            model=LEON_MODEL,
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
                    if collecting_tool and tool_json_buffer:
                        try:
                            data = json.loads(tool_json_buffer)
                            yield LeonChunk(
                                recommendation=data["recommendation"],
                                evidence=data["evidence"],
                                new_claims=data["new_claims"],
                                resolved_flags=data["resolved_flags"],
                                scope_keywords=data["scope_keywords"],
                                confidence_score=data["confidence_score"],
                            )
                        except (json.JSONDecodeError, KeyError):
                            pass  # Tool output malformed — no LeonChunk emitted
