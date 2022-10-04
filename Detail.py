from dataclasses import dataclass

@dataclass
class Detail:
    name: str
    mass: float
    length: float
    pos: float = 0


    def move(self, x):
        self.pos += x
        return True

    def move_to(self, x):
        self.pos = x
        return True

    def rename(self, name, array):
        if name == self.name:
            return True
        if name not in [obj.name for obj in array if obj != self]:
            self.name = name
            return True
        else:
            return False

    def __repr__(self):
        return f'Name: {self.name}, Mass: {self.mass}, Length: {self.length}, Position: {self.pos}'
