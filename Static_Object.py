#!/usr/bin/env python3.10
import numba as nb
from Vector2d import Vector
from Vector2d import Onb
from numba.experimental import jitclass
import math
"""
In dieser Library werden Statische Objekte erstellt, es gibt Kästen und Kreise (im zugehöriegem Programm Pins)
"""

#Kann Pins erzeugen, diese besitzen nur eine Position :).
@jitclass
class Hindernisspins:
    x : float
    y : float
    pos : Vector
    groese_des_pin : float
    grose : float
    def __init__(self,x:float,y:float,groese_des_pin:float):
        self.pos=Vector(x,y)
        self.grose=groese_des_pin

#Quader oder auch Kästen werden im Folgendem erstellt, diese besitzen eine eigene Basis um Stöße zu berechnen,
#des weiteren gibt es eine position und winkel zum erzeugen via Matplotlib
@jitclass
class Quader:
    x1:float
    x2:float
    y1:float
    y2:float
    width:float
    start : Vector
    length:float
    vektor:Vector
    orthovektor:Vector
    pos:Vector
    angle:float
    onb:Onb
    fliponb:Onb
    def __init__(self,x1,y1,x2,y2,width):
        self.width=width
        self.start=Vector(x1,y1)
        self.vektor=Vector(x2,y2)-self.start
        self.length = self.vektor.length
        self.vektor.norm()
        o_norm = self.vektor.ortho()
        self.pos=self.start+self.vektor*0.5*self.length+o_norm*0.5*width
        if self.vektor[0] > 0:
            angle=math.atan(self.vektor[1]/self.vektor[0])
        elif self.vektor[0]<0:
           angle=math.atan(self.vektor[1]/self.vektor[0])+math.pi
        else:
           angle=math.pi/2
        self.angle=180*angle/math.pi
        self.onb=Onb(self.vektor)
        self.fliponb=self.onb.invert()
        self.length*=0.5
        self.width*=0.5
        self.vektor=self.vektor*self.length
        self.orthovektor=o_norm*self.width
