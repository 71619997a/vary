from line import line
import transform
from matrix import multiply
from os import chdir
from png import Reader
from time import time
from base import Image
from numba import jit, cuda
import numba as nb
import obj
import edgeMtx
import numpy as np
from itertools import izip
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
            pts.append([x, y])
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
            pts.append([x, y])
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

@cuda.jit
def getBary(x,y,x1,y1,x2,y2,x3,y3,det):
    d1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / det
    d2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / det
    return np.ndarray([d1, d2, 1-d1-d2])

def lzip(*iterables):
    iterators = map(iter, iterables)
    while iterators:
        yield list(map(next, iterators))

def drawTexturedTri(*args):  #1-6 vertices, 7-12 tcors, 13 tex rgb, 14 bg color
    tri = list(lzip(*triangle(*args[:6])))
    print tri
    tri = np.array(list(lzip(*triangle(*args[:6]))), dtype=np.dtype(np.int32))
    pts = np.ndarray((len(tri), 5), dtype=np.dtype(np.int32))
    tpb = 100
    b = len(tri) / tpb + 1
    colorPointsOfTri[b, tpb](*(tri, pts) + args)
    return [(l[0], l[1], l[2:4]) for l in pts]

@cuda.jit
def colorPointsOfTri(tri, pts, x1, y1, x2, y2, x3, y3, tx1, ty1, tx2, ty2, tx3, ty3, rgb, bgcol):
    idx = cuda.grid(1)
    if idx > len(tri): 
        return
    cuda.syncthreads()
    th = len(rgb) - 1
    tw = len(rgb[0]) / 4 - 1
    det = float((y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3))
    x, y = tri[idx]
    d1 = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / det
    d2 = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / det
    d3 = 1 - d1 - d2
    tcx = tx1*d1+tx2*d2+tx3*d3
    tcy = ty1*d1+ty2*d2+ty3*d3
    # print tc[0], tc[1]
    if 1>=tcx>=0 and 1>=tcy>=0:
        xcor = int(tcx*tw)*4
        ycor = int(tcy*th)
        if rgb[th-ycor][xcor + 3] == 255:
            pts[idx, 0] = x
            pts[idx, 1] = y
            pts[idx, 2] = rgb[th-ycor, xcor]
            pts[idx, 3] = rgb[th-ycor, xcor+1]
            pts[idx, 4] = rgb[th-ycor, xcor+2]
        else:
            pts[idx, 4] = -1
    else:
        pts[idx, 0] = x
        pts[idx, 1] = y
        pts[idx, 2] = bgcol[0]
        pts[idx, 3] = bgcol[1]
        pts[idx, 4] = bgcol[2]


def textureTriMtxs(ms, img, texcache):
    mcols = [[]]*8
    for m, t, texture, col in ms:
        if texture is None:
            rgb = None
        else:
            if texture not in texcache:
                r = Reader(file=open(texture))
                rgb = np.array([list(a) for a in r.asRGBA()[2]], dtype=np.dtype(np.int32))
                texcache[texture] = rgb
            rgb = texcache[texture]
        npc = np.array(col, dtype=np.dtype(np.int32))
        print npc
        mcol = m + t + [[rgb] * len(m[0])] + [[npc] * len(m[0])]
        mcols = edgeMtx.addEdgeMtxs(mcols, mcol)
    triangles = []
    for i in range(0, len(mcols[0]) - 2, 3):
        # print i, mcols[0][i], mcols[1][i], mcols[0][i + 1], mcols[1][i + 1], mcols[0][i + 2], mcols[1][i + 2], sum(mcols[2][i : i+3]), mcols[4][i]
        triangles.append([mcols[0][i], mcols[1][i], mcols[0][i + 1], mcols[1][i + 1], mcols[0][i + 2], mcols[1][i + 2], sum(mcols[2][i : i+3]), mcols[4][i], mcols[5][i], mcols[4][i+1], mcols[5][i+1], mcols[4][i+2], mcols[5][i+2], mcols[6][i], mcols[7][i]])
    ordTris = sorted(triangles, key=lambda l: l[6])
    for t in ordTris:
        if t[13] is not None:
            img.setPixels(drawTexturedTri(*t[:6] + t[7:]))
        else:
            tri = triangle(*t[:6])
            coloredtri = [xy + [t[14]] for xy in tri]
            img.setPixels(coloredtri)

def textureTest():
    help(Reader)
    r = Reader(file=open('tesx.png'))
    rgb = list(r.asRGBA()[2])
    print len(rgb),len(rgb[0])
    img = Image(500,500)
    drawTexturedTri(150,150,300,100,100,300,1,0,0,1,1,1,rgb,(255,255,0),img)
    img.savePpm('t.ppm')

if __name__ == '__main__':
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
