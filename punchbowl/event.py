class Event(object):
    def __init__(self):
        self.callbacks = []

    def add(self, other):
        self.callbacks.append(other)
        return self

    def clear(self):
        self.callbacks = []

    def __call__(self, *args, **kwargs):
        for callback in self.callbacks:
            callback(*args, **kwargs)
