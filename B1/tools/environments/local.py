"""Local environment - compatibility layer"""
class LocalEnvironment:
    def __init__(self, **kwargs):
        pass
    def execute(self, cmd, **kwargs):
        import subprocess
        return subprocess.run(cmd, shell=True, capture_output=True, text=True)
