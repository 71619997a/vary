from triangle import triangle
from line import line
from time import time
from base import Image
from png import Reader
import edgeMtx
import transform
import obj
import math
from vector import Vector, concat, transVecs
class Light(object):
    def __init__(self, pos, Ia, Id, Is):
        self.pos = pos
        self.Ia = Ia
        self.Id = Id
        self.Is = Is

def getBary(x, y, x1, y1, x2, y2, x3, y3, z3, det):
        d1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / det
        d2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / det
        return d1, d2, 1-d1-d2

def drawTexturedTri(x1, y1, x2, y2, x3, y3, tx1, ty1, tx2, ty2, tx3, ty3, rgb, bgcol): #1-6 vertices, 7-12 tcors, 13 tex rgb, 14 bg color
    a = time()
    pts = []
    l = len(rgb)-1
    th = len(rgb) - 1
    tw = len(rgb[0]) / 4 - 1
    tri = triangle(x1,y1,x2,y2,x3,y3)
    det = float((y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3))
    if det == 0:
        return pts
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

def drawShadedTri(v1,v2,v3,n1,n2,n3,light,view,col,Ia,Id,Is,Ka,Kd,Ks,a):
    pts = []
    v12 = v1.to(2)
    v22 = v2.to(2)
    v32 = v3.to(2)
    tri = triangle(v12, v22, v32)
    y2 * x1 - x2 * y1 + x3 * y1 - y3 * x1   +   x2 * x3 - y2 * x3
    det = float((v2[1] - v3[1]) * (v1[0] - v3[0]) + (v3[0] - v2[0]) * (v1[1] - v3[1]))
    for tup in tri:
        d=Vector(*getBary(*tup + concat(v1, v2, v3) + [det]))
        nx, ny, nz = transVecs(n1, n2, n3)
        n = Vector(nx * d, ny * d, nz * d)
        z = transVecs(v1, v2, v3)[2] * d
        pts.append((tup[0], tup[1],shader(Vector(tup[0], tup[1], z),n,light, view,col, Ia,Id,Is, Ka, Kd, Ks, a)))
    return pts


def shader(pt,n,light, view, col, Ia,Id,Is,Ka, Kd, Ks,a):
    Lm = (light - pt).normalized()
    Lmn = Lm * n
    Rm = 2 * Lmn * n - Lm
    V = (view - pt).normalized()
    try:
        Ip = Ka * Ia + Kd * Lmn * Id + Ks * math.pow(max((Rm * V), 0),a) * Is
    except:
        Ip = 1000000000
    if Ip <= 0:
        return Vector(0,0,0)
    return Ip * col
def textureTriMtxs(ms, img, texcache):
    mcols = [[]]*8
    for m, t, texture, col in ms:
        if texture is None:
            rgb = None
        else:
            if texture not in texcache:
                print texture
                r = Reader(texture)
                rgb = list(r.asRGBA()[2])
                texcache[texture] = rgb
            rgb = texcache[texture]
        mcol = m + t + [[rgb] * len(m[0])] + [[col] * len(m[0])]
        mcols = edgeMtx.addEdgeMtxs(mcols, mcol)
    triangles = []
    for i in range(0, len(mcols[0]) - 2, 3):
        # print i, mcols[0][i], mcols[1][i], mcols[0][i + 1], mcols[1][i + 1], mcols[0][i + 2], mcols[1][i + 2], sum(mcols[2][i : i+3]), mcols[4][i]
        triangles.append([mcols[0][i], mcols[1][i], mcols[0][i + 1], mcols[1][i + 1], mcols[0][i + 2], mcols[1][i + 2], sum(mcols[2][i : i+3]), mcols[4][i], mcols[5][i], mcols[4][i+1], mcols[5][i+1], mcols[4][i+2], mcols[5][i+2], mcols[6][i], mcols[7][i]])
    ordTris = sorted(triangles, key=lambda l: l[6])
    times = 0
    for t in ordTris:
        a = time()
        if t[13] is not None:
            img.setPixels(drawTexturedTri(*t[:6] + t[7:]))
        else:
            tri = triangle(*t[:6])
            coloredtri = [xy + (t[14],) for xy in tri]
            img.setPixels(coloredtri)
        times += time() - a
    print times / 1.0 / len(ordTris) * 1000

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
    Ia = 0.3
    Id = 0.5
    Is = 0.9
    Ka = 0.3
    Kd = 0.5
    Ks = 0.9
    a = 0.5
    img = Image(500, 500)
    shadePix = drawShadedTri(x1,y1,z1,x2,y2,z2,x3,y3,z3,nx1,ny1,nz1,nx2,ny2,nz2,nx3,ny3,nz3,lx,ly,lz,col,Ia,Id,Is,Ka,Kd,Ks,a)
    print shadePix
    img.setPixels(shadePix)
    img.display()

def sphereshade():
    lx, ly, lz = 700,100,0
    vx, vy, vz = 250, 250, 2000
    col = (255, 150, 30)
    Ia = 0.4
    Id = 0.8
    Is = 1
    Ka = 0.7
    Kd = 0.4
    Ks = 1
    a = 100
    
    tris = transform.T(250, 250, 0) * edgeMtx.sphere(200, .02)
    sts = edgeMtx.edgemtx()
    edgeMtx.addCircle(sts,0,0,0,500,.01)
    sts = transform.T(250,250,0)*transform.R('x', 90)*sts
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
            shadePix = drawShadedTri(x1,y1,z1,x2,y2,z2,x3,y3,z3,nx1,ny1,nz1,nx2,ny2,nz2,nx3,ny3,nz3,lx,ly,lz,vx,vy,vz,col,Ia,Id,Is,Ka,Kd,Ks,a)
            img.setPixels(shadePix)
        img.savePpm('shade/%d.ppm'%(ke))
        if ke == 0:
            img.display()
        ke+=1
        print ke
if __name__ == '__main__':
    sphereshade()
