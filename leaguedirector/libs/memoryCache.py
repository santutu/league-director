class MemoryCache:
    _data = {}

    def rememberForever(self, key, value):
        if callable(value):
            value = value()
        self._data[key] = value
        return value

    def get(self, key):
        return self._data[key]

    def getOrNone(self, key):
        if key not in self._data:
            return None
        return self.get(key)

    def delete(self, key):
        return self._data.pop(key, None) is not None

    def clear(self):
        self._data = {}
        return self
