"""Toolsets - compatibility layer for MagicOrange"""
from typing import Dict, List, Optional, Set

KNOWN_TOOLSETS = {
    "terminal": {"description": "终端和进程管理", "tools": ["terminal"]},
    "file": {"description": "文件操作", "tools": ["read_file", "write_file", "patch"]},
    "web": {"description": "网络搜索", "tools": ["web_search", "web_extract"]},
    "browser": {"description": "浏览器自动化", "tools": []},
    "memory": {"description": "记忆工具", "tools": []},
    "skills": {"description": "Skill管理", "tools": []},
    "basic": {"description": "基础工具", "tools": ["dummy_tool", "get_time"]},
}

def validate_toolset(name: str) -> bool:
    return name in KNOWN_TOOLSETS

def resolve_toolset(name: str) -> Optional[Dict]:
    if name in KNOWN_TOOLSETS:
        return {"name": name, **KNOWN_TOOLSETS[name]}
    return None

def get_available_toolsets() -> Dict[str, str]:
    return {k: v["description"] for k, v in KNOWN_TOOLSETS.items()}

def get_all_toolsets() -> Dict[str, dict]:
    return KNOWN_TOOLSETS.copy()

def get_toolset_info(name: str) -> Optional[dict]:
    return KNOWN_TOOLSETS.get(name)
