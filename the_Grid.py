#!/usr/bin/env python3.10
import numba as nb
from numba.experimental import jitclass
from numba.typed import List
import Brett_numba
import Vector2d as Vec

#@jitclass
class Ball_Grid:
    xborder : float
    yborder : float
    number_x : int
    number_y : int
    grid : List
    def __init__(self,xborder:float,yborder:float,number_x:int,number_y:int):
        self.xborder = xborder
        self.yborder = yborder
        self.number_x = number_x
        self.number_y = number_y
        test_liste = [[[]for y in range(number_y)]for x in range(number_x)]
        test_liste[0][0] = Brett_numba.Ball(1,Vec.Vector(0,0),Vec.Vector(0,0),0)
        self.grid = test_liste#List(test_liste)
        del self.grid[0][0]
        print(self.grid)

if __name__ == "__main__":
    my_grid = Ball_Grid(30.,30.,20,20)
    print(my_grid.grid)