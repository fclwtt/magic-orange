"""
Tools registry shim - re-exports from core.tool_registry
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.tool_registry import ToolRegistry, ToolEntry

# Create a global registry instance (singleton)
registry = ToolRegistry()

__all__ = ["registry", "ToolRegistry", "ToolEntry"]

def tool_error(message: str, **kwargs) -> str:
    """Return error message in tool format"""
    import json
    return json.dumps({"error": message, **kwargs})
