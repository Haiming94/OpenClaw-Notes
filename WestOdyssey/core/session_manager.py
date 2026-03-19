"""
会话管理器
负责 session key 生成、会话历史的本地持久化
"""
import json
import uuid
import time
from pathlib import Path
from typing import Optional
from core.config import SESSION_DATA_DIR


def generate_session_key(agent_id: str, user_id: str = "default") -> str:
    """
    生成 OpenClaw 的 session key
    格式: agent:<agent_id>:main:webchat-user:<user_id>:<session_uuid>
    """
    session_uuid = uuid.uuid4().hex[:12]
    return f"agent:{agent_id}:main:webchat-user:{user_id}:{session_uuid}"


class SessionManager:
    """管理多个 Agent 的会话"""

    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self._sessions: dict = {}  # {agent_id: {session_id: SessionData}}
        self._active_sessions: dict = {}  # {agent_id: active_session_id}
        self._storage_dir = SESSION_DATA_DIR / user_id
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._load_index()

    def _index_path(self) -> Path:
        return self._storage_dir / "index.json"

    def _session_path(self, agent_id: str, session_id: str) -> Path:
        return self._storage_dir / f"{agent_id}_{session_id}.json"

    def _load_index(self):
        """从磁盘加载会话索引"""
        idx_path = self._index_path()
        if idx_path.exists():
            try:
                data = json.loads(idx_path.read_text(encoding="utf-8"))
                self._active_sessions = data.get("active_sessions", {})
                self._sessions = data.get("sessions", {})
            except (json.JSONDecodeError, KeyError):
                self._active_sessions = {}
                self._sessions = {}
        else:
            self._active_sessions = {}
            self._sessions = {}

    def _save_index(self):
        """保存会话索引到磁盘"""
        data = {
            "active_sessions": self._active_sessions,
            "sessions": self._sessions,
        }
        self._index_path().write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def create_session(self, agent_id: str, title: Optional[str] = None) -> str:
        """
        创建一个新的会话，返回 session_id
        """
        session_id = uuid.uuid4().hex[:12]
        session_key = generate_session_key(agent_id, self.user_id)

        if agent_id not in self._sessions:
            self._sessions[agent_id] = {}

        self._sessions[agent_id][session_id] = {
            "session_id": session_id,
            "session_key": session_key,
            "agent_id": agent_id,
            "title": title or f"新会话 {len(self._sessions[agent_id]) + 1}",
            "created_at": time.time(),
            "updated_at": time.time(),
            "message_count": 0,
        }
        self._active_sessions[agent_id] = session_id

        # 初始化空消息文件
        self._save_messages(agent_id, session_id, [])
        self._save_index()
        return session_id

    def get_or_create_active_session(self, agent_id: str) -> dict:
        """获取当前活跃会话，如果没有则创建"""
        active_id = self._active_sessions.get(agent_id)
        if active_id and agent_id in self._sessions and active_id in self._sessions[agent_id]:
            return self._sessions[agent_id][active_id]

        session_id = self.create_session(agent_id)
        return self._sessions[agent_id][session_id]

    def switch_session(self, agent_id: str, session_id: str) -> bool:
        """切换活跃会话"""
        if agent_id in self._sessions and session_id in self._sessions[agent_id]:
            self._active_sessions[agent_id] = session_id
            self._save_index()
            return True
        return False

    def list_sessions(self, agent_id: str) -> list:
        """列出某个 Agent 的所有会话"""
        if agent_id not in self._sessions:
            return []
        sessions = list(self._sessions[agent_id].values())
        sessions.sort(key=lambda s: s.get("updated_at", 0), reverse=True)
        return sessions

    def get_session_key(self, agent_id: str) -> str:
        """获取当前活跃会话的 session_key"""
        session = self.get_or_create_active_session(agent_id)
        return session["session_key"]

    def _save_messages(self, agent_id: str, session_id: str, messages: list):
        """保存消息到磁盘"""
        path = self._session_path(agent_id, session_id)
        path.write_text(json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8")

    def _load_messages(self, agent_id: str, session_id: str) -> list:
        """从磁盘加载消息"""
        path = self._session_path(agent_id, session_id)
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return []
        return []

    def add_message(self, agent_id: str, role: str, content: str,
                    agent_name: str = "", agent_emoji: str = ""):
        """添加一条消息到当前活跃会话"""
        session = self.get_or_create_active_session(agent_id)
        session_id = session["session_id"]

        messages = self._load_messages(agent_id, session_id)
        messages.append({
            "role": role,
            "content": content,
            "agent_id": agent_id if role == "assistant" else None,
            "agent_name": agent_name if role == "assistant" else None,
            "agent_emoji": agent_emoji if role == "assistant" else None,
            "timestamp": time.time(),
        })
        self._save_messages(agent_id, session_id, messages)

        # 更新索引元数据
        session["message_count"] = len(messages)
        session["updated_at"] = time.time()
        # 用第一条用户消息作为标题
        if role == "user" and session.get("title", "").startswith("新会话"):
            session["title"] = content[:30] + ("..." if len(content) > 30 else "")
        self._save_index()

    def get_messages(self, agent_id: str) -> list:
        """获取当前活跃会话的所有消息"""
        session = self.get_or_create_active_session(agent_id)
        return self._load_messages(agent_id, session["session_id"])

    def clear_current_session(self, agent_id: str):
        """清空当前会话的消息"""
        session = self.get_or_create_active_session(agent_id)
        session_id = session["session_id"]
        self._save_messages(agent_id, session_id, [])
        session["message_count"] = 0
        session["updated_at"] = time.time()
        self._save_index()
