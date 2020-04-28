class ItemCounter(object):
    """
    Counts the number of total items shared between services
    """

    def __init__(self, value: int):
        self._value = value

    def increment(self):
        self._value += 1

    def decrement(self):
        self._value -= 1

    def all_done(self):
        return self._value == 0
