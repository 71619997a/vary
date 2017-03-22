from line import line
import transform
from matrix import multiply
from os import chdir
from multiprocessing import Pool
from png import Reader
from time import time
from base import Image
import obj
import edgeMtx
import math
from common import *
#chdir('/storage/emulated/0/qpython/scripts/gfx-base/gfx-base')

def sortedInds(lst):
    fix = enumerate(lst)
    sort = sorted(fix, key=lambda t: t[1])
    return tuple(zip(*sort)[::-1])

def inOrder(lst, order):
    return [lst[i] for i in order]

def topTriangle(yBase, x1Base, x2Base, x1Top, y1Top):
    pts = []
    if x1Base > x1Top:
        border1 = line(x1Base, yBase, x1Top, y1Top)
    else:
        border1 = line(x1Base, yBase, x1Top, y1Top)[::-1]
    if x2Base > x1Top:
        border2 = line(x2Base, yBase, x1Top, y1Top)
    else:
        border2 = line(x2Base, yBase, x1Top, y1Top)[::-1]
    i1 = i2 = 0
    for y in range(y1Top, yBase + 1):
        while border1[i1][1] != y:
            i1 += 1
        while border2[i2][1] != y:
            i2 += 1
        for x in range(border1[i1][0], border2[i2][0] + 1):
            pts.append((x, y))
    return pts

def botTriangle(yBase, x1Base, x2Base, x1Bot, y1Bot):
    pts = []
    if x1Base > x1Bot:
        border1 = line(x1Base, yBase, x1Bot, y1Bot)[::-1]
    else:
        border1 = line(x1Base, yBase, x1Bot, y1Bot)
    if x2Base > x1Bot:
        border2 = line(x2Base, yBase, x1Bot, y1Bot)[::-1]
    else:
        border2 = line(x2Base, yBase, x1Bot, y1Bot)
    i1 = i2 = 0
    for y in range(yBase, y1Bot + 1):
        while border1[i1][1] != y:
            i1 += 1
        while border2[i2][1] != y:
            i2 += 1
        for x in range(border1[i1][0], border2[i2][0] + 1):
            pts.append((x, y))
    return pts

def baseTriangle(yb, xb1, xb2, xp, yp):
    yb, xb1, xb2, xp, yp = int(yb), int(xb1), int(xb2), int(xp), int(yp)
    if yp >= yb:
        return botTriangle(yb, xb1, xb2, xp, yp)
    return topTriangle(yb, xb1, xb2, xp, yp)

def triangle(x1, y1, x2, y2, x3, y3):  # XXX doesnt handle flat well
    ys, order = sortedInds([y1, y2, y3])
    xs = inOrder([x1, x2, x3], order)
    if xs[2] == xs[0]:
        x = xs[0]
    else:
        slope = (ys[2] - ys[0]) / float(xs[2] - xs[0])
        if slope == 0:
            x = xs[2]
        else:
            x = (ys[1] - ys[0]) / slope + xs[0]
    top = baseTriangle(ys[1], min(x, xs[1]), max(x, xs[1]), xs[2], ys[2])
    bot = baseTriangle(ys[1], min(x, xs[1]), max(x, xs[1]), xs[0], ys[0])
    return top + bot

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
                pts.append((x, y, rgb[l-ycor][xcor:xcor+3]))
        else:
            pts.append((x, y, bgcol))
    return pts

def renderTriangle(p1, p2, p3, mat, vx, vy, vz, lights, texcache, zbuf):
    tri = triangle(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y)
    det = float((p2.y - p3.y) * (p1.x - p3.x) + (p3.x - p2.x) * (p1.y - p3.y))
    pts = []
    if mat.amb.type:
        ambtex = getTexture(mat.amb.texture, texcache)
    if mat.diff.type:
        difftex = getTexture(mat.diff.texture, texcache)
    if mat.spec.type:
        spectex = getTexture(mat.spec.texture, texcache)
    for x, y in tri:
        if not (0 <= x < 500 and 0 <= y < 500):
            continue
        d1, d2, d3 = getBary(x, y, p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, det)
        z = p1.z * d1 + p2.z * d2 + p3.z * d3
        if zbuf[y][x] >= z:
            continue
        zbuf[y][x] = z
        Ka = mat.amb.color
        Kd = mat.diff.color
        Ks = mat.spec.color
        if mat.amb.type or mat.diff.type or mat.spec.type:
            tcx = tx1*d1+tx2*d2+tx3*d3
            tcy = ty1*d1+ty2*d2+ty3*d3
            # print tc[0], tc[1]
            if 1>=tcx>=0 and 1>=tcy>=0:
                xcor = int(tcx*tw)*4
                ycor = int(tcy*th)
                # TODO transparency checking
                if mat.amb.type:
                    Ka = ambtex[ycor][xcor : xcor + 3]
                if mat.diff.type:
                    Kd = difftex[ycor][xcor : xcor + 3]
                if mat.spec.type:
                    Ks = spectex[ycor][xcor : xcor + 3]
        nx = p1.nx * d1 + p2.nx * d2 + p3.nx * d3
        ny = p1.ny * d1 + p2.ny * d2 + p3.ny * d3
        nz = p1.nz * d1 + p2.nz * d2 + p3.nz * d3
        col = shader(x, y, z, nx, ny, nz, lights, vx, vy, vz, Ka, Kd, Ks, mat.exp)
        pts.append(x, y, col)
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
        
def shader(x,y,z,nx,ny, nz,lx,ly,lz,vx,vy,vz, Ia,Id,Is,Ka, Kd, Ks,a):
    Lmx , Lmy, Lmz = normalize(lx-x,ly-y,lz-z)
    Lmn = Lmx * nx + Lmy * ny + Lmz * nz
    Rmx = 2 * Lmn * nx - Lmx
    Rmy = 2 * Lmn * ny - Lmy
    Rmz = 2 * Lmn * nz - Lmz
    Vx, Vy, Vz = normalize(vx-x,vy-y,vz-z)
    diff = max(Lmn, 0)
    try:
        spec = math.pow(max((Rmx*Vx+Rmy*Vy+Rmz*Vz), 0),a)
    except:
        spec = 1
    c = [0,0,0]
    for i in xrange(3):
        c[i] = min(max(int(Ka[i]*Ia[i] + Kd[i]*Id[i]*diff + Ks[i]*Is[i]*spec),0),65535) / 256
    return c

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

def apply(m, tris):
    for t in tris:
        for i in xrange(3):
            pt = t[i]
            x = dot4xyz(m[0], pt.x, pt.y, pt.z)
            y = dot4xyz(m[0], pt.x, pt.y, pt.z)
            z = dot4xyz(m[0], pt.x, pt.y, pt.z)
            pt.x = x
            pt.y = y
            pt.z = z

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

    zbuf = [[None for _ in xrange(500)] for _ in xrange(500)]
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
    chdir('mario')
    tris = obj.parse('mario.obj','mario.mtl')
    m = transform.T(250,250,0)*transform.R('z', 180)
    apply(m, tris)
    for tri in tris
    renderTriangle(p1, p2, p3, mat, vx, vy, vz, lights, texcache, zbuf)
    
if __name__ == '__main__':
    sphinput()
    
