# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 10:31:42 2022

@author: ggil
"""
from math import sqrt

unit = 'u'

def surface_area(polyhedron, side):
    if (polyhedron == 'tetrahedron'):
        return sqrt(3) * side ** 2
    elif (polyhedron == 'cube'):
        return 2 * side ** 2
    elif (polyhedron == 'octahedron'):
        return 2 * sqrt(3) * side ** 2
    elif (polyhedron == 'dodecahedron'):
        return 3 * sqrt(25 + 10 * sqrt(5)) * side ** 2
    elif (polyhedron == 'icosahedron'):
        return 5 * sqrt(3) * side ** 2


def volume(polyhedron, side):
    if (polyhedron == 'tetrahedron'):
        return sqrt(2) / 12 * side ** 3
    elif (polyhedron == 'cube'):
        return side ** 3
    elif (polyhedron == 'octahedron'):
        return sqrt(2) / 3 * side ** 3
    elif (polyhedron == 'dodecahedron'):
        return ((15 + 7 * sqrt(5))) / 4 * side ** 3
    elif (polyhedron == 'icosahedron'):
        return 5 / 12 * (3 + sqrt(5)) * side ** 3
