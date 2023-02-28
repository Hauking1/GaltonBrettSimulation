#!/usr/bin/env python3.10
import numba as nb
from numba.experimental import jitclass
from numba.typed import List
import Vector2d as Vec

#@jitclass
class Ball_Grid:
    xborder : float
    yborder : float
    number_x : int
    number_y : int
    grid : nb.types.DictType(nb.types.int64,nb.types.DictType(nb.types.int64,nb.types.ListType(nb.types.int64)))
    def __init__(self,xborder:float,yborder:float,number_x:int,number_y:int):
        self.xborder = xborder
        self.yborder = yborder
        self.number_x = number_x
        self.number_y = number_y
        self.grid = {x:{y:[-1] for y in range(number_y)} for x in range(number_x)}
    
    def empty(self):
        for x in range(self.number_x):
            for y in range(self.number_y):
                self.grid[x][y] = self.grid[x][y][:]

    def __getitem__(self,key:int)-> int:
        return self.grid[key]
    
    def __setitem__(self,key:tuple,value:int):
        self.grid[key[0]][key[1]] = value
    
    def check(self,pos,balls):
        for x in range(self.number_x):
            for y in range(self.number_y):
                if len(self.grid[x][y])>2:
                    for items in self.grid[x][y]:
                        for dx in (-1,0,1):
                            for dy in (-1,0,1):
                                for stosen in self.grid[x+dx][y+dy]:
                                    balls[items].ball_stos(stosen)


if __name__ == "__main__":
    my_grid = Ball_Grid(30.,30.,20,20)
    print(my_grid.grid)
    my_grid.empty()