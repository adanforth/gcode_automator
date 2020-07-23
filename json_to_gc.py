import json
from stl_test import *
import sys



vectors = read_json('vectors.json')
original_stdout = sys.stdout


origin_x = 0.000
origin_y = 0.000


def vector_json_print(vectors):
    start = vectors[0]
    prev_x = start[0][0] - origin_x
    prev_y = start[0][1] - origin_y
    print("G0" + " X{:.3f} Y{:.3f} Z0.300".format(start[0][0] - origin_x, start[0][1] - origin_y))
    print("G1 Z-.100 F30.000")
    for vector in vectors:
        if prev_x == vector[1][0] - origin_x:
            print("G1" + " Y{:.3f}".format(vector[1][1] - origin_y))
        elif prev_y == vector[1][1] - origin_y:
            print("G1" + " X{:.3f}".format(vector[1][0] - origin_x,)) 
        else:
            print("G1" + " X{:.3f} Y{:.3f}".format(vector[1][0] - origin_x, vector[1][1] - origin_y))
        prev_x = vector[1][0] - origin_x
        prev_y = vector[1][1] - origin_y




# work out tool changing
with open('test.gc', 'w') as f:
    sys.stdout = f
    print("%")
    print("S15000")
    print("G90 G17 G40 G70")
    print("M3")
    print("G0 Z4.000 F150")
    print("G0 X0.000 Y0.000 F1200.000")
    print("T6 M6")
    for shape in vectors:
        vector_json_print(vectors[shape])
        print("G0 Z0.300")
    print("G0 Z0.300")
    print("G0 X0.000 Y0.000 Z4.000")
    print("G0 Z4.000")
    print("G0 X0 Y0")
    print("M5")
    print("M30")
    print("M2")
    print("%")
    sys.stdout = original_stdout

