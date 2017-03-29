from edgeMtx import edgemtx, addEdgeMtxs, addTriangle, addPoint, addEdge, addCircle
import math
import transform

def addBoxPoints(m, x, y, z, w, h, d):
    for i in range(8):
        xcor = x + (i >> 2) * w
        ycor = y + (i >> 1) % 2 * w
        zcor = z + i % 2 * w
        addEdge(m, xcor, ycor, zcor, xcor, ycor, zcor)
    return m

def addSpherePoints(m, x, y, z, r, step=0.05):
    steps = int(math.ceil(1 / steps))
    for theta in range(steps):
        for phi in range(steps):
            xcor = x + r * math.sin(phi * math.pi / steps) * math.cos(theta * 2 * math.pi / steps)
            ycor = y + r * math.sin(phi * math.pi / steps) * math.sin(theta * 2 * math.pi / steps)
            zcor = z + r * math.cos(phi * math.pi / steps)
            addEdge(m, xcor, ycor, zcor, xcor, ycor, zcor)
    return m

def addTorusPoints(m, x, y, z, r, R, mainStep=0.05, ringStep=0.1):
    steps = int(math.ceil(1 / mainStep))
    mCircle = edgemtx()
    addPoint(mCircle, r, 0, 0)
    addCircle(mCircle, 0, 0, 0, r, ringStep)
    for theta in range(steps):
        yOuter = y + R * math.sin(theta * 360. / steps)
        zOuter = z + R * math.cos(theta * 360. / steps)
        movedCircle = transform.T(x, yOuter, zOuter) * transform.R('y', theta * 360. / steps) * mCircle
        addEdgeMtxs(m, movedCircle)
    return m
def box(x,y,z,w,h,d):
    p = (x,y,z)
    dim = (w,h,d)
    m = edgemtx()
    n = edgemtx()
    for i in xrange(3):
        j = (i + 1) % 3
        ai = [0,0,0]
        aj = [0,0,0]
        ak = [0,0,0]
        ai[i] = dim[i]
        aj[j] = dim[j]
        for k in xrange(2):
            addTriangle(m, x+ak[0], y+ak[1], z+ak[2], x+ai[0]+ak[0], y+ai[1]+ak[1], z+ai[2]+ak[2], x+aj[0]+ak[0], y+aj[1]+ak[1], z+aj[2]+ak[2])
            addTriangle(m, x+ai[0]+ak[0], y+ai[1]+ak[1], z+ai[2]+ak[2], x+aj[0]+ak[0], y+aj[1]+ak[1], z+aj[2]+ak[2], x+ai[0]+aj[0]+ak[0], y+ai[1]+aj[1]+ak[1], z+ai[2]+aj[2]+ak[2])
            norm = [0,0,0]
            dir = 1 - k * 2
            norm[3 - i - j] = dir
            addEdge(n, *norm*2)
            ak[3 - i - j] += dim[3 - i - j]
    return m, n
            
