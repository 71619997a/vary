import matrix
import math
from common import *
import render
sin = lambda t: math.sin(t * math.pi / 180)
cos = lambda t: math.cos(t * math.pi / 180)
EDGE = 2
POLY = 3

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

    def clone(self):
        newlst = [row[:] for row in self.lst]
        return TransMatrix(newlst)
    

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

def C2(cam, near, far):
    m = R('z', -cam.dz) * R('y', -cam.dy) * R('z', -cam.dz) * T(-cam.x, -cam.y, -cam.z)
    dt = TransMatrix()
    dt[0][0] = cam.vz
    dt[1][1] = cam.vz
    dt[3][2] = -1
    dt[3][3] = 0
    dt[2][2] = -1.*far / (far - near)
    dt[3][2] = -1.*far * near / (far - near)
    print dt * m
    return dt * m
def projected(m, cam):
    mp = C(cam) * m
    for i in xrange(len(mp[0])):
        for j in xrange(4):
            mp[j][i] /= mp[3][i]
    print mp
    return mp


def C3(r,t,n,f):
    mat = TransMatrix()
    mat[0][0] = 1.*n/r
    mat[1][1] = 1.*n/t
    mat[2][2] = -1.*(f+n)/(f-n)
    mat[2][3] = -2.*(f*n)/(f-n)
    mat[3][3] = 0
    mat[3][2] = -1
    return mat

def C3invT(r, t, n, f):
    mat = TransMatrix()
    mat[0][0] = 1.*r/n
    mat[1][1] = 1.*t/n
    mat[2][2] = 0
    mat[2][3] = 1.*(n-f)/(2*f*n)
    mat[3][2] = -1
    mat[3][3] = 1.*(f+n)/(2*f*n)
    return mat

'''
A = 
n/r 0   0   0
0 n/t   0   0
0   0 -(f+n)/(f-n) -2fn/(f-n)
0   0  -1   0
A'A = I
A' = 
r/n 0   ?
0 t/n   ?
0   0   ?   
0   0   ?   ?
'''


def iparse(inp):
    return [float(i.strip()) for i in inp.split(' ')]


def drawObjects(objects, img):
    for type, mtx in objects:
        if type == EDGE:
            drawEdges(mtx, img)
        elif type == POLY:
            drawTriangles(mtx, img, wireframe=True)


def cross3d(v1x, v1y, v1z, v2x, v2y, v2z):
    return [v1y*v2z - v1z*v2y, v1z*v2x - v1x*v2z, v1x*v2y - v1y*v2x]
            

def getPointsFromTriangles(m):  # assumes m is a poly mtx
    print m
    for i in range(0, len(m[0]), 3):
        v12x, v12y, v12z = tuple(m[n][i] - m[n][i+1] for n in range(3))
        v23x, v23y, v23z = tuple(m[n][i+1] - m[n][i+2] for n in range(3))
        v13x, v13y, v13z = tuple(m[n][i] - m[n][i+2] for n in range(3))
        try:
            n1 = normalizeList(cross3d(-v12x, -v12y, -v12z, v13x, v13y, v13z))
            n2 = normalizeList(cross3d(v12x, v12y, v12z, v23x, v23y, v23z))
            n3 = normalizeList(cross3d(v23x, v23y, v23z, -v13x, -v13y, -v13z))
        except ZeroDivisionError:
            continue
        yield (Point(m[0][i], m[1][i], m[2][i], n1[0], n1[1], n1[2], 0, 0), 
               Point(m[0][i+1], m[1][i+1], m[2][i+1], n2[0], n2[1], n2[2], 0, 0), 
               Point(m[0][i+2], m[1][i+2], m[2][i+2], n3[0], n3[1], n3[2], 0, 0))

            
dullWhite = Material(Texture(False, (255, 255, 255)), Texture(False, (255, 255, 255)), Texture(False, (80, 80, 80)), 4)
niceLights = [
    Light(750, -3000, 750, (100, 95, 90), (200, 180, 160), (255, 230, 210)),  # sun at just past noon
    #Light(0, 0, 200, (0, 20, 80), (30, 100, 200), (50, 150, 255))  # cyan light to the left-top
    ]

def depthShader(x, y, z, nx, ny, nz, *_):
    return [0, 0, min(255, max(0, int(z + 128)))]


def drawObjectsNicely(objects, img, mat=dullWhite, V=(250, 250, 600), lights=niceLights, shader=depthShader):
    zbuf = [[None] * 500 for _ in xrange(500)]
    for type, mtx in objects:
        if type == EDGE:
            drawEdges(mtx, img)
        elif type == POLY:
            for pts in getPointsFromTriangles(mtx):
                img.setPixels(renderTriangle(*pts + (mat,) + V + (lights, {}, zbuf)))
            

if __name__ == '__main__':  # parser
    from edgeMtx import edgemtx, addEdge, addTriangle, drawEdges, addBezier, addHermite, addCircle, drawTriangles
    from base import Image
    from render import renderTriangle, phongShader
    import shape
    cstack = [TransMatrix()]
    frc = 0
    cam = Camera(250, 250, 700, 90, 0, 0, -250, -250, 250)
    img = Image(500, 500)
    objects = []
    while(True):
        try:
            inp = raw_input('').strip()
        except EOFError:  # script file
            break
        if inp == 'line':
            inp = raw_input('')
            edges = edgemtx()
            addEdge(edges, *iparse(inp))
            edges = cstack[-1] * edges
            objects.append((EDGE, edges))
            #drawEdges(cstack[-1] * edges, img)
        elif inp == 'ident':
            cstack[-1] = TransMatrix()
        elif inp == 'scale':
            inp = raw_input('')
            cstack[-1] *= S(*iparse(inp))
        elif inp == 'move':
            inp = raw_input('')
            cstack[-1] *= T(*iparse(inp))
        elif inp == 'rotate':
            inp = raw_input('')
            axis, t = (i.strip() for i in inp.split(' '))
            cstack[-1] *= R(axis.lower(), float(t))
        elif inp == 'display':
            drawObjectsNicely(objects, img)
            img.flipUD().display()
        elif inp == 'save':
            drawObjectsNicely(objects, img)
            inp = raw_input('').strip()
            if inp[-4:] == '.ppm':
                img.flipUD().savePpm(inp)
            else:
                img.flipUD().saveAs(inp)
        elif inp == 'saveframe':
            drawObjectsNicely(objects, img)
            inp = raw_input('').strip()
            img.flipUD().savePpm('%s%d.ppm' % (inp, frc))
            frc += 1
        elif inp == 'circle':
            inp = raw_input('').strip()
            edges = edgemtx()
            addCircle(*[edges]+iparse(inp)+[.01])
            edges = cstack[-1] * edges
            objects.append((EDGE, edges))
            #drawEdges(cstack[-1] * edges, img)
        elif inp == 'bezier':
            inp = raw_input('').strip()
            edges = edgemtx()
            addBezier(*[edges]+iparse(inp)+[.01])
            edges = cstack[-1] * edges
            objects.append((EDGE, edges))
            #drawEdges(cstack[-1] * edges, img)
        elif inp == 'hermite':
            inp = raw_input('').strip()
            edges = edgemtx()
            addHermite(*[edges]+iparse(inp)+[.01])
            edges = cstack[-1] * edges
            objects.append((EDGE, edges))
            #drawEdges(cstack[-1] * edges, img)
        elif inp == 'clear':
            img = Image(500, 500)
        elif inp == 'clearstack':
            cstack = [TransMatrix()]
        elif inp == 'box':
            inp = raw_input('').strip()
            polys = edgemtx()
            coos = iparse(inp)
            shape.addBox(*[polys] + coos)
            polys = cstack[-1] * polys
            objects.append((POLY, polys))
            #drawTriangles(cstack[-1] * polys, img, wireframe=True)
        elif inp == 'sphere':
            inp = raw_input('').strip()
            polys = edgemtx()
            shape.addSphere(*[polys] + iparse(inp) + [.03])
            polys = cstack[-1] * polys
            objects.append((POLY, polys))
            #drawTriangles(cstack[-1] * polys, img, wireframe=True)
        elif inp == 'torus':
            inp = raw_input('').strip()
            polys = edgemtx()
            shape.addTorus(*[polys] + iparse(inp) + [.05, .05])
            polys = cstack[-1] * polys
            objects.append((POLY, polys))
            #drawTriangles(cstack[-1] * polys, img, wireframe=True)
        elif inp == 'push':
            print 'pushed'
            cstack.append(cstack[-1].clone())
            for i in cstack:
                print i
        elif inp == 'pop':
            print 'popped'
            cstack.pop()
            for i in cstack:
                print i
        elif len(inp) < 1 or inp[0] != '#':
            print len(inp)
            print repr(inp)
            print inp, 'not valid'
