"""Status - compatibility layer"""
class StatusManager:
    def __init__(self, **kwargs):
        pass
    def get_status(self, **kwargs):
        return {}

import threading
_locks = {}
_locks_lock = threading.Lock()

def acquire_scoped_lock(scope, timeout=None):
    """Acquire a scoped lock"""
    with _locks_lock:
        if scope not in _locks:
            _locks[scope] = threading.Lock()
        lock = _locks[scope]
    acquired = lock.acquire(timeout=timeout)
    return acquired

def release_scoped_lock(scope):
    """Release a scoped lock"""
    with _locks_lock:
        if scope in _locks:
            try:
                _locks[scope].release()
            except RuntimeError:
                pass
