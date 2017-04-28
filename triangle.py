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
    for y in range(int(math.ceil(y1Top)), int(math.ceil(yBase))):
        try:
            border1[i][0]
            border2[i][0]
        except IndexError:
            continue
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
    for y in range(int(math.ceil(yBase)), int(math.ceil(y1Bot + 1))):
        try:
            border1[i][0]
            border2[i][0]
        except IndexError:
            continue
        for x in range(border1[i][0], border2[i][0]+1):
            pts.append((x, y))
        i += 1
    return pts + border1 + border2

def baseTriangle(yb, xb1, xb2, xp, yp):
    # yb, xb1, xb2, xp, yp = int(round(yb)), int(round(xb1)), int(round(xb2)), int(round(xp)), int(round(yp))
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


def triangle2(x1, y1, x2, y2, x3, y3):
    pts = []
    # 1. floating point -> integers with more precision
    x1 = int(round(x1))
    x2 = int(round(x2))
    x3 = int(round(x3))
    y1 = int(round(y1))
    y2 = int(round(y2))
    y3 = int(round(y3))

    # 2. find bounding box
    yMin = min(y1, y2, y3)
    yMax = max(y1, y2, y3)
    xMin = min(x1, x2, x3)
    xMax = max(x1, x2, x3)
    
    # 3. use eq of line to find interior:
    # on line if (y - y1)(x1 - x2) - (x - x1)(y1 - y2) = 0
    # y(x1 - x2) - x(y1 - y2) + C = 0
    # increment y = x1 - x2
    # incr3ement x = y2 - y1
    # C = x1(y1 - y2)-y1(x1 - x2)
    dy12 = x1 - x2
    dx12 = y2 - y1
    dy23 = x2 - x3
    dx23 = y3 - y2
    dy31 = x3 - x1
    dx31 = y1 - y3
    c12 = x1*(y1-y2)-y1*(x1-x2)
    c23 = x2*(y2-y3)-y2*(x2-x3)
    c31 = x3*(y3-y1)-y3*(x3-x1)

    x = xMin
    y = yMin
    A12start = y*dy12 + x*dx12 + c12
    A23start = y*dy23 + x*dx23 + c23
    A31start = y*dy31 + x*dx31 + c31
    print A12start, A23start, A31start
    # 4. Loop
    while y < yMax:
        # start at x=xmin, y=whatever
        A12 = A12start
        A23 = A23start
        A31 = A31start
        while x < xMax:
            if A12 > 0 and A23 > 0 and A31 > 0:
                pts.append((x, y))
            A12 += dx12
            A23 += dx23
            A31 += dx31
            print A12, A23, A31
            x += 1
        # discard A, move Astart down
        A12start += dy12
        A23start += dy23
        A31start += dy31
        y += 1
    return pts
            
