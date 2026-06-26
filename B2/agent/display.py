"""Display - compatibility layer"""

class KawaiiSpinner:
    def __init__(self, *args, **kwargs):
        pass
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def update(self, *args):
        pass

def build_tool_preview(**kwargs) -> str:
    return ""

def get_cute_tool_message(**kwargs) -> str:
    return ""

def _detect_tool_failure(**kwargs) -> bool:
    return False

def get_tool_emoji(**kwargs) -> str:
    return "⚡"
