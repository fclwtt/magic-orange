"""Vision analysis — analyze images via LLM vision capabilities."""

from __future__ import annotations
import base64, json, os
from typing import Any


def _encode_image(path_or_url: str) -> str | None:
    """Read an image file and return a base64 data URL."""
    if path_or_url.startswith(("http://", "https://")):
        try:
            import httpx
            resp = httpx.get(path_or_url, timeout=30)
            ext = path_or_url.rsplit(".", 1)[-1].lower()
            mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "webp": "image/webp"}
            return f"data:{mime.get(ext, 'image/png')};base64,{base64.b64encode(resp.content).decode()}"
        except Exception:
            return None
    try:
        with open(path_or_url, "rb") as f:
            data = f.read()
        ext = path_or_url.rsplit(".", 1)[-1].lower()
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "webp": "image/webp"}
        return f"data:{mime.get(ext, 'image/png')};base64,{base64.b64encode(data).decode()}"
    except Exception:
        return None


def vision_analyze(args: dict[str, Any]) -> str:
    """Analyze an image. Returns a dict that the agent loop handles.

    The actual vision call is made by the LLM provider - this tool just
    encodes the image and returns a formatted string the provider can use.
    """
    path = args.get("path", args.get("url", ""))
    if not path:
        return json.dumps({"error": "path or url required"})
    data_url = _encode_image(path)
    if not data_url:
        return json.dumps({"error": f"Cannot read image: {path}"})
    return json.dumps({
        "type": "image",
        "source": path,
        "data_url": data_url,
        "description": args.get("description", ""),
    })


SCHEMAS = {
    "vision_analyze": {
        "description": "Analyze an image by file path or URL",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Local file path or URL"},
            "description": {"type": "string", "description": "Optional description of what to look for"},
        }},
    },
}
