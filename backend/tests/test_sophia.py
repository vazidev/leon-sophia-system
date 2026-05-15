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
