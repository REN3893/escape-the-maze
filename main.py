class Direction:
    def __init__(self):
        self._x = 0
        self._y = 0

class Player:
    def __init__(self, name: str):
        self.name = name
        self.direction = Direction()
        
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value: str):
        if len(value) < 1:
            raise NameError("Name length cannot be less than 1 character")
        self._name = value
    
