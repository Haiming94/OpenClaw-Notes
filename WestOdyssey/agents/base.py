# -*- coding: utf-8 -*-
import logging
from typing import Generator, Optional
import requests

from core.config import get_agent_api_url, AUTH_TOKEN, AGENT_DEFINITIONS
from core.stream_handler import parse_sse_stream, parse_non_stream_response

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = (10, 120)
STREAM_TIMEOUT = (10, 300)

SYSTEM_PROMPTS: dict = {}

def _load_system_prompts():
    if SYSTEM_PROMPTS:
        return
    from agents.sanzang import SANZANG_SYSTEM_PROMPT
    from agents.wukong import WUKONG_SYSTEM_PROMPT
    from agents.wuneng import WUNENG_SYSTEM_PROMPT
    from agents.wujing import WUJING_SYSTEM_PROMPT
    from agents.horse import HORSE_SYSTEM_PROMPT
    from agents.coordinator import COORDINATOR_SYSTEM_PROMPT
    SYSTEM_PROMPTS.update({
        "sanzang": SANZANG_SYSTEM_PROMPT,
        "wukong": WUKONG_SYSTEM_PROMPT,
        "wuneng": WUNENG_SYSTEM_PROMPT,
        "wujing": WUJING_SYSTEM_PROMPT,
        "horse": HORSE_SYSTEM_PROMPT,
        "coordinator": COORDINATOR_SYSTEM_PROMPT,
    })


class AgentBase:
    def __init__(self, agent_id: str):
        if agent_id not in AGENT_DEFINITIONS:
            raise ValueError(f"\u672a\u77e5\u7684 Agent: {agent_id}")
        _load_system_prompts()
        self.agent_id = agent_id
        self._def = AGENT_DEFINITIONS[agent_id]
        self.name = self._def["name"]
        self.emoji = self._def["emoji"]
        self.color = self._def["color"]
        self.description = self._def["description"]
        self.system_prompt = SYSTEM_PROMPTS.get(agent_id, "")

    def _build_headers(self, session_key: str) -> dict:
        headers = {"Content-Type": "application/json"}
        if AUTH_TOKEN:
            headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
        headers["X-OpenClaw-Agent-Id"] = self.agent_id
        headers["X-OpenClaw-Session-Key"] = session_key
        return headers

    def _build_payload(self, message: str, history: Optional[list] = None, stream: bool = True) -> dict:
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        if history:
            recent = history[-40:]
            for msg in recent:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": message})
        return {
            "model": f"openclaw:{self.agent_id}",
            "messages": messages,
            "stream": stream,
        }

    def chat(self, message: str, session_key: str, history: Optional[list] = None) -> str:
        url = get_agent_api_url()
        headers = self._build_headers(session_key)
        payload = self._build_payload(message, history, stream=False)
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=DEFAULT_TIMEOUT)
            resp.raise_for_status()
            content = parse_non_stream_response(resp)
            return content or "(\u65e0\u54cd\u5e94)"
        except requests.exceptions.ConnectionError:
            return "\u274c \u65e0\u6cd5\u8fde\u63a5\u5230 OpenClaw Gateway"
        except requests.exceptions.Timeout:
            return "\u274c \u8bf7\u6c42\u8d85\u65f6"
        except requests.exceptions.HTTPError as e:
            logger.error(f"API error: {e}")
            return f"\u274c API \u9519\u8bef: {e.response.status_code} - {e.response.text[:200]}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return f"\u274c \u9519\u8bef: {str(e)}"

    def chat_stream(self, message: str, session_key: str,
                    history: Optional[list] = None) -> Generator[str, None, None]:
        url = get_agent_api_url()
        headers = self._build_headers(session_key)
        payload = self._build_payload(message, history, stream=True)
        try:
            resp = requests.post(
                url, json=payload, headers=headers,
                stream=True, timeout=STREAM_TIMEOUT
            )
            resp.raise_for_status()
            yield from parse_sse_stream(resp)
        except requests.exceptions.ConnectionError:
            yield "\u274c \u65e0\u6cd5\u8fde\u63a5\u5230 OpenClaw Gateway"
        except requests.exceptions.Timeout:
            yield "\u274c \u8bf7\u6c42\u8d85\u65f6"
        except requests.exceptions.HTTPError as e:
            logger.error(f"Stream API error: {e}")
            yield f"\u274c API \u9519\u8bef: {e.response.status_code}"
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"\u274c \u9519\u8bef: {str(e)}"


_agent_cache: dict[str, AgentBase] = {}


def get_agent(agent_id: str) -> AgentBase:
    if agent_id not in _agent_cache:
        _agent_cache[agent_id] = AgentBase(agent_id)
    return _agent_cache[agent_id]
