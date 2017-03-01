import matrix
from math import sin, cos

def translate(m, a, b, c):
    mat = matrix.id(4)
    mat[0][3] = a
    mat[1][3] = b
    mat[2][3] = c
    return matrix.multiply(mat, m)


def scale(m, a, b, c):
    mat = matrix.id(4)
    mat[0][0] = a
    mat[1][1] = b
    mat[2][2] = c
    return matrix.multiply(mat, m)


def relativeScale(m, oa, ob, oc, sa, sb, sc):
    return translate(scale(translate(m, -oa, -ob, -oc), sa, sb, sc), oa, ob, oc)


X_AX = 0
Y_AX = 1
Z_AX = 2
def rotate(m, t, axis):
    if axis == Z_AX:
        mat = matrix.id(4)
        c = cos(t)
        s = sin(t)
        mat[0][0] = c
        mat[0][1] = -s
        mat[1][0] = s
        mat[1][1] = c
        return matrix.multiply(mat, m)
        
