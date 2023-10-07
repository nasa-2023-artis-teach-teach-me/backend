import math
from typing import List

class Position:

    def __init__(self, loc: List[float]):

        if len(loc) != 2:
            raise ValueError
        
        self.x = loc[0]
        self.y = loc[1]

    def toInt(self, resolution: int):

        self.x = int(self.x * resolution)
        self.y = int(self.y * resolution)

        return self
    
    def __sub__(self, other):

        return math.sqrt(math.pow(self.x - other.x, 2) + math.pow(self.y - other.y, 2))
    
    def __mul__(self, other):

        return Position([self.x * other, self.y * other])
    
    def __repr__(self):

        return f"[{self.x}, {self.y}]"