from edgeMtx import edgemtx, addToEdgeMtx, addTriangle, addPoint, addEdge, addCircle, drawEdges
import math
import transform

def genBoxPoints(x, y, z, w, h, d):
    pts = []
    for i in range(8):
        xcor = x + (i >> 2) * w
        ycor = y + (i >> 1) % 2 * w
        zcor = z + i % 2 * w
        pts.append([xcor, ycor, zcor])
    return pts

def addBox(m, x, y, z, w, h, d):
    pts = genBoxPoints(x, y, z, w, h, d)
    addTriangle(m, *pts[0]+pts[5]+pts[1])
    addTriangle(m, *pts[0]+pts[4]+pts[5])
    addTriangle(m, *pts[2]+pts[3]+pts[7])
    addTriangle(m, *pts[2]+pts[7]+pts[6])
    
    addTriangle(m, *pts[0]+pts[2]+pts[6])
    addTriangle(m, *pts[0]+pts[6]+pts[4])
    addTriangle(m, *pts[1]+pts[7]+pts[3])
    addTriangle(m, *pts[1]+pts[5]+pts[7])

    addTriangle(m, *pts[0]+pts[1]+pts[3])
    addTriangle(m, *pts[0]+pts[3]+pts[2])
    addTriangle(m, *pts[4]+pts[7]+pts[5])
    addTriangle(m, *pts[4]+pts[6]+pts[7])


def addSphere(m, x, y, z, r, step=0.02):
    steps = int(math.ceil(1 / step))
    pts = genSpherePoints(x, y, z, r, step)
    for i in range(steps):
        for j in range(steps):
            iNext = (i + 1) % steps
            jNext = (j + 1) % steps
            cor = i * steps + j
            leftcor = i * steps + jNext
            topcor = iNext * steps + j
            diagcor = iNext * steps + jNext
            addTriangle(m, *pts[cor] + pts[diagcor] + pts[leftcor])
            addTriangle(m, *pts[cor] + pts[topcor] + pts[diagcor])
    return m
    

def genSpherePoints(x, y, z, r, step=0.02):
    pts = []
    steps = int(math.ceil(1 / step))
    for theta in range(steps):
        for phi in range(steps):
            xcor = x + r * math.sin(phi * math.pi / steps) * math.cos(theta * 2 * math.pi / steps)
            ycor = y + r * math.sin(phi * math.pi / steps) * math.sin(theta * 2 * math.pi / steps)
            zcor = z + r * math.cos(phi * math.pi / steps)
            pts.append([xcor, ycor, zcor])
    return pts

def genTorusPoints(m, x, y, z, r, R, mainStep=0.02, ringStep=0.05):
    pts = []
    steps = int(math.ceil(1 / mainStep))
    rsteps = int(math.ceil(1 / ringStep))
    om = 2 * math.pi / steps
    im = 2 * math.pi / rsteps
    for theta in range(steps):
        for phi in range(rsteps):
            xcor = math.cos(theta * om) * (r * math.cos(phi * im) + R) + x
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
            
if __name__ == '__main__':
    from base import Image
    import transform
    cube = edgemtx()
    addBoxPoints(cube, 125, 125, -125, 250, 250, 250)
    m = edgemtx()
    xTrans = transform.T(250, 250, 0) * transform.R('x', 18) * transform.T(-250, -250, 0)
    yTrans = transform.T(250, 250, 0) * transform.R('y', 18) * transform.T(-250, -250, 0)
    for d in 'xyz':
        trans = transform.T(250, 250, 0) * transform.R(d, 15) * transform.T(-250, -250, 0)
        for i in range(24):
            addToEdgeMtx(m, cube)
            cube = trans * cube
        cube = m
        m = edgemtx()
    cube = transform.T(250, 250, 0) * transform.R('y', 49) * transform.R('x', 67) * transform.R('z', 23) * transform.T(-250, -250, 0) * cube
    img = Image(500, 500)
    drawEdges(cube, img)
    img.display()
    img.saveAs('badsphere.png')
