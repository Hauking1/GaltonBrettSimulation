#!/usr/bin/env python3.10

import numba as nb
from numba.experimental import jitclass
from numba.typed import List
import time
import random

@nb.njit(nogil = True)
def merge(eingabe1,eingabe2):
    for i in eingabe2:
        eingabe1.append(i)
    return eingabe1


@nb.njit(nogil = True)
def insertion_sort(eingabe, left=0, right=None):
    if right is None:
        right = len(eingabe) - 1

    # gehe durch die elemente
    for i in range(left + 1, right + 1):
        # das element welches verschoben wird
        key_item = eingabe[i]

        # einfach eine Laufvaribale
        j = i - 1

        # geht durch die liste und findet den tauschpartner
        while j >= left and eingabe[j][0] > key_item[0]:
            # bewegt item nach rechts
            eingabe[j + 1] = eingabe[j]
            j -= 1

        # so jetzt ist alles an seiner stelle
        eingabe[j + 1] = key_item

    return eingabe

@nb.njit(nogil = True)
def timesort(eingabe):
    min_laenge = 32
    n = len(eingabe)

    #teile die liste auf
    for i in range(0, n, min_laenge):
        insertion_sort(eingabe, i, min((i + min_laenge - 1), n - 1))

    # packt die slices zusammen von min an bis länger als eingabe
    groese = min_laenge
    while groese < n:
        # schaut was zusammen muss
        for start in range(0, n, groese * 2):
            # berechnet die mitte beider slices und das ende des letzten slices
            midpoint = start + groese - 1
            end = min((start + groese * 2 - 1), (n-1))

            # packt die slices zusammen
            merged_eingabe = merge(
                eingabe[start:midpoint + 1],
                eingabe[midpoint + 1:end + 1])

            # und setzt wiederin eingabe ein
            eingabe[start:start + len(merged_eingabe)] = merged_eingabe

        # verdoppelt immer die eingabe länge
        groese *= 2

    return eingabe


if __name__ =="__main__":
    test = [(random.randint(0,100),random.randint(0,100)) for i in range(10000)]
    test = List(test)
    start = time.time()
    for i in range(100):    
        test = timesort(test)
    print(time.time()-start)
    start = time.time()
    for i in range(1):    
        timesort(test)
    print(time.time()-start)
    print(test)