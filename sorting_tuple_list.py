#!/usr/bin/env python3.10

import numba as nb
from numba.experimental import jitclass
from numba.typed import List
import time
import random

@nb.njit(nogil = True)
def merge(links, rechts):
    # wenn ein array leer ist dann gibt den anderen zurück
    if len(links) == 0:
        return rechts

    if len(rechts) == 0:
        return links

    ausgabe = List()
    index_links = index_rechts = 0

    # geht durch beide eingaben bis alles in ausgabe
    while len(ausgabe) < len(links) + len(rechts):
        # sortiert die elemente
        if links[index_links] <= rechts[index_rechts]:
            ausgabe.append(links[index_links])
            index_links += 1
        else:
            ausgabe.append(rechts[index_rechts])
            index_rechts += 1

        # wenn das ende da ist, dann eindach den rest dran packen
        if index_rechts == len(rechts):
            for i in links[index_links:]:
                ausgabe.append(i)
            break

        if index_links == len(links):
            for i in rechts[index_rechts:]:
                ausgabe.append(i)
            break

    return ausgabe


@nb.njit(nogil = True,fastmath = True)
def insertion_sort(eingabe, links=0, rechts=None):
    if rechts is None:
        rechts = len(eingabe) - 1

    # gehe durch die elemente
    for i in range(links + 1, rechts + 1):
        # das element welches verschoben wird
        key_item = eingabe[i]

        # einfach eine Laufvaribale
        j = i - 1

        # geht durch die liste und findet den tauschpartner
        while j >= links and eingabe[j][0] > key_item[0]:
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
    test = [(random.randint(0,100),random.randint(0,100)) for i in range(1000)]
    test = List(test)
    start = time.time()
    for i in range(100):    
        test = timesort(test)
    print(time.time()-start)
    start = time.time()
    for i in range(100):    
        timesort(test)
    print(time.time()-start)