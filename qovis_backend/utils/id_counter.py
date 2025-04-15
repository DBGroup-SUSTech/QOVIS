class IdCounter:
    def __init__(self, start=0):
        self._id = start - 1

    def get(self):
        self._id += 1
        return self._id
