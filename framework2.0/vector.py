class Vec2:
    __slots__ = 'x','y'
    def __init__(self,x:float,y:float):
        self.x = x
        self.y = y

    def __add__(self,other: "Vec2"):
        return Vec2(other.x + self.x,other.y + self.y)
    
    def __sub__(self,other: "Vec2"):
        return Vec2(self.x - other.x,self.y - other.y)
    
    def __mul__(self,other: int|float):
        return Vec2(self.x * other, self.y * other)
    
    def __iadd__(self,other: "Vec2"):
        self.x += other.x
        self.y += other.y
        return self
    
    def __isub__(self,other: "Vec2"):
        self.x -= other.x
        self.y -= other.y
        return self
    
    def __neg__(self):
        return Vec2(-self.x,-self.y)

    def __repr__(self) -> str:
        return f'Vec2({self.x},{self.y})'


class Vec2Int:
    __slots__ = 'x','y'
    def __init__(self,x:int,y:int):
        self.x = x
        self.y = y

    def __add__(self,other: "Vec2Int"):
        return Vec2Int(other.x + self.x,other.y + self.y)
    
    def __sub__(self,other: "Vec2Int"):
        return Vec2Int(self.x - other.x,self.y - other.y)
    
    def __mul__(self,other: int):
        return Vec2Int(self.x * other, self.y * other)
    
    def __iadd__(self,other: "Vec2Int"):
        self.x += other.x
        self.y += other.y
        return self
    
    def __isub__(self,other: "Vec2Int"):
        self.x -= other.x
        self.y -= other.y
        return self
    
    def __neg__(self):
        return Vec2Int(-self.x,-self.y)

    def __repr__(self) -> str:
        return f'Vec2Int({self.x},{self.y})'
    
    def copy(self):
        return Vec2Int(self.x,self.y)
    
    @property
    def tupled(self) -> tuple[int,int]:
        return self.x,self.y

