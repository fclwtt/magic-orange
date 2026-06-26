"""Singularity environment - compatibility layer"""
def is_singularity():
    return False

def _get_scratch_dir():
    return "/tmp/magic-orange"

class SingularityEnvironment:
    def __init__(self, **kwargs):
        pass
    def execute(self, cmd, **kwargs):
        import subprocess
        return subprocess.run(cmd, shell=True, capture_output=True, text=True)
