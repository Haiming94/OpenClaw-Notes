"""
Agent 基类测试 (不依赖 Gateway 连接)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.base import AgentBase, get_agent
from core.config import AGENT_DEFINITIONS


def test_agent_init():
    for agent_id in AGENT_DEFINITIONS:
        agent = AgentBase(agent_id)
        assert agent.agent_id == agent_id
        assert agent.name
        assert agent.emoji
        assert agent.color


def test_agent_headers():
    agent = AgentBase("literature")
    headers = agent._build_headers("test-session-key")
    assert headers["X-OpenClaw-Agent-Id"] == "literature"
    assert headers["X-OpenClaw-Session-Key"] == "test-session-key"
    assert headers["X-OpenClaw-Message-Channel"] == "webchat"


def test_agent_payload():
    agent = AgentBase("data")
    payload = agent._build_payload("分析数据", stream=True)
    assert payload["model"] == "openclaw/data"
    assert payload["stream"] is True
    assert len(payload["messages"]) == 1
    assert payload["messages"][0]["role"] == "user"
    assert payload["messages"][0]["content"] == "分析数据"


def test_agent_payload_with_history():
    agent = AgentBase("experiment")
    history = [
        {"role": "user", "content": "设计实验"},
        {"role": "assistant", "content": "好的，我来帮你设计"},
    ]
    payload = agent._build_payload("继续", history=history, stream=False)
    assert payload["stream"] is False
    # history(2) + current(1) = 3
    assert len(payload["messages"]) == 3


def test_agent_cache():
    a1 = get_agent("writer")
    a2 = get_agent("writer")
    assert a1 is a2  # 同一实例


def test_invalid_agent():
    try:
        AgentBase("nonexistent")
        assert False, "应该抛出 ValueError"
    except ValueError:
        pass


if __name__ == "__main__":
    test_agent_init()
    test_agent_headers()
    test_agent_payload()
    test_agent_payload_with_history()
    test_agent_cache()
    test_invalid_agent()
    print("✅ All agent_base tests passed!")
