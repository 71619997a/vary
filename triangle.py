from line import line
import transform
from matrix import multiply
from os import chdir
from png import Reader
from time import time
from base import Image
import obj
import edgeMtx
import math
from vector import Vector
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

def triangle(v1, v2, v3):  # XXX doesnt handle flat well
    vs = sorted([v1, v2, v3], lambda v: v[0])
    ys, order = sortedInds([y1, y2, y3])
    xs = inOrder([x1, x2, x3], order)
    if vs[2][0] == vs[0][0]:
        x = vs[0][0]
    else:
        slope = (vs[2][1] - vs[0][1]) / float(vs[2][0] - vs[0][0])
        if slope == 0:
            x = vs[2][0]
        else:
            x = (vs[1][1] - vs[0][1]) / slope + vs[0][0]
    top = baseTriangle(vs[1][1], min(x, vs[1][0]), max(x, vs[1][0]), *vs[2].comp)
    bot = baseTriangle(vs[1][1], min(x, vs[1][0]), max(x, vs[1][0]), *vs[0].comp)
    return top + bot


    
