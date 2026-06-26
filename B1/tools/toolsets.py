"""
Toolsets compatibility shim for MagicOrange.
Provides toolset validation and resolution.
"""
from typing import Optional, Dict, List


# Known toolsets
KNOWN_TOOLSETS = {
    "terminal": "终端和进程管理",
    "file": "文件操作",
    "web": "网络搜索",
    "browser": "浏览器自动化",
    "memory": "记忆工具",
    "skills": "Skill 管理",
}


def validate_toolset(name: str) -> bool:
    """Validate if a toolset name is known."""
    return name in KNOWN_TOOLSETS


def resolve_toolset(name: str) -> Optional[Dict]:
    """Resolve a toolset name to its configuration."""
    if name in KNOWN_TOOLSETS:
        return {"name": name, "description": KNOWN_TOOLSETS[name]}
    return None


def get_available_toolsets() -> Dict[str, str]:
    """Get all available toolsets."""
    return KNOWN_TOOLSETS.copy()
