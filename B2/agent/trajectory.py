"""Trajectory - compatibility layer"""
from typing import Optional

def convert_scratchpad_to_think(content: str) -> str:
    return content

def has_incomplete_scratchpad(content: str) -> bool:
    return False

def save_trajectory(**kwargs) -> None:
    pass
