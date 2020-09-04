class CycleList:
    _items = []
    _listLength = 10

    def __init__(self, listLength):
        self._listLength = listLength

    def getItems(self):
        return self._items

    def addItem(self, val):
        self._items.append(val)
        if self.isOverItemsLength():
            self._items = self._items[1:]

    def getLastItem(self):
        length = self.getLength()
        if length == 0:
            return None
        return self.getItems()[length - 1]

    def getBeforeItemAtLast(self):
        length = self.getLength()
        idx = length - 2
        if idx < 0:
            return None
        return self.getItems()[idx]

    def getLength(self):
        return len(self.getItems())

    def isOverItemsLength(self):
        return self.getLength() > self._listLength

    def isFullItemsLength(self):
        return self.getLength() == self._listLength