"""Interrupt - compatibility layer"""
import logging
logger = logging.getLogger(__name__)

def set_interrupt(handler=None) -> None:
    logger.debug("set_interrupt called")

def is_interrupted() -> bool:
    """Check if operation was interrupted"""
    return False

import threading
_interrupt_event = threading.Event()
