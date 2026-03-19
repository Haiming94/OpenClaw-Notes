"""
SSE Stream 处理器
解析 OpenAI 兼容的 Server-Sent Events 流
"""
import json
import logging
from typing import Generator, Optional
import requests

logger = logging.getLogger(__name__)


def parse_sse_stream(response: requests.Response) -> Generator[str, None, None]:
    """
    解析 OpenAI 兼容的 SSE 流，逐块 yield 文本内容

    SSE 格式:
    data: {"choices": [{"delta": {"content": "Hello"}}]}
    data: {"choices": [{"delta": {"content": " World"}}]}
    data: [DONE]
    """
    try:
        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line:
                continue

            line = raw_line.strip()

            # SSE 格式: "data: ..."
            if not line.startswith("data:"):
                continue

            data_str = line[5:].strip()

            # 结束信号
            if data_str == "[DONE]":
                return

            try:
                data = json.loads(data_str)
            except json.JSONDecodeError:
                logger.debug(f"跳过无法解析的 SSE 数据: {data_str[:100]}")
                continue

            # 提取 delta content
            choices = data.get("choices", [])
            if not choices:
                continue

            delta = choices[0].get("delta", {})
            content = delta.get("content")
            if content:
                yield content

            # 检查 finish_reason
            finish_reason = choices[0].get("finish_reason")
            if finish_reason == "stop":
                return

    except requests.exceptions.ChunkedEncodingError:
        logger.warning("SSE 流连接中断")
    except Exception as e:
        logger.error(f"SSE 流解析错误: {e}")


def collect_stream_response(response: requests.Response) -> str:
    """收集整个 stream 响应为完整文本"""
    parts = []
    for chunk in parse_sse_stream(response):
        parts.append(chunk)
    return "".join(parts)


def parse_non_stream_response(response: requests.Response) -> Optional[str]:
    """解析非 stream 响应"""
    try:
        data = response.json()
        choices = data.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            return message.get("content", "")
        return None
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"解析非 stream 响应失败: {e}")
        return None
