# -*- coding: utf-8 -*-
import os
from pathlib import Path
from collections import OrderedDict
from dotenv import load_dotenv

_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / ".env")

GATEWAY_URL: str = os.getenv("OPENCLAW_GATEWAY_URL", "http://localhost:18789")
AUTH_TOKEN: str = os.getenv("OPENCLAW_AUTH_TOKEN", "")
CHAT_COMPLETIONS_PATH: str = "/v1/chat/completions"
SESSION_DATA_DIR: Path = Path(os.getenv("SESSION_DATA_DIR", str(_project_root / "data" / "sessions")))
SESSION_DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

RESEARCH_AGENTS: dict = OrderedDict([
    ("sanzang", {
        "id": "sanzang",
        "name": "\u5510\u50e7",
        "emoji": "\U0001f9d8",
        "color": "#FFD700",
        "description": "\u79d1\u7814\u6218\u7565\u4e0e\u65b9\u5411\u89c4\u5212\uff0c\u5b9a\u4e49\u7814\u7a76\u95ee\u9898\u3001\u5236\u5b9a\u8ba1\u5212\u3001\u534f\u8c03\u4f18\u5148\u7ea7",
        "aliases": ["\u5510\u50e7", "sanzang", "\u89c4\u5212", "\u6218\u7565"],
    }),
    ("wukong", {
        "id": "wukong",
        "name": "\u5b59\u609f\u7a7a",
        "emoji": "\U0001f4bb",
        "color": "#FF6B6B",
        "description": "\u7b97\u6cd5\u5f00\u53d1\u4e0e\u7f16\u7a0b\u5b9e\u73b0\uff0c\u7f16\u5199\u8c03\u8bd5\u4ee3\u7801\u3001\u6784\u5efa\u5b9e\u9a8c pipeline\u3001\u8bad\u7ec3\u6a21\u578b",
        "aliases": ["\u5b59\u609f\u7a7a", "\u609f\u7a7a", "wukong", "\u7f16\u7a0b", "\u4ee3\u7801"],
    }),
    ("wuneng", {
        "id": "wuneng",
        "name": "\u732a\u516b\u6212",
        "emoji": "\u270d\ufe0f",
        "color": "#FFA62B",
        "description": "\u5b66\u672f\u5199\u4f5c\u4e0e\u9879\u76ee\u7533\u62a5\uff0c\u64b0\u5199\u8bba\u6587\u3001\u6da6\u8272\u8bed\u8a00\u3001\u64b0\u5199\u57fa\u91d1\u7533\u8bf7\u4e66",
        "aliases": ["\u732a\u516b\u6212", "\u516b\u6212", "wuneng", "\u5199\u4f5c", "\u8bba\u6587"],
    }),
    ("wujing", {
        "id": "wujing",
        "name": "\u6c99\u50e7",
        "emoji": "\U0001f4da",
        "color": "#6C63FF",
        "description": "\u6587\u732e\u7ba1\u7406\u4e0e\u77e5\u8bc6\u6574\u5408\uff0c\u7cfb\u7edf\u6027\u68c0\u7d22\u6587\u732e\u3001\u6784\u5efa\u77e5\u8bc6\u5e93\u3001\u751f\u6210\u7efc\u8ff0",
        "aliases": ["\u6c99\u50e7", "wujing", "\u6587\u732e", "\u7efc\u8ff0"],
    }),
    ("horse", {
        "id": "horse",
        "name": "\u767d\u9f99\u9a6c",
        "emoji": "\u2699\ufe0f",
        "color": "#00C9A7",
        "description": "\u6570\u636e\u5de5\u7a0b\u4e0e\u6d41\u7a0b\u81ea\u52a8\u5316\uff0c\u81ea\u52a8\u5316 workflow\u3001\u7ba1\u7406\u8ba1\u7b97\u8d44\u6e90\u3001\u5904\u7406\u6742\u4e8b",
        "aliases": ["\u767d\u9f99\u9a6c", "horse", "\u81ea\u52a8\u5316", "\u6570\u636e"],
    }),
])

COORDINATOR_AGENT: dict = {
    "id": "coordinator",
    "name": "\u5b66\u672f\u8ba8\u8bba\u7a7a\u95f4",
    "emoji": "\U0001f3db\ufe0f",
    "color": "#E91E63",
    "description": "\u79d1\u7814\u56e2\u961f\u5b66\u672f\u8ba8\u8bba\u7a7a\u95f4\uff0c\u8d1f\u8d23\u4efb\u52a1\u5206\u53d1\u3001\u534f\u8c03\u548c\u6c47\u603b",
    "aliases": ["\u8ba8\u8bba", "coord", "\u7ec4\u4f1a", "\u5b66\u672f\u8ba8\u8bba\u7a7a\u95f4"],
}

AGENT_DEFINITIONS: dict = OrderedDict(list(RESEARCH_AGENTS.items()) + [("coordinator", COORDINATOR_AGENT)])


def get_agent_api_url() -> str:
    return f"{GATEWAY_URL.rstrip('/')}{CHAT_COMPLETIONS_PATH}"


def get_auth_headers() -> dict:
    headers = {"Content-Type": "application/json"}
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    return headers
