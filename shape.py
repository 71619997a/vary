from edgeMtx import edgemtx, addToEdgeMtx, addTriangle, addPoint, addEdge, addCircle
import math
import transform

def addBoxPoints(m, x, y, z, w, h, d):
    for i in range(8):
        xcor = x + (i >> 2) * w
        ycor = y + (i >> 1) % 2 * w
        zcor = z + i % 2 * w
        addEdge(m, xcor, ycor, zcor, xcor, ycor, zcor)
    return m

def addSpherePoints(m, x, y, z, r, step=0.02):
    steps = int(math.ceil(1 / step))
    for theta in range(steps):
        for phi in range(steps):
            xcor = x + r * math.sin(phi * math.pi / steps) * math.cos(theta * 2 * math.pi / steps)
            ycor = y + r * math.sin(phi * math.pi / steps) * math.sin(theta * 2 * math.pi / steps)
            zcor = z + r * math.cos(phi * math.pi / steps)
            addEdge(m, xcor, ycor, zcor, xcor, ycor, zcor)
    return m

def addTorusPoints(m, x, y, z, r, R, mainStep=0.02, ringStep=0.05):
    steps = int(math.ceil(1 / mainStep))
    mCircle = edgemtx()
    addPoint(mCircle, r, 0, 0)
    addCircle(mCircle, 0, 0, 0, r, ringStep)
    addPoint(mCircle, mCircle[0][-1], mCircle[1][-1], 0)
    for theta in range(steps):
        xOuter = x + R * math.cos(theta * 2 * math.pi / steps)
        zOuter = z + R * math.sin(theta * 2 * math.pi / steps)
        movedCircle = transform.T(xOuter, y, zOuter) * transform.R('y', -theta * 360. / steps) * mCircle
        addToEdgeMtx(m, movedCircle)
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
            
