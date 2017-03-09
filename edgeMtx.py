from base import Image
from line import line
from triangle import triangle
import matrix

def edgemtx():
    return [[],[],[],[]]

def addEdgeMtxs(m1, m2):
    m = [m1[i] + m2[i] for i in range(len(m1))]
    return m

def addPoint(m, x, y, z):
    m[0].append(x)
    m[1].append(y)
    m[2].append(z)
    m[3].append(1.)

def addEdge(m, x0, y0, z0, x1, y1, z1):
    addPoint(m, x0, y0, z0)
    addPoint(m, x1, y1, z1)

def addEdgesFromParam(m, fx, fy, fz, step):
    t = step
    lastpt = (fx(0), fy(0), fz(0))
    while t <= 1.001:
        pt = (fx(t), fy(t), fz(t))
        addEdge(m, *lastpt + pt)
        lastpt = pt
        t += step

def addTriangle(m, *args):
    assert len(args) == 9
    for i in range(0, 9, 3):
        addPoint(m, *args[i : i+3])

def drawEdges(m, image, color=(255, 0, 0)):  # draws the edges to an image
    for i in range(0, len(m[0]) - 1, 2):
        lin = line(m[0][i], m[1][i], m[0][i + 1], m[1][i + 1])
        coloredlin = [xy + (color,) for xy in lin]
        image.setPixels(coloredlin)

def drawTriangles(m, image, color=(255, 0, 0), bordercol=(255,255,255)):
    triangles = []
    for i in range(0, len(m[0]) - 2, 3):
        triangles.append([m[0][i], m[1][i], m[0][i + 1], m[1][i + 1], m[0][i + 2], m[1][i + 2], sum(m[2][i : i+3])])
    ordTris = sorted(triangles, key=lambda l: l[6])
    for t in ordTris:
        tri = triangle(*t[:6])
        border = line(*t[:4])
        border.extend(line(*t[2:6]))
        border.extend(line(*t[:2] + t[4:6]))
        coloredtri = [xy + (color,) for xy in tri] + [xy + (bordercol,) for xy in border]
        image.setPixels(coloredtri)

def drawColoredTriangles(ms, image, bordercol=(255, 255, 255)):
    mcols = edgemtx() + [[]]
    for m, col in ms:
        mcol = m + [[col] * len(m[0])]
        mcols = addEdgeMtxs(mcols, mcol)
    triangles = []
    for i in range(0, len(mcols[0]) - 2, 3):
        # print i, mcols[0][i], mcols[1][i], mcols[0][i + 1], mcols[1][i + 1], mcols[0][i + 2], mcols[1][i + 2], sum(mcols[2][i : i+3]), mcols[4][i]
        triangles.append([mcols[0][i], mcols[1][i], mcols[0][i + 1], mcols[1][i + 1], mcols[0][i + 2], mcols[1][i + 2], sum(mcols[2][i : i+3]), mcols[4][i]])
    ordTris = sorted(triangles, key=lambda l: l[6])
    for t in ordTris:
        tri = triangle(*t[:6])
        border = line(*t[:4])
        border.extend(line(*t[2:6]))
        border.extend(line(*t[:2] + t[4:6]))
        coloredtri = [xy + (t[7],) for xy in tri] + [xy + (bordercol,) for xy in border]
        image.setPixels(coloredtri)

def mtxTest1():
    m1 = [[2, 2, 3], [3, 2, 2]]
    m2 = [[1, 5], [6.5, 4], [1, -0.7]]
    m3 = [[1, 2, 3, 1], [5, 2, -1, 3], [-1, -5, 3, 6], [2, 4, -7, 2]]
    k1 = 2.5
    k2 = 3.5
    id3 = matrix.id(3)
    id2 = matrix.id(2)
    print 'identity 3x3'
    print matrix.toStr(id3)
    print 'identity 2x2'
    print matrix.toStr(id2)
    print 'm1 2x3'
    print matrix.toStr(m1)
    print 'sanity checks: m1 * id3 = m1, id2 * m1 = m1'
    m1again = matrix.multiply(m1, id3)
    m1evenmore = matrix.multiply(id2, m1)
    print matrix.toStr(m1again)
    print matrix.toStr(m1evenmore)
    print 'testing size mismatch id3 * m1:'
    try:
        matrix.multiply(id3, m1)
    except ArithmeticError:
        print 'it errored, that\'s good'
    print 'm2 3x2'
    print matrix.toStr(m2)
    m12 = matrix.multiply(m1, m2)
    print 'm1 * m2, should be a 2x2'
    print matrix.toStr(m12)
    m21 = matrix.multiply(m2, m1)
    print 'm2 * m1, should be a 3x3'
    print matrix.toStr(m21)
    print '10 * (m2 * m1)'
    print matrix.toStr(matrix.multiply(10, m21))
    print '(m2 * m1) * 10'
    print matrix.toStr(matrix.multiply(m21, 10))
    print '10 * 10'
    print matrix.multiply(10, 10)
    print 'Adding edge (1, 1, 1), (2, 3, 2.5)'
    m = edgemtx()
    addEdge(m, 1, 1, 1, 2, 3, 2.5)
    print matrix.toStr(m)
    print 'm3'
    print matrix.toStr(m3)
    print 'Transforming edge matrix'
    print matrix.toStr(matrix.multiply(m3, m))
    
    img = Image(500, 500)
    for loc in range(0, 500, 4):
        edges = edgemtx()
        addEdge(edges, 125, loc, 100, loc + 1, 375, 100)
        addEdge(edges, loc + 1, 375, 100, 375, 500 - loc - 2, 100)
        addEdge(edges, 375, 500 - loc - 2, 100, 500 - loc - 3, 125, 100)
        addEdge(edges, 500 - loc - 3, 125, 100, 125, loc + 4, 100)
        drawEdges(edges, img, (255 - loc / 2, loc / 2, 127))  # crossfade r + g
    img.display()

def triangleTest1():
    tris = edgemtx()
    img = Image(500, 500)
    for x in range(0, 500, 50):
        for y in range(0, 500, 50):
            addTriangle(tris, x, y, 0, x + 25, y, 0, 250, 250, 250)
    drawTriangles(tris, img)
    img.display()

def circleTest1():
    import math
    m = edgemtx()
    addEdgesFromParam(m, lambda t: 250 + 100 * math.cos(t * 2 * math.pi), lambda t: 250 + 100 * math.sin(t * 2 * math.pi), lambda t: 0, 0.01)
    img = Image(500, 500)
    drawEdges(m, img)
    img.display()

def circleTest2():
    m = edgemtx()
    for theta in range(36):
        costheta = math.cos(theta)
        def fx(t):
            return 250 + 100 * math.cos(t * 2 * math.pi) * costheta
        
if __name__ == '__main__':
    circleTest1()
