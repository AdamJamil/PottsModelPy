'''
dumm.py

This file exists just to isolate functions and see them more clearly in
the snakeviz trace
'''

import exprs

def do_cast_up(a, b, c=False):
    return exprs.cast_up(a, b, c)
