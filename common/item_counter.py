from multiprocessing import Value, Lock


class ItemCounter(object):
    """
    Counts the number of total items shared between services
    """

    def __init__(self, value: int):
        self._val = Value('i', value)
        self._lock = Lock()

    def increment(self):
        with self._lock:
            self._val.value += 1

    def decrement(self):
        with self._lock:
            self._val.value -= 1

    def all_done(self):
        with self._lock:
            return self._val.value == 0
