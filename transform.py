import matrix
from math import sin, cos

class TransMatrix(object):
    def __init__(self, lst=-1):
        self.lst = matrix.id(4)
        if lst != -1:
            self.lst = lst

    __getitem__ = self.lst.__getitem__
    __setitem__ = self.lst.__setitem__
    __missing__ = self.lst.__missing__

    def __mul__(self, mat):
        if isinstance(mat, TransMatrix):
            return TransMatrix(matrix.multiply(self.lst, mat.lst))
        else:
            return matrix.multiply(self.lst, mat)
            
    

def T(a, b, c):
    mat = TransMatrix()
    mat[0][3] = a
    mat[1][3] = b
    mat[2][3] = c
    return mat


def S(a, b, c):
    mat = TransMatrix()
    mat[0][0] = a
    mat[1][1] = b
    mat[2][2] = c
    return mat


def relativeScale(oa, ob, oc, sa, sb, sc):
    return T(oa, ob, oc)*S(sa, sb, sc)*T(-oa, -ob, -oc)

X_AX = 0
Y_AX = 1
Z_AX = 2
def R(t, axis):
    mat = TransMatrix()
    c = cos(t)
    s = sin(t)
    if axis == Z_AX:
        mat[0][0] = c
        mat[0][1] = -s
        mat[1][0] = s
        mat[1][1] = c
    if axis == X_AX:
        mat[1][1] = c
        mat[1][2] = -s
        mat[2][1] = s
        mat[2][2] = c
    if axis == Y_AX:
        mat[0][0] = c
        mat[0][2] = s
        mat[2][0] = -s
        mat[2][2] = c
    return mat
        
