#!/usr/bin/env python3.10
import Vector2d as Vec
import numba as nb
from numba.experimental import jitclass
from numba.typed import List
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import time
import Static_Object as SO

"""
Smuliert ein Galtonbrett mit stößen unter den Bällen und einer Funktion zum überspringen der ersten Bilder,
nutzt ein eigens erstelltes Modul für Vektoren sowie für objekte. Zudem wird Numba großflächig eingesetzt zur beschleunigung
Eine Überspringung von 100000 Frames und 100 Bällen ergibt auf einen Laptop ca 6 min wartezeit
(ohne compilier zeit also insgesammt etwas länger), und eine Verteilung von 4000 durchgefallenen Bällen.
"""


#wie viele Frames übersprungen werden sollen, default 10000, 100 Frames werden immer übersprungen
amount_skip = int(input("Wie viele Frames möchtest du übersprungen haben,\n ohne eingabe überspringt er 10000 Bilder,\n 100 werden immer Übersprungen: ")or 10000)

#größe und anzahl der Bälle
radius=float(input("Gib mir den Radius der Bälle, ohne eingabe ist der Radius 1: ") or 1)
anzahl=int(input("Gib mir die Anzahl der Bälle,ohne eingabe werden 100 Bälle berechnet: ")or 100)


#algemeine Parameter für das Galtonbrett :)
anzahlebenen=10
pin_grose=2
pin_abstand=20
ebenenabstand=10

#Simulationsparameter
stosparameter=0.3
delta_t=0.01
beschleunigung=Vec.Vector(0.,-15.)
beschleunigung = beschleunigung * delta_t
count = 0

#Plot parameter und der Verteilungsplot :)
yborder=anzahlebenen*ebenenabstand
xborder=anzahlebenen/2*pin_abstand+5
fig, (ax,ax1) = plt.subplots(1,2)
ax.set_xlim(-xborder,xborder)
ax.set_ylim(-yborder,yborder)
ax.set_aspect("equal")
ax1.set_ylim(0,1.02)

text = ax1.text(0,0.9,"Bälle: " + str(count))
x_verteilung = list(range(anzahlebenen+1))
verteilung = [0]*(anzahlebenen+1)
verteilung_fast = List([0]*(anzahlebenen+1))
bars = ax1.bar(x_verteilung,verteilung)

#bis zur class Ball die benötigten Funktionen um mit matplotlib zu arbeiten, etwas mehr als sonst wegen Numba.
#das darstellen der Verteilung macht die Simulation signifikant langsamer, sie wird aufgrund der aussagekraft trotzdem
#berechnet
alle_Artists_balls = list()
alle_Artists_pins = list()
alle_Artists_kasten = list()
def add_ball_list(ball):
    alle_Artists_balls.append(plt.Circle((ball.pos[0], ball.pos[1]), radius=ball.radius, color = [random.random(),random.random(),random.random()]))
    ax.add_patch(alle_Artists_balls[ball.index])

def artist_set_center(ball_info):
    alle_Artists_balls[ball_info[0]].set_center((ball_info[1][0],ball_info[1][1]))

def add_pin_list(pin):
    alle_Artists_pins.append(plt.Circle((pin.pos[0], pin.pos[1]), radius = pin.grose, color="red"))
    ax.add_patch(alle_Artists_pins[-1])

def add_kasten_list(kasten):
    alle_Artists_kasten.append(plt.Rectangle(kasten.start,kasten.length*2,kasten.width*2,angle = kasten.angle,color="red",))
    ax.add_patch(alle_Artists_kasten[-1])

def update_text(count):
    alle_Artists_balls[-1] = ax1.text(0,0.9,"Bälle: " + str(count))


def update_bars(verteilung_fast,animator):
    for zahl1,zahl in enumerate(verteilung_fast):
        verteilung[zahl1] += zahl
    for zahl,bar in enumerate(bars):
        if count != 0:
            bar.set_height(verteilung[zahl]/count)
        animator.append(bar)

def update_verteilung(verteilung_fast):
    for zahl,i in enumerate(verteilung_fast):
        verteilung[zahl]+= i



"""Die folgende Klasse ist neben dem Vektor aus dem Importiertem Modul Vector2D das Herz der berechnung.
Es werden Bälle mit vielen eigenschaften Definiert, diese können untereinander, und mit Objekten Stoßen.
Die Funktionen add_ball und set_center sind für die Interaktion mit Matplotlib :)
"""
@jitclass
class Ball:
    radius : int
    pos : Vec.Vector
    speed : Vec.Vector
    index : int
    def __init__ (self,radius :float, initialx:float, initialy:float, index:int):
        self.radius = radius
        self.pos = Vec.Vector(initialx,initialy)
        self.speed = Vec.Vector((random.random()-0.5)*10,0.)
        self.index = index
    
    def add_ball(self)->"Ball":
        return self
    
    def setcenter(self)->tuple:
        return (self.index,self.pos)
    
    #Updated die Position in folge der Geschwindigkeit und Gravitation
    def move(self,delta_t:float, beschleunigung:"Vector"):
        self.pos += self.speed*delta_t
        self.speed += beschleunigung
    
    #Berechnet die Stöße mit den Seitenwänden des Plotes, und das resetten der Bälle beim durchlaufen der unteren Kante
    def wand_stos(self,yborder:float,xborder:float,counter : int, verteilung_fast,pin_abstand)->int:
        verteilung_andere = verteilung_fast.copy()
        if self.pos[1]<=-yborder:
            self.pos[1]=2/3*yborder+self.pos[0]**2/yborder
            self.speed = Vec.Vector((random.random()-0.5)*10,0.)
            counter+=1
            verteilung_andere[int((self.pos[0]+xborder)//pin_abstand)]+=1
        elif self.pos[0]<-xborder and self.speed[0]<0:
            self.speed[0]=-self.speed[0]
        elif self.pos[0]>xborder and self.speed[0]>0:
            self.speed[0]=-self.speed[0]
        return counter,verteilung_andere
    
    #Berechnet die Stöße der Bälle untereinander, dies wird mit einer Basistransformation der Geschwindigkeiten gemacht,
    #die Orthogonal zur Stoßebene Geschwindigkeitskomponente wird getauscht, da beide Bälle die selbe Masse haben :)
    def ball_stos(self,balls : List):
        for bal in balls[self.index+1:]:
            abstand_vektor = bal.pos-self.pos
            if abstand_vektor.length <= 2*self.radius:
                if self.speed.dot(abstand_vektor)>0 or bal.speed.dot(abstand_vektor)<0:
                    onb = Vec.Onb(abstand_vektor.norm())
                    invonb = onb.invert()
                    bal.speed = invonb*bal.speed
                    self.speed = invonb*self.speed
                    o_speed=self.speed[0]
                    self.speed[0] = bal.speed[0]
                    bal.speed[0] = o_speed
                    self.speed = onb*self.speed
                    bal.speed = onb*bal.speed
    
    #Berechnet analog zu dem Ball stößen die Stöße mit einem Pin
    def pin_stos(self,hindernisspins : List,stosparameter:float):
        for hindernis in hindernisspins:
            abstand_vektor = hindernis.pos-self.pos
            if abstand_vektor.length<=self.radius+hindernis.grose:
                if self.speed.dot(abstand_vektor)>0:
                    onb = Vec.Onb(abstand_vektor.norm())
                    invonb = onb.invert()
                    self.speed=invonb*self.speed
                    self.speed[0]=-stosparameter*self.speed[0]
                    self.speed=onb*self.speed
    
    #Berechnet den Stoß mit der Ecke eines Kasten, wird analog zu der Berechnung für die Pins berechnet
    def kasten_stos_edge(self,kasten,nabstand):
        nabstand.norm
        stosmatrix=Vec.Onb(nabstand)
        self.speed=kasten.onb*self.speed
        self.speed=stosmatrix.invert()*self.speed
        self.speed[0]*=-1
        self.speed=stosmatrix*self.speed
        self.speed=kasten.fliponb*self.speed
    
    #Berechnet den Stoß mit den Kästen, ruft auch den Stoß mit der Ecke auf. Die Stöße mit den Käste funktioniert über
    #eine Transformation der Geschwindigkeit und des Abstanden in das Bezugsystem den Kasten,
    #dort kann man dann Koordinaten abfragen und die Richtige berechnung durchführen
    def kasten_stos(self,hindernis_kasten):
        for kasten in hindernis_kasten:
            abstand_vektor = kasten.fliponb*(self.pos-kasten.pos)
            if abs(abstand_vektor[0])-self.radius<=kasten.length and abs(abstand_vektor[1])-self.radius<=kasten.width:
                self.speed=kasten.fliponb*self.speed
                if (abstand_vektor[0]<-kasten.length and self.speed[0]>0) or ((abstand_vektor[0]>kasten.length and self.speed[0]<0)) :
                    self.speed[0]*=-1
                elif (abstand_vektor[1]<-kasten.width and self.speed[1]>0) or ((abstand_vektor[1]>kasten.width and self.speed[1]<0)) :
                    self.speed[1]*=-1
                else:
                    if abstand_vektor[0]>kasten.length and abstand_vektor[1]>kasten.width:
                        nabstand=self.pos-(kasten.pos+kasten.vektor+kasten.orthovektor)
                        abstand_vektor=kasten.fliponb*nabstand
                        if abstand_vektor.dot(self.speed)<0:
                            self.kasten_stos_edge(kasten,nabstand)
                    elif abstand_vektor[0]<kasten.length and abstand_vektor[1]>kasten.width:
                        nabstand=self.pos-(kasten.pos-kasten.vektor+kasten.orthovektor)
                        abstand_vektor=kasten.fliponb*nabstand
                        if abstand_vektor.dot(self.speed)<0:
                            self.kasten_stos_edge(kasten,nabstand)
                            
                    elif abstand_vektor[0]>kasten.length and abstand_vektor[1]<kasten.width:
                        nabstand=self.pos-(kasten.pos+kasten.vektor-kasten.orthovektor)
                        abstand_vektor=kasten.fliponb*nabstand
                        if abstand_vektor.dot(self.speed)<0:
                            self.kasten_stos_edge(kasten,nabstand)
                            
                    else:
                        nabstand=self.pos-(kasten.pos-kasten.vektor-kasten.orthovektor)
                        abstand_vektor=kasten.fliponb*nabstand
                        if abstand_vektor.dot(self.speed)<0:
                            self.kasten_stos_edge(kasten,nabstand)
                    
                self.speed=kasten.onb*self.speed

#Im folgenden werden die Kästen auf dem Bildschirm Platziert und zum Stoßen erzeugt, das ganze passiert auch
#wenn die Pins erstellt werden (siehe weiter unten)
hindernis_kasten=List()
hindernis_kasten.append(SO.Quader(-8*radius,ebenenabstand+radius,-xborder,2/3*yborder-2*radius-1,radius))
hindernis_kasten.append(SO.Quader(8*radius,ebenenabstand,xborder,2/3*yborder-2*radius-1,radius))
hindernis_kasten.append(SO.Quader(-8*radius,ebenenabstand+radius,-xborder,-ebenenabstand*anzahlebenen+ebenenabstand,radius))
hindernis_kasten.append(SO.Quader(8*radius,ebenenabstand,xborder,-ebenenabstand*anzahlebenen+ebenenabstand,radius))

def positionieren_quader(i,initialx,initialy):
    if i == anzahlebenen:
        hindernis_kasten.append(SO.Quader(initialx+pin_grose/2,-yborder,initialx+pin_grose/2,initialy,pin_grose))
        hindernis_kasten.append(SO.Quader(-initialx+pin_grose/2,-yborder,-initialx+pin_grose/2,initialy,pin_grose))



#Erstellt die Pins für die Simulation und die Kästen am unterem Brett :)
#Die Pins werden abhängig der obigen konstanten definiert
#der erste Block macht die Pins oberhalb des Brettes (zur beschleunigung des eintauchen ins Brett), der Zweite Block
#erstellt die Pins für das Brett
hindernisspins = List()
initialx=0
hindernisspins.append(SO.Hindernisspins(initialx,2/3*yborder-2*pin_grose-1,pin_grose))
hindernisspins.append(SO.Hindernisspins(initialx,ebenenabstand+8*radius+2*pin_grose+2*radius,pin_grose))
while initialx< xborder-6*radius-5*pin_grose:
    initialx+=4*radius+2*pin_grose
    hindernisspins.append(SO.Hindernisspins(initialx,2/3*yborder-2*pin_grose-1,pin_grose))
    hindernisspins.append(SO.Hindernisspins(-initialx,2/3*yborder-2*pin_grose-1,pin_grose))

initialy=ebenenabstand
for i in range(1,anzahlebenen+1):
    initialy-=ebenenabstand
    if i%2==0:
        for k in range(int(i/2)):
            initialx=k*pin_abstand+pin_abstand/2
            hindernisspins.append(SO.Hindernisspins(initialx,initialy,pin_grose))
            hindernisspins.append(SO.Hindernisspins(-initialx,initialy,pin_grose))
            positionieren_quader(i,initialx,initialy)
    else:
        for k in range(int(i/2)+1):
            if k==0:
                hindernisspins.append(SO.Hindernisspins(0,initialy,pin_grose))
                positionieren_quader(i,0,initialy)
            else:
                initialx=k*pin_abstand
                hindernisspins.append(SO.Hindernisspins(initialx,initialy,pin_grose))
                hindernisspins.append(SO.Hindernisspins(-initialx,initialy,pin_grose))
                positionieren_quader(i,initialx,initialy)
for pins in hindernisspins:
    add_pin_list(pins)
for kasten in hindernis_kasten:
    add_kasten_list(kasten)


#plaziert die Bälle über dem Brett
balls = List()
initialx=0
initialy=2/3*yborder
for i in range(anzahl):
    initialx+=2*radius+0.1
    if initialx>=xborder-2*radius:
        initialy+=2*radius+0.1
        initialx=0
    if initialx == 0:
        balls.append(Ball(radius,initialx,initialy,i))
        add_ball_list(balls[i])
    else:
        if i%2 == 0:
            balls.append(Ball(radius,initialx,initialy,i))
            add_ball_list(balls[i])
        else:
            balls.append(Ball(radius,-initialx,initialy,i))
            add_ball_list(balls[i])

alle_Artists_balls.append(text)

#Die Berechnung der Frames ohne Darstellung und stark beschleunigt geht alle checks durch und gibt die Verteilung aus
@nb.njit(nogil = True)
def update_fast(balls,delta_t,beschleunigung,hindernisspins,stosparameter,hindernis_kasten,counter,verteilung_fast,pin_abstand)->int:
    count = 0
    vert = verteilung_fast.copy()
    for bal in balls:
        bal.move(delta_t,beschleunigung)
        variable = bal.wand_stos(yborder,xborder,counter,verteilung_fast,pin_abstand)
        count += variable[0]
        for zahl,i in enumerate(variable[1]):
            vert[zahl]+= i
        bal.ball_stos(balls)
        bal.pin_stos(hindernisspins,stosparameter)
        bal.kasten_stos(hindernis_kasten)
    counter = count
    return counter,vert

#Die von Matplotlib benutzte Funktion zum darstellen und Updaten des Plots
def update(t):
    global count
    variable = update_fast(balls,delta_t,beschleunigung,hindernisspins,stosparameter,hindernis_kasten,counter,verteilung_fast,pin_abstand)
    count += variable[0]
    update_text(count)
    for ball in balls:
        artist_set_center(ball.setcenter())
    animator = alle_Artists_balls.copy()
    update_bars(variable[1],animator)
    return animator

#Um das Plotten mittels Blit zu beschleunigen (Matplotlip)
def initialize():
    for ball in balls:
        artist_set_center(ball.setcenter()) 
    animator = alle_Artists_balls.copy()
    return animator

#Die funktion zum überspingen der Frames (berechnet alle Bälle trotzdem richtig,also mit Weg und allem :))
@nb.njit(nogil = True)
def skip(anzahl:int,balls:List,delta_t:float,beschleunigung:"Vector",hindernisspins:List,stosparameter,hindernis_kasten,counter:int,verteilung_fast,pin_abstand)->int:
    count = 0
    verteilung_andere = verteilung_fast.copy()
    for i in range(anzahl):
        variable = update_fast(balls,delta_t,beschleunigung,hindernisspins,stosparameter,hindernis_kasten,counter,verteilung_fast,pin_abstand)
        count += variable[0]
        for zahl,i in enumerate(variable[1]):
            verteilung_andere[zahl] += i
        
    counter = count
    return counter,verteilung_andere

# der folgende Block händelt das Jitten der Funktionen, in dem es diese erst mal 100 mal berechnet,
#danach das echte Skippen, zum interagieren mit Matplotlib werden noch einige Konstanten erstellt.
#gibt noch die Zeit welche für die ersten 100 durchläufe gebraucht wurde aus und jene zum skippen der eingegebenen Frames
counter = 0
start = time.time()
variable = skip(100,balls,delta_t,beschleunigung,hindernisspins,stosparameter,hindernis_kasten,counter,verteilung_fast,pin_abstand)
count += variable[0]
update_verteilung(variable[1])
print(time.time()-start)
start = time.time()
variable = skip(amount_skip,balls,delta_t,beschleunigung,hindernisspins,stosparameter,hindernis_kasten,counter,verteilung_fast,pin_abstand)
count += variable[0]
update_verteilung(variable[1])
print(time.time()-start)

#Die Animation von Matplotlib
intervall=100*delta_t
ani = animation.FuncAnimation(fig, update, repeat=False,init_func=initialize,blit=True,interval=intervall)
plt.show()