from line import line
import transform
from matrix import multiply
from os import chdir
from png import Reader
from time import time
from base import Image
import obj
import edgeMtx
import numpy as np
import matrix
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
    for y in range(y1Top, yBase):
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
#  BARY LIE FUNCTIONS




def topTriangleTex(yBase, x1Base, x2Base, x1Top, y1Top, rgb):
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
    for y in range(y1Top, yBase):
        while border1[i1][1] != y:
            i1 += 1
        while border2[i2][1] != y:
            i2 += 1
        for x in range(border1[i1][0], border2[i2][0] + 1):
            pts.append((x, y, rgb[y][x:x+3]))
    return pts


def botTriangleTex(yBase, x1Base, x2Base, x1Bot, y1Bot, rgb):

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
            pts.append((x, y, rgb[y][x:x+3]))
    return pts

def baseTriangleTex(yb, xb1, xb2, xp, yp, rgb):
    yb, xb1, xb2, xp, yp = int(yb), int(xb1), int(xb2), int(xp), int(yp)
    if yp >= yb:
        return botTriangleTex(yb, xb1, xb2, xp, yp, rgb), True
    return topTriangleTex(yb, xb1, xb2, xp, yp, rgb), False

def triangleTex(x1, y1, x2, y2, x3, y3, rgb):  # XXX doesnt handle flat well
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
    t1, isBot1 = baseTriangleTex(ys[1], min(x, xs[1]), max(x, xs[1]), xs[2], ys[2], rgb)
    t2, _ = baseTriangleTex(ys[1], min(x, xs[1]), max(x, xs[1]), xs[0], ys[0], rgb)
    return t2 + t1 if isBot1 else t1 + t2


def getBary(x,y,x1,y1,x2,y2,x3,y3,det):
    d1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / det
    d2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / det
    return d1, d2, 1-d1-d2


def drawTexturedTri(m, tx1, ty1, tx2, ty2, tx3, ty3, rgb, bgcol): #1-6 vertices, 7-12 tcors, 13 tex rgb, 14 bg color
    a = time()
    th = len(rgb) - 1
    tw = len(rgb[0]) / 4 - 1
    x1, x2, x3, y1, y2, y3 = tuple(m[0]) + tuple(m[1])
    det = float((y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3))
    a = (y2 - y3) / det
    b = (x3 - x2) / det
    c = (y3 - y1) / det
    d = (x1 - x3) / det
    T = [
        [1, 0, -x3],
        [0, 1, -y3],
        [0, 0, 1]
    ]
    baryT = [
        [a, b, 0],
        [c, d, 0],
        [-a-c, -b-d, 1]
    ]
    texT = [
        [tx1, tx2, tx3],
        [ty1, ty2, ty3]
    ]
    S = [
        [tw, 0],
        [0, th]
    ]
    result = np.array(multiply(S, multiply(texT, multiply(baryT, T))), dtype=np.dtype(np.float32))
    tri = np.array(zip(*triangle(x1, y1, x2, y2, x3, y3)), dtype=np.dtype(np.int32))
    tri = np.vstack((tri, np.ones((1, len(tri[0])), dtype=np.dtype(np.int32))))
    transTri = np.zeros((2, len(tri[0])), dtype=np.dtype(np.float32))
    matrix.mat_23_3n_mult_kernel[len(tri[0]) / 256 + 1, 256](result, tri, transTri, len(tri[0]))
    #transTri = multiply(result, tri)
    def getcol(i):
        tcx = int(transTri[0][i])
        tcy = int(transTri[1][i])
        if tw >= tcx >= 0 and th >= tcy >= 0:
            tcx *= 4
            return rgb[th - tcy][tcx:tcx+3]
        else:
            return bgcol
        # try:
        #     if l >= int(transTri[1][i]):
        #         row = rgb[l - int(transTri[1][i])]
        #     else:
        #         return bgcol
        #     xcor = int(transTri[0][i]) * 4
        #     if row[xcor + 3] == 255:
        #         a = tuple(row[xcor:xcor + 3])
        #         return a
        #     else:
        #         return -1
        # except IndexError:
        #     return bgcol
        # return bgcol
    pts = [(tri[0][i], tri[1][i], getcol(i)) for i in range(len(tri[0]))]
    return pts
    tcyinc = cy1*ty1+cy2*ty2+cy3*ty3
    d1,d2,d3 = getBary(tri[0][1], tri[0][0], x1, y1, x2, y2, x3, y3, 1/idet)
    tcx = tx1*d1+tx2*d2+tx3*d3
    tcy = ty1*d1+ty2*d2+ty3*d3
    for y, x1, x2 in tri:
        for x in range(x1, x2 + 1):
            # print tc[0], tc[1]
            if 1>=tcx>=0 and 1>=tcy>=0:
                xcor = int(tcx*tw)*4
                ycor = int(tcy*th)
                if rgb[l-ycor][xcor + 3] == 255:
                    pts.append((x, y, rgb[l-ycor][xcor:xcor+3]))
            else:
                pts.append((x, y, bgcol))
            tcx += tcxinc
        tcy += tcyinc
    return pts


def textureTriMtxs(ms, img, texcache):
    mcols = [[]]*8
    for m, t, texture, col in ms:
        if texture is None:
            rgb = None
        else:
            if texture not in texcache:
                r = Reader(texture)
                rgb = list(r.asRGBA()[2])
                texcache[texture] = rgb
            rgb = texcache[texture]
        mcol = m + t + [[rgb] * len(m[0])] + [[col] * len(m[0])]
        mcols = edgeMtx.addEdgeMtxs(mcols, mcol)
    triangles = []
    for i in range(0, len(mcols[0]) - 2, 3):
        # print i, mcols[0][i], mcols[1][i], mcols[0][i + 1], mcols[1][i + 1], mcols[0][i + 2], mcols[1][i + 2], sum(mcols[2][i : i+3]), mcols[4][i]
        triangles.append([[mcols[0][i:i+3], mcols[1][i:i+3]], sum(mcols[2][i : i+3]), mcols[4][i], mcols[5][i], mcols[4][i+1], mcols[5][i+1], mcols[4][i+2], mcols[5][i+2], mcols[6][i], mcols[7][i]])
    ordTris = sorted(triangles, key=lambda l: l[1])
    times = 0
    for t in ordTris:
        a = time()
        if t[8] is not None:
            img.setPixels(drawTexturedTri(*t[:1] + t[2:]))
        else:
            tri = triangle(*[i for tup in zip(*t[0]) for i in tup])
            coloredtri = [xy + (t[9],) for xy in tri]
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

def mariotest():
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

def triCTest():
    print triangleC(0,200,50,100,150,175)
    
if __name__ == '__main__':
    mariotest()
