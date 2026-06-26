"""Browser tool - compatibility layer"""
import logging
logger = logging.getLogger(__name__)

def cleanup_browser() -> None:
    logger.debug("cleanup_browser called")
