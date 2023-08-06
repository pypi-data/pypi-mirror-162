# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 10:12:18 2022

@author: ggil
"""


def dual(polyhedron):
    if (polyhedron == 'tetrahedron'):
        return 'tetrahedron'
    elif (polyhedron == 'cube'):
        return 'octahedron'
    elif (polyhedron == 'octahedron'):
        return 'cube'
    elif (polyhedron == 'dodecahedron'):
        return 'icosahedron'
    elif (polyhedron == 'icosahedron'):
        return 'dodecahedron'
