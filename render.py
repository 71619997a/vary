from line import lineByY, line
import transform
from matrix import multiply
import matrix
from os import chdir
from multiprocessing import Pool
from png import Reader
from time import time
from base import Image
import obj
import edgeMtx
import math
from common import *
from triangle import triangle

def getBary(x,y,x1,y1,x2,y2,x3,y3,det):
    try:
        d1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / det
        d2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / det
        return d1, d2, 1-d1-d2
    except:
        return 1, 0, 0

def drawTexturedTri(x1, y1, x2, y2, x3, y3, tx1, ty1, tx2, ty2, tx3, ty3, mat): #1-6 vertices, 7-12 tcors, 13 material
    # TODO: rgb + bgcol -> mat, use mat to get shading stuff and use below code frag
    '''if 'ambtexture' in mat:
            rgbAmbient = getTexture(mat['ambtexture'], texcache)
        else:
            rgbAmbient = None
        if 'difftexture' in mat:
            rgbDiffuse = getTexture(mat['difftexture'], texcache)
        else:
            rgbDiffuse = None'''
    a = time()
    pts = []
    l = len(rgb)-1
    th = len(rgb) - 1
    tw = len(rgb[0]) / 4 - 1
    tri = triangle(x1,y1,x2,y2,x3,y3)
    det = float((y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3))
    for x, y in tri:
        d1,d2,d3=getBary(x, y, x1, y1, x2, y2, x3, y3, det)
        tcx = tx1*d1+tx2*d2+tx3*d3
        tcy = ty1*d1+ty2*d2+ty3*d3
        # print tc[0], tc[1]
        if 1>=tcx>=0 and 1>=tcy>=0:
            xcor = int(tcx*tw)*4
            ycor = int(tcy*th)
            if rgb[l-ycor][xcor + 3] == 255:
                shade = shader(d1,d2,d3,n1x,n1y,n2x,n2y,n3x,n3y,col,Ka,Kd,Ks)
                pts.append((x, y, rgb[l-ycor][xcor:xc    or+3]))
        else:
            pts.append((x, y, bgcol))
    return pts


def phongShader(x,y,z,nx,ny, nz,lights, vx,vy,vz,Ka, Kd, Ks,a):
    Vx, Vy, Vz = normalize(vx-x,vy-y,vz-z)
    c = [0,0,0]
    for l in lights:
        Lmx , Lmy, Lmz = normalize(l.x-x,l.y-y,l.z-z)
        Lmn = Lmx * nx + Lmy * ny + Lmz * nz
        Rmx = 2 * Lmn * nx - Lmx
        Rmy = 2 * Lmn * ny - Lmy
        Rmz = 2 * Lmn * nz - Lmz    
        diff = max(Lmn, 0)
        try:
            spec = max((Rmx*Vx+Rmy*Vy+Rmz*Vz), 0)**a
        except:
            spec = 1 
        for i in xrange(3):
            c[i] += Ka[i]*l.Ia[i] + Kd[i]*l.Id[i]*diff + Ks[i]*l.Is[i]*spec
    for i in xrange(3):
        c[i] = min(int(c[i]), 65535) / 256
    return c


def renderTriangle(p1, p2, p3, mat, vx, vy, vz, lights, texcache, zbuf, shader=phongShader):
    tri = triangle(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y)
    det = float((p2.y - p3.y) * (p1.x - p3.x) + (p3.x - p2.x) * (p1.y - p3.y))
    pts = []
    if mat.amb.type:
        ambtex = getTexture(mat.amb.texture, texcache)
        ambw = len(ambtex[0]) / 4
        ambh = len(ambtex)
    if mat.diff.type:
        difftex = getTexture(mat.diff.texture, texcache)
        diffw = len(difftex[0]) / 4
        diffh = len(difftex)
    if mat.spec.type:
        spectex = getTexture(mat.spec.texture, texcache)
        specw = len(spectex[0]) / 4
        spech = len(spectex)
    for x, y in tri:
        #print x,y
        if not (0 <= x < 500 and 0 <= y < 500):
            #print 'offscreen'
            continue
        d1, d2, d3 = getBary(x, y, p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, det)
        z = p1.z * d1 + p2.z * d2 + p3.z * d3
        if zbuf[y][x] >= z:
            continue
        #print 'not buffed'

        nz = p1.nz * d1 + p2.nz * d2 + p3.nz * d3
        if nz <= 0:
            continue
        zbuf[y][x] = z
        nx = p1.nx * d1 + p2.nx * d2 + p3.nx * d3
        ny = p1.ny * d1 + p2.ny * d2 + p3.ny * d3
        Ka = mat.amb.col
        Kd = mat.diff.col
        Ks = mat.spec.col
        if mat.amb.type or mat.diff.type or mat.spec.type:
            tcx = p1.tx*d1+p2.tx*d2+p3.tx*d3
            tcy = p1.ty*d1+p2.ty*d2+p3.ty*d3
            # print tc[0], tc[1]
            if 1>=tcx>=0 and 1>=tcy>=0:
                # TODO transparency checking
                if mat.amb.type:
                    xcor = int(tcx*ambw)*4
                    ycor = int(tcy*ambh)
                    Ka = ambtex[ambh-1-ycor][xcor : xcor + 3]
                if mat.diff.type:
                    xcor = int(tcx*diffw)*4
                    ycor = int(tcy*diffh)
                    Kd = difftex[diffh-1-ycor][xcor : xcor + 3]
                if mat.spec.type:
                    xcor = int(tcx*specw)*4
                    ycor = int(tcy*spech)
                    Ks = spectex[spech-1-ycor][xcor : xcor + 3]
        col = shader(x, y, z, nx, ny, nz, lights, vx, vy, vz, Ka, Kd, Ks, mat.exp)
        pts.append((x, y, col))
    return pts

def drawShadedTri(x1,y1,z1,x2,y2,z2,x3,y3,z3,nx1,ny1,nz1,nx2,ny2,nz2,nx3,ny3,nz3,lx,ly,lz,vx,vy,vz,Ia,Id,Is,Ka,Kd,Ks,a,zbuf):
    pts = []
    tri = triangle(x1,y1,x2,y2,x3,y3)
    det = float((y2 - y3) * (x1 - x3) + (x3 - x2) * (y1\
 - y3))
    for x, y in tri:
        #print y, x
        if not (0 <= x < 500 and 0 <= y < 500):
            continue
        d1,d2,d3=getBary(x, y, x1, y1, x2, y2, x3, y3, \
det)
        z = z1*d1+z2*d2+z3*d3
        if zbuf[y][x] >= z:
            #print 'buf pixf at %f for %f'%(z,zbuf[y][x])
            continue
        #else: print 'nein'
        #if zbuf[y][x] is not None:
        #    print 'do pixf at %f over %f'%(z,zbuf[y][x])
        #else:
        #    print 'new pixel', y, x
        zbuf[y][x] = z
        nz = nz1*d1+nz2*d2+nz3*d3
        # if nz < 0:
        #    pts.append((x,y,(0,0,0)))
        #    continue
        nx = nx1*d1+nx2*d2+nx3*d3
        ny = ny1*d1+ny2*d2+ny3*d3
        pts.append((x,y,shader(x,y,z,nx,ny, nz,lx,ly,lz, vx,vy,vz, Ia,Id,Is, Ka, Kd, Ks, a)))
    return pts

def normalize(*v):
    v = list(v)
    norm = math.sqrt(sum([i**2 for i in v]))
    for i in xrange(len(v)):
        v[i] /= norm
    return v

def getTexture(texture, texcache):
    if texture not in texcache:
        r = Reader(texture)
        rgb = list(r.asRGBA()[2])
        texcache[texture] = rgb
    return texcache[texture]

def textureTriMtxs(obj, img, texcache):
    mcols = [[]]*7
    for m, t, mat in ms:
        mcol = m + t + [[mat] * len(m[0])]
        mcols = edgeMtx.addEdgeMtxs(mcols, mcol)
    triangles = []
    for i in range(0, len(mcols[0]) - 2, 3):
        # print i, mcols[0][i], mcols[1][i], mcols[0][i + 1], mcols[1][i + 1], mcols[0][i + 2], mcols[1][i + 2], sum(mcols[2][i : i+3]), mcols[4][i]
        triangles.append([mcols[0][i], mcols[1][i], mcols[0][i + 1], mcols[1][i + 1], mcols[0][i + 2], mcols[1][i + 2], sum(mcols[2][i : i+3]), mcols[4][i], mcols[5][i], mcols[4][i+1], mcols[5][i+1], mcols[4][i+2], mcols[5][i+2], mcols[6][i]])  # 14 els long
    ordTris = sorted(triangles, key=lambda l: l[6])
    times = 0
    for t in ordTris:
        a = time()
        if t[13] is not None:  # todo shading w/ textures
            img.setPixels(drawTexturedTri(*t[:6] + t[7:]))
        else:  # todo shading w/o textures
            tri = triangle(*t[:6])
            coloredtri = [xy + (t[13],) for xy in tri]
            img.setPixels(coloredtri)
        times += time() - a
    print times / 1.0 / len(ordTris) * 1000

def copyPoint(pt):
    return Point(pt.x, pt.y, pt.z, pt.nx, pt.ny, pt.nz, pt.tx, pt.ty)


def appliedHomogeneousTrans(m, tris):
    newtris = [[copyPoint(i[0]), copyPoint(i[1]), copyPoint(i[2]), i[3]] for i in tris]
    for j in range(len(tris)):
        tri = tris[j]
        newtri = newtris[j]
        for i in xrange(3):
            pt = tri[i]
            new = newtri[i]
            fac = dot4xyz(m[3], pt.x, pt.y, pt.z)
            x = dot4xyz(m[0], pt.x, pt.y, pt.z) / fac# * 500
            y = dot4xyz(m[1], pt.x, pt.y, pt.z) / fac# * 500
            z = dot4xyz(m[2], pt.x, pt.y, pt.z) / fac# * 500
            new.x = x
            new.y = y
            new.z = z
            print new.x, new.y, new.z
    return newtris

def applied(m, tris):
    newtris = [[copyPoint(i[0]), copyPoint(i[1]), copyPoint(i[2]), i[3]] for i in tris]
    for j in range(len(tris)):
        tri = tris[j]
        newtri = newtris[j]
        for i in xrange(3):
            pt = tri[i]
            new = newtri[i]
            x = dot4xyz(m[0], pt.x, pt.y, pt.z)
            y = dot4xyz(m[1], pt.x, pt.y, pt.z)
            z = dot4xyz(m[2], pt.x, pt.y, pt.z)
            new.x = x
            new.y = y
            new.z = z
            print x,y,z
    return newtris


def apply(m, tris):
    for t in tris:
        for i in xrange(3):
            pt = t[i]
            x = dot4xyz(m[0], pt.x, pt.y, pt.z)
            y = dot4xyz(m[1], pt.x, pt.y, pt.z)
            z = dot4xyz(m[2], pt.x, pt.y, pt.z)
            pt.x = x
            pt.y = y
            pt.z = z

def applyNorms(m, tris):
    for t in tris:
        for i in xrange(3):
            pt = t[i]
            nx = dot4xyz(m[0], pt.nx, pt.ny, pt.nz)
            ny = dot4xyz(m[1], pt.nx, pt.ny, pt.nz)
            nz = dot4xyz(m[2], pt.nx, pt.ny, pt.nz)
            pt.nx = nx
            pt.ny = ny
            pt.nz = nz

def dot4xyz(v, x, y, z):
    return v[0] * x + v[1] * y + v[2] * z + v[3]


def textureTest():
    help(Reader)
    r = Reader(file=open('tesx.png'))
    rgb = list(r.asRGBA()[2])
    print len(rgb),len(rgb[0])
    img = Image(500,500)
    drawTexturedTri(150,150,300,100,100,300,1,0,0,1,1,1,rgb,(255,255,0),img)
    img.savePpm('t.ppm')

def marioTest():
    from time import time
    tc = {}
    chdir('mario')
    triset = obj.parse('mario.obj','mario.mtl')
    mat = transform.T(250, 400, 0) * transform.R('z', 180) * transform.S(1.5,1.5,1.5)
    for i in range(len(triset)):
        triset[i][0] = mat * triset[i][0]
    img = Image(500,500)
    mat = transform.T(250,400,0)*transform.R('y',5)*transform.T(-250,-400,0)
    textureTriMtxs(triset,img,tc)
    print len(tc)
    img.display()
    for i in range(72):
        print 'making image...',
        a = time()
        img = Image(500,500)
        print (time() - a) * 1000, 'ms'
        print 'transforming...',
        a = time()
        for j in range(len(triset)):
            triset[j][0] = mat * triset[j][0]
        print (time() - a) * 1000, 'ms'
        print 'texturing...',
        a = time()
        textureTriMtxs(triset, img,tc)
        print (time() - a) * 1000, 'ms'
        print 'saving...',
        a = time()
        img.savePpm('../animar/%d.ppm'%(i))
        print (time() - a) * 1000, 'ms'
        print i, 'drawn'

def shadetest():
    x1, y1, z1 = 100, 100, 200
    x2, y2, z2 = 300, 150, 0
    x3, y3, z3 = 150, 300, 0
    nx1, ny1, nz1 = normalize(x1, y1, z1)
    nx2, ny2, nz2 = normalize(x2, y2, z2)
    nx3, ny3, nz3 = normalize(x3, x3, z3)
    lx, ly, lz = 300, 300, 300
    col = (255, 150, 30)
    Ia = (255,200,150)
    Id = (255,200, 150)
    Is = (255,200,150)
    Ka = (0,200,100)
    Kd = (0,200,100)
    Ks = (255,255,255)
    a = 0.5
    img = Image(500, 500)
    shadePix = drawShadedTri(x1,y1,z1,x2,y2,z2,x3,y3,z3,nx1,ny1,nz1,nx2,ny2,nz2,nx3,ny3,nz3,lx,ly,lz,Ia,Id,Is,Ka,Kd,Ks,a)
    print shadePix
    img.setPixels(shadePix)
    img.display()

def sphereshade():
    lx, ly, lz = 700,100,0
    vx, vy = 250, 250
    Ia = (100, 100, 100)
    Id = (255, 0, 0)
    Is = (255, 150, 150)
    Ks = (128, 128, 128)

    zbuf = [[None for _ in xrange(500)] for _ in ge(500)]
    tris = transform.T(250, 250, 0) * edgeMtx.sphere(200, .02)
    sts = edgeMtx.edgemtx()
    edgeMtx.addCircle(sts,0,0,0,500,.05)
    sts = transform.T(250,250,0)*transform.R('y', -45)*transform.R('x', 90)*sts
    sts = zip(*sts)[::2]
    ke=0
    for lx,ly,lz,_ in sts:
        img = Image(500,500)
        triList = []
        for i in range(0, len(tris[0]) - 2, 3):
            triList.append(tuple(tris[0][i : i + 3] + tris[1][i : i + 3] + tris[2][i : i + 3]))
        triList.sort(key=lambda t: sum(t[6:9]))
        print 'sorted lis'
        for x1, x2, x3, y1, y2, y3, z1, z2, z3 in triList:
            nx1, ny1, nz1 = normalize(x1 - 250, y1 - 250, z1)
            nx2, ny2, nz2 = normalize(x2 - 250, y2 - 250, z2)
            nx3, ny3, nz3 = normalize(x3 - 250, y3 - 250, z3)
            shadePix = drawShadedTri(x1,y1,z1,x2,y2,z2,x3,y3,z3,nx1,ny1,nz1,nx2,ny2,nz2,nx3,ny3,nz3,lx,ly,lz,vx,vy,vz,Ia,Id,Is,Ka,Kd,Ks,a,zbuf)
            img.setPixels(shadePix)
        img.savePpm('shade/%d.ppm'%(ke))
        if ke == 0: img.display()
        ke+=1
        print ke

def sphinput():
    lx, ly, lz = tuple(input('light position x,y,z: '))
    vz = int(input('viewer position z: '))
    vx = vy = 250
    Ia = tuple(input('ambient color r,g,b: '))
    Id = tuple(input('light color r,g,b: '))
    Is = tuple(input('spectral color r,g,b: '))
    Ka = Kd = tuple(input('ball color r,g,b: '))
    Ks = 255, 255, 255
    a = int(input('shininess a: '))
    n = 1. / float(input('sphere steps: '))
    r = float(input('radius: '))
    cx, cy, cz = tuple(input('center position x,y,z: '))
    tris = transform.T(cx, cy, cz) * edgeMtx.sphere(r, n)
    zbuf = [[None] * 500 for i in xrange(500)]
    zbuf[250][250] = 1
    print zbuf[251][250]
    img = Image(500,500)
    triList = []
    for i in range(0, len(tris[0]) - 2, 3):
        triList.append(tuple(tris[0][i : i + 3] + tris[1][i : i + 3] + tris[2][i : i + 3]))
    triList.sort(key=lambda t: -sum(t[6:9]))
    print 'sorted lis'
    for x1, x2, x3, y1, y2, y3, z1, z2, z3 in triList:
        nx1, ny1, nz1 = normalize(x1 - cx, y1 - cy, z1 - cz)
        nx2, ny2, nz2 = normalize(x2 - cx, y2 - cy, z2 - cz)
        nx3, ny3, nz3 = normalize(x3 - cx, y3 - cy, z3 - cz)
        shadePix = drawShadedTri(x1,y1,z1,x2,y2,z2,x3,y3,z3,nx1,ny1,nz1,nx2,ny2,nz2,nx3,ny3,nz3,lx,ly,lz,vx,vy,vz,Ia,Id,Is,Ka,Kd,Ks,a,zbuf)
        img.setPixels(shadePix)
    img.display()
    img.saveAs('sph.png')

def marioshadetest():
    img = Image(500, 500)
    # TODO implement lights, texcache, zbuf
    lights = [Light(409.1, 409.1, 0, (30, 10, 10), (200, 50, 50), (255, 150, 150)), 
        Light(25, 250, 50, (5, 30, 10), (50, 200, 50), (150, 255, 150)),
        Light(250, 25, 100, (10, 20, 30), (50, 50, 200), (150, 150, 255))]
    fov = 90
    cam = Camera(250, 250, 200, 0, 0, 0, -250,-250, 1 / math.tan(fov / 2.))
    camT = transform.T(cam.x,cam.y,cam.z)*transform.C2(cam, 500, -500)
    print matrix.toStr(camT)
    lballs = []
    sphere = edgeMtx.sphere(20, .1)
    for l in lights:
        lightball = transform.T(l.x, l.y, l.z) * sphere
        lballs.append([lightball, l.Id])
    texcache = {}
    chdir('mario')
    tris = obj.parse('mario.obj','mario.mtl')
    mrot = transform.R('z', 180)*transform.R('y', 180)
    m = transform.T(250,380,0)*transform.S(1.2, 1.2, 1.2)*mrot
    apply(m, tris)
    applyNorms(mrot, tris)
    # ROTATE MARIO
    # mrot = transform.R('y', 5)
    # m = transform.T(250, 380, 0) * mrot * transform.T(-250, -380, 0)
    # ROTATE LIGHTS
    m = transform.T(250, 250, 0) * transform.R('z', 5) * transform.T(-250, -250, 0)
    for i in range(72):
        a = time()
        zbuf = [[None]*500 for j in xrange(500)]
        img = Image(500, 500)
        for ball, col in lballs:
            edgeMtx.drawTriangles(ball, img, col, col, False)
        tricam = applied(camT, tris)
        tricam.sort(key=lambda tri: -tri[0].z - tri[1].z - tri[2].z)
        for tri in tricam:
            #for j in xrange(3):
            #    pt = tri[j]
            #    pt.x += cam.x
            #    pt.y += cam.y
            #    pt.z += cam.z
            img.setPixels(renderTriangle(*tri + [cam.vx, cam.vy, cam.vz, lights, texcache, zbuf]))
        if i == 0:
            img.display()
            img.saveAs('proj.png')
        img.savePpm('../marshade/%d.ppm' % (i))
        # ROTATE MARIO
        # apply(m, tris)
        # applyNorms(mrot, tris)
        # ROTATE LIGHTS
        for ball in lballs:
            ball[0] = m * ball[0]
        for l in lights:
            x = dot4xyz(m[0], l.x, l.y, l.z)
            y = dot4xyz(m[1], l.x, l.y, l.z)
            z = dot4xyz(m[2], l.x, l.y, l.z)
            l.x = x
            l.y = y
            l.z = z
        print i, 'in', (time() - a) * 1000, 'ms'
    chdir('..')
    img.display()
    img.saveAs('marshade.png')

def triIter(m):
    for i in range(0, len(m[0]), 3):
        t = matrix.transpose([m[j][i:i+3] for j in xrange(3)])
        x = 0
        for j in t:
            for k in range(len(j)):
                j[k] *= 250./m[3][i + x]
            x += 1
        yield t
        
    
def camtest():
    import shape
    fov = 100
    cam = Camera(0.5,0.5,0.8,0,0,0,0,0,1 / math.tan(fov / 2.))
    camargs = [100,100,-50,-300]
    camT = transform.C3(*camargs)*transform.T(-250, -250,-175)
    print camT
    ncamT = transform.C3invT(*camargs)
    print ncamT
    v = [250,250,1000]
    lights = [Light(500,0,500,(20,20,20),(200,200,200),(255,255,255)),
              Light(500,500,200,(20,20,20),(200,200,200),(255,255,255)),
              Light(0,250,500,(20,20,20),(200,200,200),(255,255,255))
    ]
    camlights = []
    for l in lights:
        x = dot4xyz(camT[0], l.x, l.y, l.z)
        y = dot4xyz(camT[1], l.x, l.y, l.z)
        z = dot4xyz(camT[2], l.x, l.y, l.z)
        w = dot4xyz(camT[3], l.x, l.y, l.z)*1.
        print x/w*250,y/w*250,z/w*250
        camlights.append(Light(x/w*250, y/w*250, z/w*250,l.Ia,l.Id,l.Is))
    tris, norms = shape.box(200,200,-100,100,100,200)
    print norms
    print ncamT * norms
    print list(triIter(tris))
    trot = transform.R('y',5)
    nrot = transform.TransMatrix()
    nrot.lst = matrix.transpose(transform.R('y',-5))
    tmat = transform.T(250,250,0)*trot*transform.T(-250,-250,0)
    tris = tmat*tmat*tmat*tris
    norms= trot*trot*trot*norms
    print norms
    print ncamT*norms
    amb = Texture(False, [255,0,0])
    diff = Texture(False, [255,0,0])
    spec = Texture(False, [255,150,150])
    mat = Material(amb, diff, spec, 10)
    for i in range(72):
        #print tris
        tricam = camT * tris
        #print tricam
        #tricam[3] = [1.] * len(tricam[3])
        #tricam = transform.T(*v) * tricam
        print 'trans done'
        a = time()
        zbuf = [[None]*500 for _ in range(500)]
        img = Image(500,500)
        trit = list(triIter(tricam))
        #print trit,tricam
        trit.sort(key=lambda tri: -tri[0][2] - tri[1][2] - tri[2][2])
        normcam = ncamT*norms
        normt = []
        for j in range(len(normcam[0])):
            sgn = (normcam[3][j] > 0) * 2 - 1
            normt.append(normalize(normcam[0][j]*sgn, normcam[1][j]*sgn, normcam[2][j]*sgn))
        print normt
        #print len(trit), len(normt)
        for j in range(len(trit)):
            # (p1, p2, p3, mat, vx, vy, vz, lights, texcache, zbuf):
            t = trit[j]
            ps = []
            for pt in t:
                pt[0]+=250
                pt[1]+=250
                pt[2]+=0
                print pt
                ps.append(Point(*pt + normt[j] + [0,0]))
            img.setPixels(renderTriangle(*ps + [mat] + v + [camlights, {}, zbuf]))
        for t in trit:
            l = line(*t[0][:2]+t[1][:2])
            l += line(*t[0][:2]+t[2][:2])
            l += line(*t[2][:2]+t[1][:2])
            img.setPixels([p + ((0,0,0),) for p in l])

        for j in range(len(trit)):
            t = trit[j]
            ps = []
            for pt in t:
                nls = line(pt[0] - 4, pt[1], pt[0] + 4, pt[1])
                nls += line(pt[0], pt[1] - 4, pt[0], pt[1] + 4)
                nls += line(pt[0] - 4, pt[1] - 4, pt[0] + 4, pt[1] + 4)
                nls += line(pt[0] - 4, pt[1] + 4, pt[0] + 4, pt[1] - 4)
                nls += line(pt[0], pt[1], pt[0] + normt[j][0]*20, pt[1] + normt[j][1]*20)
                print normt[j][0], normt[j][1]
                img.setPixels([p + ((0,255,0),) for p in nls])
        
        img.savePpm('cube/%d.ppm'%(i))
        tris = tmat * tris
        norms = nrot * norms
        print norms
        print i, (time() - a) * 1000, 'ms'
if __name__ == '__main__':
    camtest()
    
