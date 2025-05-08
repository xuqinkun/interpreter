import time

MILLISECONDS = 1000


class Timer:

    def __init__(self):
        self._total = None
        self._start = None


    def start(self):
        self._start = time.time() * MILLISECONDS

    def stop(self):
        if self._start is None:
            raise Exception("Called stop before start")
        self._total = time.time() * MILLISECONDS - self._start
        self._start = None

    def elapse(self):
        if self._total is None:
            self.stop()
        total = int(self._total)
        self._total = None
        ms = int(total % MILLISECONDS)
        sec = int(total / MILLISECONDS)
        return f'{sec}s-{ms}ms'