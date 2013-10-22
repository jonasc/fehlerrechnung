#!/usr/bin/env python3
# -*- coding: utf8 -*-

from fehlerrechnung import *

hs = [
    dict(value='2', relerror='0.01'),
    dict(value='4', relerror='0.01'),
    dict(value='6', relerror='0.01'),
    dict(value='8', relerror='0.01'),
    dict(value='10', relerror='0.01')
]

ts = [
    dict(value='0.62', error='0.02'),
    dict(value='0.91', error='0.02'),
    dict(value='1.12', error='0.02'),
    dict(value='1.20', error='0.02'),
    dict(value='1.44', error='0.02')
]

for i in range(len(hs)):
    h = Value(**hs[i])
    t = Value(**ts[i])
    g = 2*h/t**2
    print(h, t)
    print(g)
    print()
