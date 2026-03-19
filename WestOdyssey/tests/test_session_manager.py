"""
会话管理器测试
"""
import sys
import tempfile
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# 用临时目录避免污染真实数据
_tmp = tempfile.mkdtemp()
os.environ["SESSION_DATA_DIR"] = _tmp

from core.session_manager import SessionManager, generate_session_key


def test_generate_session_key():
    key = generate_session_key("literature", "user1")
    assert "literature" in key
    assert "user1" in key
    assert key.startswith("agent:literature:")


def test_create_and_get_session():
    sm = SessionManager(user_id="test_user")
    session_id = sm.create_session("literature", "测试会话")
    assert session_id is not None

    session = sm.get_or_create_active_session("literature")
    assert session["session_id"] == session_id
    assert session["title"] == "测试会话"


def test_add_and_get_messages():
    sm = SessionManager(user_id="test_msg")
    sm.create_session("data")
    sm.add_message("data", "user", "你好")
    sm.add_message("data", "assistant", "你好！有什么可以帮你的？",
                   agent_name="数据工程师", agent_emoji="📊")

    messages = sm.get_messages("data")
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["agent_name"] == "数据工程师"


def test_list_sessions():
    sm = SessionManager(user_id="test_list")
    sm.create_session("experiment", "实验1")
    sm.create_session("experiment", "实验2")

    sessions = sm.list_sessions("experiment")
    assert len(sessions) == 2


def test_switch_session():
    sm = SessionManager(user_id="test_switch")
    s1 = sm.create_session("writer", "草稿1")
    s2 = sm.create_session("writer", "草稿2")

    assert sm.get_or_create_active_session("writer")["session_id"] == s2
    sm.switch_session("writer", s1)
    assert sm.get_or_create_active_session("writer")["session_id"] == s1


def test_clear_session():
    sm = SessionManager(user_id="test_clear")
    sm.create_session("reviewer")
    sm.add_message("reviewer", "user", "test message")
    assert len(sm.get_messages("reviewer")) == 1

    sm.clear_current_session("reviewer")
    assert len(sm.get_messages("reviewer")) == 0


if __name__ == "__main__":
    test_generate_session_key()
    test_create_and_get_session()
    test_add_and_get_messages()
    test_list_sessions()
    test_switch_session()
    test_clear_session()
    print("✅ All session_manager tests passed!")
