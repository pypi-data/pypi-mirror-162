class PropertyChangedEvent():
    def __call__(self, sender, name:str, oldValue, newValue):
        for handler in self._handlers:
            handler(sender, name, oldValue, newValue)

    def __init__(self):
        self._handlers = []
    
    def __iadd__(self, handler):
        self._handlers.append(handler)
        return self
    
    def __isub__(self, handler):
        self._handlers.remove(handler)
        return self

    def __call__(self, *args, **kwds):
        for handler in self._handlers:
            handler(*args,**kwds)
    
    def __getitem__(self, i: int):
        return self._handlers[i]

    def __iter__(self):
        self.idx = 0
        return self

    def __next__(self):
        self.idx += 1
        try:
            return self[self.idx-1]
        except IndexError:
            self.idx = 0
            raise StopIteration

    def __len__(self):
        return len(self._handlers)







