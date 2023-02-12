#!/usr/bin/env python3.10
import numba as nb
from numba.experimental import jitclass
from numba.typed import List
import math
import time

"""
Diese Library kann benutzt werden um einige Vektorrechnungen sehr schnell durchzuführen, zudem enthällt sie eine
definition für eine Fundamentale (nur wenige Funktionen) Basis
"""


#Definiert uns einen Vektor mit ein paar grundlegenden Funktionen, allserdings kann man nicht alles mit diesen macgen, da
#Numba sonst etwas langsamer wird, somit wurden nur benutzte Funktionen Implementiert
#der Vektor besitzt nur einen x und y wert :)
@jitclass
class Vector:
    x:float
    y:float
    def __init__ (self, x:float, y:float):
        self.x = x
        self.y = y
    
    def __sub__(self,other:"Vector")->"Vector":
        return Vector(self.x-other.x,self.y-other.y)
    
    def __isub__(self,other:"Vector")->"Vector":
        self.x-=other.x
        self.y-=other.y
        return self
    
    def __add__(self,other:"Vector")->"Vector":
        return Vector(self.x+other.x,self.y+other.y)
    
    def __iadd__ (self, other:"Vector")->"Vector":
        self.x+=other.x
        self.y+=other.y
        return self
    
    def __mul__(self,other: float)->"Vector":
        return Vector(self.x*other,self.y*other)
    
    def __rmul__(other:float ,self)-> "Vector":
        return Vector(self.x*other,self.y*other)
    
    @property
    def length(self)-> float:
        return math.sqrt(self.x**2+self.y**2)
    
    def norm(self):
        lenge = self.length
        self.x /= lenge
        self.y /= lenge
        return self
    
    def ortho(self)->"Vector":
        return Vector(-self.y,self.x)
    
    def __neg__(self)->"Vector":
        return Vector(-self.x,-self.y)
    
    def dot(self, other:"Vector")->float:
        return self.x*other.x+self.y*other.y
    
    def __getitem__(self,key:int)-> float:
        if key ==0 :
            return self.x
        else:
            return self.y
    
    def __setitem__(self,key:int,value:float):
        if key ==0:
            self.x = value
        else :
            self.y = value
    
    
    

#kreiert eine Basis, sie wird genutzt für Normalbasen, dadurch der name Onb.
#sie kann sich nur selbst inertirren, hat eine Determinante,  und die Matrix-Vektor multiplikation wurde implementiert.
@jitclass
class Onb:
    vector: Vector
    a:float
    b:float
    c:float
    d:float
    def __init__(self,vector:Vector):
        self.vector = vector
        self.a = vector[0]
        self.b = -vector[1]
        self.c = vector[1]
        self.d = vector[0]
    
    def invert(self)->"Onb":
        ersatz = Vector(self.vector[0],-self.vector[1])
        return Onb(ersatz*(1/self.determinante))
    
    @property
    def determinante(self)-> float:
        return self.a*self.d-self.b*self.c
    
    def __mul__(self,other:"Vector" )->"Vector":
        return Vector(self.a*other[0]+self.b*other[1],self.c*other[0]+self.d*other[1])
    
    
    
    
    
    
#einige Tests :)
if __name__ == "__main__":
    vector1 = Vector(1,2)
    vector2 = Vector(3,3)
    vector1.norm()
    vector3 = -vector1+vector2
    print(vector1.x)
    print(vector2.x)
    print(vector3.x)

    #@nb.njit
    def initialize():
        vektoren = List()
        for i in range(1000000):
            vektoren.append(Vector(i/2,i/4))
        return vektoren

    vektoren= initialize()

    @nb.njit(fastmath = True)
    def run(vektoren):
        for i in range(len(vektoren)-1):
            vektoren[i]+=vektoren[i+1]*2
    start = time.time()
    run(vektoren)
    print(time.time()-start)
    start = time.time()
    run(vektoren)
    print(time.time()-start)