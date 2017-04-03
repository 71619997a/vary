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
        border1 = lineByY(x1Base, yBase, x1Top, y1Top)
    else:
        border1 = lineByY(x1Base, yBase, x1Top, y1Top)[::-1]
    if x2Base > x1Top:
        border2 = lineByY(x2Base, yBase, x1Top, y1Top)
    else:
        border2 = lineByY(x2Base, yBase, x1Top, y1Top)[::-1]
    i = 0
    for y in range(y1Top, yBase):
        for x in range(border1[i][0], border2[i][0]+1):
            pts.append((x, y))
        i += 1
    return pts + border1 + border2

def botTriangle(yBase, x1Base, x2Base, x1Bot, y1Bot):
    pts = []
    if x1Base > x1Bot:
        border1 = lineByY(x1Base, yBase, x1Bot, y1Bot)[::-1]
    else:
        border1 = lineByY(x1Base, yBase, x1Bot, y1Bot)
    if x2Base > x1Bot:
        border2 = lineByY(x2Base, yBase, x1Bot, y1Bot)[::-1]

    else:
        border2 = lineByY(x2Base, yBase, x1Bot, y1Bot)
    i = 0
    for y in range(yBase, y1Bot + 1):
        for x in range(border1[i][0], border2[i][0]+1):
            pts.append((x, y))
        i += 1
    return pts + border1 + border2

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
