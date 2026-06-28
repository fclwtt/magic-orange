"""Web search & extract — 最小实现（httpx + 正则）"""

from __future__ import annotations
import json, re, logging
from typing import Any
try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)

def _extract_text(html: str) -> str:
    """从 HTML 中提取可读文本。"""
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    html = re.sub(r'<[^>]+>', ' ', html)
    html = re.sub(r'\s+', ' ', html).strip()
    return html[:8000]


def web_search(args: dict[str, Any]) -> str:
    """搜索互联网（使用 DuckDuckGo 的 HTML 结果）。"""
    query = args.get("query", "")
    if not query:
        return json.dumps({"error": "query required"})
    if httpx is None:
        return json.dumps({"error": "httpx not installed; pip install httpx"})

    try:
        url = f"https://html.duckduckgo.com/html/?q={httpx.utils.quote(query)}"
        resp = httpx.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        results = []
        for match in re.finditer(r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>', resp.text):
            href = match.group(1)
            title = re.sub(r'<[^>]+>', '', match.group(2)).strip()
            results.append({"title": title, "url": href})
        return json.dumps({"results": results[:10]})
    except Exception as e:
        return json.dumps({"error": str(e)})


def web_extract(args: dict[str, Any]) -> str:
    """提取网页内容。"""
    url = args.get("url", "")
    if not url:
        return json.dumps({"error": "url required"})
    if httpx is None:
        return json.dumps({"error": "httpx not installed"})

    try:
        resp = httpx.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        text = _extract_text(resp.text)
        return json.dumps({"url": url, "content": text[:8000]})
    except Exception as e:
        return json.dumps({"error": str(e)})


SCHEMAS = {
    "web_search": {
        "description": "Search the web for information",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
    },
    "web_extract": {
        "description": "Extract content from a web page",
        "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
    },
}
