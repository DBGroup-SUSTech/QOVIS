import sys
import os

class HiddenPrints:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self._original_stdout = None
        self._original_stderr = None

    def __enter__(self):
        if not self.enabled:
            return
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.enabled:
            return
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr