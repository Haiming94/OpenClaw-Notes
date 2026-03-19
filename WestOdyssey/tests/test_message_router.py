"""
消息路由器测试
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.message_router import parse_message, resolve_agent, list_agents


def test_resolve_agent_by_id():
    assert resolve_agent("literature") == "literature"
    assert resolve_agent("data") == "data"
    assert resolve_agent("experiment") == "experiment"
    assert resolve_agent("writer") == "writer"
    assert resolve_agent("reviewer") == "reviewer"


def test_resolve_agent_by_chinese():
    assert resolve_agent("文献") == "literature"
    assert resolve_agent("数据") == "data"
    assert resolve_agent("实验") == "experiment"
    assert resolve_agent("写作") == "writer"
    assert resolve_agent("审稿") == "reviewer"


def test_resolve_agent_by_alias():
    assert resolve_agent("lit") == "literature"
    assert resolve_agent("dat") == "data"
    assert resolve_agent("exp") == "experiment"
    assert resolve_agent("wrt") == "writer"
    assert resolve_agent("rev") == "reviewer"


def test_resolve_agent_unknown():
    assert resolve_agent("unknown_agent") is None


def test_parse_message_with_mention():
    text, agent = parse_message("@文献 帮我查一下 transformer 论文", "data")
    assert agent == "literature"
    assert "transformer" in text


def test_parse_message_with_english_mention():
    text, agent = parse_message("@data 分析一下这个数据集", "literature")
    assert agent == "data"
    assert "数据集" in text


def test_parse_message_no_mention():
    text, agent = parse_message("帮我分析一下这个问题", "experiment")
    assert agent == "experiment"
    assert text == "帮我分析一下这个问题"


def test_list_agents():
    agents = list_agents()
    assert len(agents) == 5
    ids = [a["id"] for a in agents]
    assert "literature" in ids
    assert "reviewer" in ids


if __name__ == "__main__":
    test_resolve_agent_by_id()
    test_resolve_agent_by_chinese()
    test_resolve_agent_by_alias()
    test_resolve_agent_unknown()
    test_parse_message_with_mention()
    test_parse_message_with_english_mention()
    test_parse_message_no_mention()
    test_list_agents()
    print("✅ All message_router tests passed!")
