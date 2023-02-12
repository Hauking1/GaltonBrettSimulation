#!/usr/bin/env python3.10
import numba as nb
from numba.experimental import jitclass
from numba.typed import List

@jitclass
class Grid:
    xborder : float
    yborder : float
    number_x : int
    number_y : int
    

