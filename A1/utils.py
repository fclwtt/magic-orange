"""Utils - compatibility layer for MagicOrange"""
import json
import os
from pathlib import Path

def atomic_json_write(path: Path, data: dict) -> None:
    """Atomically write JSON to file"""
    tmp_path = path.with_suffix('.tmp')
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    tmp_path.rename(path)

def env_var_enabled(name: str, default: bool = False) -> bool:
    """Check if environment variable is enabled"""
    val = os.environ.get(name, '').lower()
    if val in ('1', 'true', 'yes', 'on'):
        return True
    if val in ('0', 'false', 'no', 'off'):
        return False
    return default

def is_truthy_value(value) -> bool:
    """Check if a value is truthy"""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
    return bool(value)

def atomic_yaml_write(path, data):
    """Atomically write YAML to file"""
    import yaml
    import tempfile
    tmp_path = path.with_suffix('.tmp')
    with open(tmp_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    tmp_path.rename(path)
