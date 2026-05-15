import pytest
import json
from unittest.mock import MagicMock, patch
from agents.sophia import SophiaAgent, SophiaFlagChunk, SophiaReviewChunk, SophiaTextChunk

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

    review_json = json.dumps(review_input)
    mid = len(review_json) // 2

    # Simulate: text token, then tool JSON split across two deltas, then stop
    # Use content_block_start to signal which tool is active
    # NOTE: MagicMock(name=...) sets the mock's display name, NOT the .name attribute.
    # Use configure_mock or direct assignment to set .name as a real string attribute.
    content_block_mock = MagicMock()
    content_block_mock.type = "tool_use"
    content_block_mock.name = "submit_review"
    fake_events = [
        MagicMock(type="content_block_delta",
                  delta=MagicMock(type="text_delta", text="Needs work.")),
        MagicMock(type="content_block_start",
                  content_block=content_block_mock),
        MagicMock(type="content_block_delta",
                  delta=MagicMock(type="input_json_delta", partial_json=review_json[:mid])),
        MagicMock(type="content_block_delta",
                  delta=MagicMock(type="input_json_delta", partial_json=review_json[mid:])),
        MagicMock(type="content_block_stop"),
        MagicMock(type="message_stop"),
    ]

    class AsyncContextManagerMock:
        def __init__(self, events):
            self._events = events
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        def __aiter__(self):
            return self._iter()
        async def _iter(self):
            for evt in self._events:
                yield evt

    with patch.object(agent._client.messages, "stream",
                      return_value=AsyncContextManagerMock(fake_events)):
        chunks = [c async for c in agent.stream_review("test topic", [], "LEON rec")]

    text_chunks = [c for c in chunks if isinstance(c, SophiaTextChunk)]
    flag_chunks = [c for c in chunks if isinstance(c, SophiaFlagChunk)]
    review_chunks = [c for c in chunks if isinstance(c, SophiaReviewChunk)]

    assert len(text_chunks) == 1
    assert text_chunks[0].text == "Needs work."
    assert len(flag_chunks) == 1
    assert flag_chunks[0].severity == "blocking"
    assert flag_chunks[0].claim == "microservices claim"
    assert len(review_chunks) == 1
    assert review_chunks[0].quality_score == 5.5
    assert review_chunks[0].is_blocking is True


@pytest.mark.asyncio
async def test_sophia_convergence_emits_convergence_chunk():
    from agents.sophia import SophiaAgent, SophiaConvergenceChunk, SophiaTextChunk
    agent = SophiaAgent(api_key="test")

    convergence_input = {
        "quality_score": 8.5,
        "final_recommendation": "Adopt microservices.",
        "key_tradeoff": "Complexity vs scalability.",
        "open_advisories": ["Monitor latency"],
        "achievement_steps": [
            {"title": "Phase 1", "description": "Set up", "timeline": "2w", "owner": "team"}
        ],
        "predicted_metrics": [
            {"label": "Latency", "value": "50ms", "confidence": 0.8}
        ],
        "predicted_narrative": "Migration completes in 3 months.",
        "overall_confidence": 0.85
    }

    conv_json = json.dumps(convergence_input)
    mid = len(conv_json) // 2

    content_block_mock = MagicMock()
    content_block_mock.type = "tool_use"
    content_block_mock.name = "submit_convergence"

    fake_events = [
        MagicMock(type="content_block_delta",
                  delta=MagicMock(type="text_delta", text="Converging.")),
        MagicMock(type="content_block_start",
                  content_block=content_block_mock),
        MagicMock(type="content_block_delta",
                  delta=MagicMock(type="input_json_delta", partial_json=conv_json[:mid])),
        MagicMock(type="content_block_delta",
                  delta=MagicMock(type="input_json_delta", partial_json=conv_json[mid:])),
        MagicMock(type="content_block_stop"),
        MagicMock(type="message_stop"),
    ]

    class AsyncContextManagerMock:
        def __init__(self, events):
            self._events = events
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            pass
        def __aiter__(self):
            return self._iter()
        async def _iter(self):
            for evt in self._events:
                yield evt

    with patch.object(agent._client.messages, "stream",
                      return_value=AsyncContextManagerMock(fake_events)):
        chunks = [c async for c in agent.stream_review("test topic", [], "LEON rec")]

    text_chunks = [c for c in chunks if isinstance(c, SophiaTextChunk)]
    conv_chunks = [c for c in chunks if isinstance(c, SophiaConvergenceChunk)]

    assert len(text_chunks) == 1
    assert len(conv_chunks) == 1
    assert conv_chunks[0].quality_score == 8.5
    assert conv_chunks[0].final_recommendation == "Adopt microservices."
    assert len(conv_chunks[0].achievement_steps) == 1
    assert len(conv_chunks[0].predicted_metrics) == 1
