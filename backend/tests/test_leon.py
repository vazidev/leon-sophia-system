import pytest
import json
from unittest.mock import MagicMock, patch
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

    tool_json_str = json.dumps(tool_input)
    mid = len(tool_json_str) // 2

    fake_events = [
        MagicMock(type="content_block_delta",
                  delta=MagicMock(type="text_delta", text="Use micro")),
        MagicMock(type="content_block_delta",
                  delta=MagicMock(type="text_delta", text="services")),
        MagicMock(type="content_block_delta",
                  delta=MagicMock(type="input_json_delta",
                                  partial_json=tool_json_str[:mid])),
        MagicMock(type="content_block_delta",
                  delta=MagicMock(type="input_json_delta",
                                  partial_json=tool_json_str[mid:])),
        MagicMock(type="message_stop"),
    ]

    class AsyncContextManagerMock:
        """Mock that supports 'async with ... as stream: async for event in stream:'"""
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        def __aiter__(self):
            return self._async_gen()

        async def _async_gen(self):
            for evt in fake_events:
                yield evt

    def mock_stream(*args, **kwargs):
        return AsyncContextManagerMock()

    with patch.object(agent._client.messages, "stream", new=mock_stream):
        chunks = [c async for c in agent.stream_response("test topic", [], [])]

    text_chunks = [c for c in chunks if isinstance(c, LeonTextChunk)]
    meta_chunks = [c for c in chunks if isinstance(c, LeonChunk)]
    assert len(text_chunks) == 2
    assert text_chunks[0].text == "Use micro"
    assert len(meta_chunks) == 1
    assert meta_chunks[0].recommendation == "Use microservices"
    assert meta_chunks[0].confidence_score == 0.75
