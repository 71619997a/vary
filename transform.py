import matrix
import math
from common import *

sin = lambda t: math.sin(t * math.pi / 180)
cos = lambda t: math.cos(t * math.pi / 180)

class TransMatrix(object):
    def __init__(self, lst=-1):
        self.lst = matrix.id(4)
        if lst != -1:
            self.lst = lst

    def __getitem__(self, i):
        return self.lst[i]
    
    def __setitem__(self, i, v):
        self.lst[i] = v

    def __str__(self):
        return matrix.toStr(self.lst)

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


def R(axis, t):
    mat = TransMatrix()
    c = cos(t)
    s = sin(t)
    if axis == 'z':
        mat[0][0] = c
        mat[0][1] = -s
        mat[1][0] = s
        mat[1][1] = c
    if axis == 'x':
        mat[1][1] = c
        mat[1][2] = -s
        mat[2][1] = s
        mat[2][2] = c
    if axis == 'y':
        mat[0][0] = c
        mat[0][2] = s
        mat[2][0] = -s
        mat[2][2] = c
    return mat


def C(cam):
    m = R('z', -cam.dz) * R('y', -cam.dy) * R('z', -cam.dz) * T(-cam.x, -cam.y, -cam.z)
    dt = TransMatrix()
    dt[3][3] = 0
    dt[3][2] = 1. / cam.vz
    dt[1][2] = -1.*cam.vy / cam.vz
    dt[0][2] = -1.*cam.vx / cam.vz
    return dt * m


def projected(m, cam):
    mp = C(cam) * m
    for i in xrange(len(mp[0])):
        for j in xrange(4):
            mp[j][i] /= mp[3][i]
    print mp
    return mp


def iparse(inp):
    return [float(i.strip()) for i in inp.split(' ')]

if __name__ == '__main__':  # parser
    from edgeMtx import edgemtx, addEdge, drawEdges, addBezier, addHermite, addCircle
    from base import Image
    edges = edgemtx()
    trans = TransMatrix()
    frc = 0
    cam = Camera(250, 250, 700, 90, 0, 0, 0, 0, 250)
    while(True):
        try:
            inp = raw_input('')
        except EOFError:  # script file
            break
        if inp == 'line':
            inp = raw_input('')
            addEdge(edges, *iparse(inp))
        elif inp == 'ident':
            trans = TransMatrix()
        elif inp == 'scale':
            inp = raw_input('')
            trans = S(*iparse(inp)) * trans
        elif inp == 'move':
            inp = raw_input('')
            trans = T(*iparse(inp)) * trans
        elif inp == 'rotate':
            inp = raw_input('')
            axis, t = (i.strip() for i in inp.split(' '))
            trans = R(axis.lower(), float(t)) * trans
        elif inp == 'apply':
            print edges
            edges = trans * edges
            print edges
        elif inp == 'display':
            img = Image(500, 500)
            drawEdges(projected(edges, cam), img)
            img.flipUD().display()
        elif inp == 'save':
            inp = raw_input('').strip()
            img = Image(500, 500)
            drawEdges(edges, img)
            if inp[-4:] == '.ppm':
                img.flipUD().savePpm(inp)
            else:
                img.saveAs(inp)
        elif inp == 'saveframe':
            inp = raw_input('').strip()
            img = Image(500, 500)
            drawEdges(edges, img)
            img.flipUD().savePpm('%s%d.ppm' % (inp, frc))
            frc += 1
        elif inp == 'circle':
            inp = raw_input('').strip()
            addCircle(*[edges]+iparse(inp)+[.01])
        elif inp == 'bezier':
            inp = raw_input('').strip()
            addBezier(*[edges]+iparse(inp)+[.01])
        elif inp == 'hermite':
            inp = raw_input('').strip()
            addHermite(*[edges]+iparse(inp)+[.01])
