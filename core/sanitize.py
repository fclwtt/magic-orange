"""Message sanitization — handle non-ASCII, surrogates, etc."""

from __future__ import annotations
import re

_SURROGATE_RE = re.compile(r"[\ud800-\udfff]")


def sanitize_messages(
    messages: list[dict],
    *,
    strip_images: bool = False,
    max_content_len: int = 0,
) -> list[dict]:
    """Sanitize a message list in-place.

    - Removes surrogate characters
    - Replaces non-ASCII characters where appropriate
    - Optionally strips image content
    - Truncates content to max_content_len
    """
    result = []
    for msg in messages:
        m = dict(msg)
        content = m.get("content", "")
        if isinstance(content, str):
            content = _SURROGATE_RE.sub("\ufffd", content)
            if max_content_len and len(content) > max_content_len:
                content = content[:max_content_len]
            m["content"] = content
        elif isinstance(content, list):
            cleaned = []
            for part in content:
                if strip_images and isinstance(part, dict) and part.get("type") in ("image_url", "image"):
                    continue
                if isinstance(part, dict) and "text" in part:
                    part = dict(part)
                    text = _SURROGATE_RE.sub("\ufffd", part["text"])
                    if max_content_len and len(text) > max_content_len:
                        text = text[:max_content_len]
                    part["text"] = text
                cleaned.append(part)
            m["content"] = cleaned
        result.append(m)
    return result


def truncate_content(content: str, max_chars: int = 100000) -> str:
    """Truncate long content for tool results."""
    if len(content) > max_chars:
        return content[:max_chars] + "\n...[truncated]"
    return content
