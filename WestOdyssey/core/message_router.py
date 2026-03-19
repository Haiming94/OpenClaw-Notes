import re
from typing import Optional, Tuple
from core.config import AGENT_DEFINITIONS

_ALIAS_MAP: dict[str, str] = {}
for _agent_id, _agent_def in AGENT_DEFINITIONS.items():
    _ALIAS_MAP[_agent_id] = _agent_id
    _ALIAS_MAP[_agent_def["name"]] = _agent_id
    for alias in _agent_def.get("aliases", []):
        _ALIAS_MAP[alias] = _agent_id

_sorted_aliases = sorted(_ALIAS_MAP.keys(), key=len, reverse=True)
_escaped = [re.escape(k) for k in _sorted_aliases]
_MENTION_PATTERN = re.compile(
    r"@(" + "|".join(_escaped) + r")(?:\s|$|[,.\uff0c\u3002])",
    re.IGNORECASE,
)


def resolve_agent(mention: str) -> Optional[str]:
    clean = mention.strip().lstrip("@").strip()
    return _ALIAS_MAP.get(clean)


def parse_message(text: str, current_agent_id: str = "literature") -> Tuple[str, str]:
    match = _MENTION_PATTERN.search(text)
    if match:
        mention_text = match.group(1)
        agent_id = _ALIAS_MAP.get(mention_text, current_agent_id)
        clean_text = text[:match.start()] + text[match.end():]
        clean_text = clean_text.strip()
        if not clean_text:
            clean_text = text
        return clean_text, agent_id
    return text, current_agent_id


def get_agent_info(agent_id: str) -> Optional[dict]:
    return AGENT_DEFINITIONS.get(agent_id)


def list_agents() -> list[dict]:
    return list(AGENT_DEFINITIONS.values())
