import os
import json
from dataclasses import dataclass, field
from typing import AsyncGenerator
import anthropic

SOPHIA_MODEL = "claude-sonnet-4-6"

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
        self._client = anthropic.AsyncAnthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY", "test"))

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
        active_tool: str | None = None

        async with self._client.messages.stream(
            model=SOPHIA_MODEL,
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
                        try:
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
                        except (json.JSONDecodeError, KeyError):
                            pass
                        active_tool = None
                        tool_json_buffer = ""
