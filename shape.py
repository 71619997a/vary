from edgeMtx import edgemtx, addToEdgeMtx, addTriangle, addPoint, addEdge, addCircle, drawEdges
import math
import transform

def genBoxPoints(x, y, z, w, h, d):
    # how to preserve orientation for dummies
    if w < 0:
        return genBoxPoints(x + w, y, z, -w, h, d)
    if h < 0:
        return genBoxPoints(x, y + h, z, w, -h, d)
    if d < 0:
        return genBoxPoints(x, y, z + d, w, h, -d)
    pts = []
    for i in range(8):
        xcor = x + (i >> 2) * w
        ycor = y - (i >> 1) % 2 * h
        zcor = z - d + i % 2 * d
        pts.append((xcor, ycor, zcor))
    return pts

def genBoxTris():
    return [(0,5,1),(0,4,5),(2,3,7),(2,7,6),(0,2,6),(0,6,4),(1,7,3),(1,5,7),(0,1,3),(0,3,2),(4,7,5),(4,6,7)]

def addBox(m, x, y, z, w, h, d):
    pts = genBoxPoints(x, y, z, w, h, d)
    for a,b,c in genBoxTris():
        addTriangle(m, *pts[a]+pts[b]+pts[c])

def addSphere(m, x, y, z, r, step=0.02):
    pts = genSpherePoints(x, y, z, r, step)
    for a,b,c in genSphereTris(step):
        addTriangle(m, *pts[a]+pts[b]+pts[c])

def genSphereTris(step=0.02):
    tris = []
    steps = int(math.ceil(1 / step))
    for i in range(steps):
        for j in range(steps - 1):
            iNext = (i + 1) % steps
            jNext = (j + 1) % steps
            cor = i * steps + j
            leftcor = i * steps + jNext
            topcor = iNext * steps + j
            diagcor = iNext * steps + jNext
            tris.append((cor, diagcor, leftcor))
            tris.append((cor, topcor, diagcor))
    return tris

def genSpherePoints(x, y, z, r, step=0.02):
    pts = []
    steps = int(math.ceil(1 / step))
    theps = 0
    thep = 2 * math.pi / steps
    phep = math.pi / (steps - 1)
    for theta in range(steps):
        pheps = 0
        for phi in range(steps):
            xcor = x + r * math.sin(pheps) * math.cos(theps)
            ycor = y + r * math.sin(pheps) * math.sin(theps)
            zcor = z + r * math.cos(pheps)
            pts.append((xcor, ycor, zcor))
            pheps += phep
        theps += thep
    return pts

def addTorus(m, x, y, z, r, R, mainStep=0.02, ringStep=0.05):
    pts = genTorusPoints(x, y, z, r, R, mainStep, ringStep)
    for a,b,c in genTorusTris(mainStep, ringStep):
        addTriangle(m, *pts[a]+pts[b]+pts[c])

def genTorusTris(mainStep=0.02, ringStep=0.05):
    steps = int(math.ceil(1 / mainStep))
    rsteps = int(math.ceil(1 / ringStep))
    tris = []
    for c in range(steps):
        for r in range(rsteps):
            cNext = (c + 1) % steps
            rNext = (r + 1) % rsteps
            cor = c * rsteps + r
            leftcor = c * rsteps + rNext
            topcor = cNext * rsteps + r
            diagcor = cNext * rsteps + rNext
            tris.append((cor, diagcor, leftcor))
            tris.append((cor, topcor, diagcor))
    return tris

            

def genTorusPoints(x, y, z, r, R, mainStep=0.02, ringStep=0.05):
    pts = []
    steps = int(math.ceil(1 / mainStep))
    rsteps = int(math.ceil(1 / ringStep))
    om = 2 * math.pi / steps
    im = 2 * math.pi / rsteps
    for theta in range(steps):
        for phi in range(rsteps):
            xcor = math.cos(theta * om) * (r * math.cos(phi * im) + R) + x
            ycor = r * math.sin(phi * im) + y
            zcor = -math.sin(theta * om) * (r * math.cos(phi * im) + R) + z
            pts.append((xcor, ycor, zcor))
    return pts

        
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
