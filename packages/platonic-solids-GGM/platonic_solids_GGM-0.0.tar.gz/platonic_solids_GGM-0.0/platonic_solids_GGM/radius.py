# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 10:33:13 2022

@author: ggil
"""
from math import sqrt

pi=3.141592

def circumradius(polyhedron, side):
    if (polyhedron == 'tetrahedron'):
        return sqrt(6) / 4 * side
    elif (polyhedron == 'cube'):
        return sqrt(3) / 2 * side
    elif (polyhedron == 'octahedron'):
        return sqrt(2) / 2 * side
    elif (polyhedron == 'dodecahedron'):
        return sqrt(3) * (1 + sqrt(5)) / 4 * side
    elif (polyhedron == 'icosahedron'):
        return sqrt(10 + 2 * sqrt(5)) / 4 * side


def inradius(polyhedron, side):
    if (polyhedron == 'tetrahedron'):
        return sqrt(6) / 12 * side
    elif (polyhedron == 'cube'):
        return side / 2
    elif (polyhedron == 'octahedron'):
        return sqrt(6) / 6 * side
    elif (polyhedron == 'dodecahedron'):
        return sqrt((25 + 11 * sqrt(5)) / 10) / 2 * side
    elif (polyhedron == 'icosahedron'):
        return sqrt(3) * (3 + sqrt(5)) / 12 * side
