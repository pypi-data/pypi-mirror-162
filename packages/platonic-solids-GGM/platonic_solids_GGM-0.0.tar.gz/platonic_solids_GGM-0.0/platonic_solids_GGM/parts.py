# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 10:28:24 2022

@author: ggil
"""


def faces(polyhedron):
    if (polyhedron == 'tetrahedron'):
        return 3
    elif (polyhedron == 'cube'):
        return 6
    elif (polyhedron == 'octahedron'):
        return 8
    elif (polyhedron == 'dodecahedron'):
        return 12
    elif (polyhedron == 'icosahedron'):
        return 20


def edges(polyhedron):
    if (polyhedron == 'tetrahedron'):
        return 6
    elif (polyhedron == 'cube'):
        return 12
    elif (polyhedron == 'octahedron'):
        return 12
    elif (polyhedron == 'dodecahedron'):
        return 30
    elif (polyhedron == 'icosahedron'):
        return 30


def vertex(polyhedron):
    if (polyhedron == 'tetrahedron'):
        return 3
    elif (polyhedron == 'cube'):
        return 8
    elif (polyhedron == 'octahedron'):
        return 6
    elif (polyhedron == 'dodecahedron'):
        return 20
    elif (polyhedron == 'icosahedron'):
        return 12
