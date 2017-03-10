from line import line
import transform
from matrix import multiply
from os import chdir
from png import Reader
from base import Image
import obj
import edgeMtx
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

def getBary(x,y,x1,y1,x2,y2,x3,y3):
    m = [[y2-y3,x3-x2],[y3-y1,x1-x3]]
    m = multiply(m, 1./((x1-x3)*(y2-y3)-(y1-y3)*(x2-x3)))
    rr3 = [[x-x3],[y-y3]]
    res = multiply(m,rr3)
    d1 = res[0][0]
    d2 = res[1][0]
    return d1, d2, 1-d1-d2

def lerpcol(c1, c2, fac):
    return tuple(int(c1[i] * (255 - fac) / 255. + c2[i] * fac / 255.) for i in xrange(3))

def drawTexturedTri(*args): #1-6 vertices, 7-12 tcors, 13 tex rgb, 14 bg color 15 img
    rgb = args[12]
    l = len(rgb)-1
    img = args[14]
    th = len(rgb) - 1
    tw = len(rgb[0]) / 4 - 1
    tri = triangle(*args[:6])
    texs = []
    for pt in tri:
        d1,d2,d3=getBary(*pt+args[:6])
        tc = (args[6]*d1+args[8]*d2+args[10]*d3,
        args[7]*d1+args[9]*d2+args[11]*d3)
        # print tc[0], tc[1]
        if 1>=tc[0]>=0 and 1>=tc[1]>=0:
            xcor = int(tc[0]*tw)*4
            ycor = int(tc[1]*th)
            col = lerpcol(args[13], tuple(rgb[l-ycor][xcor:xcor+3]), rgb[l-ycor][xcor + 3])
            
            img.setPixel(pt[0], pt[1], col)
        else:
            img.setPixel(pt[0], pt[1], args[13])


def textureTriMtxs(ms, img, texcache):
    mcols = [[]]*8
    for m, t, texture, col in ms:
        if texture is None:
            rgb = None
        else:
            if texture not in texcache:
                r = Reader(file=open(texture))
                rgb = list(r.asRGBA()[2])
                texcache[texture] = rgb
            rgb = texcache[texture]
        mcol = m + t + [[rgb] * len(m[0])] + [[col] * len(m[0])]
        mcols = edgeMtx.addEdgeMtxs(mcols, mcol)
    triangles = []
    for i in range(0, (len(mcols[0]) - 2)/3):
        # print i, mcols[0][i], mcols[1][i], mcols[0][i + 1], mcols[1][i + 1], mcols[0][i + 2], mcols[1][i + 2], sum(mcols[2][i : i+3]), mcols[4][i]
        triangles.append([mcols[0][i*3], mcols[1][i*3], mcols[0][i*3 + 1], mcols[1][i*3 + 1], mcols[0][i*3 + 2], mcols[1][i*3 + 2], sum(mcols[2][i*3 : i*3+3]), mcols[4][i*3], mcols[5][i*3], mcols[4][i*3+1], mcols[5][i*3+1], mcols[4][i*3+2], mcols[5][i*3+2], mcols[6][i * 3], mcols[7][i * 3]])
    ordTris = sorted(triangles, key=lambda l: l[6])
    for t in ordTris:
        if t[13] is not None:
            drawTexturedTri(*t[:6] + t[7:] +[img])
        else:
            tri = triangle(*t[:6])
            coloredtri = [xy + (t[14],) for xy in tri]
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
    tc = {}
    chdir('mario')
    triset = obj.parse('mario.obj','mario.mtl')
    mat = transform.T(250, 400, 0) * transform.R('z', 180) * transform.S(1.5,1.5,1.5) * transform.R('y', 180)
    for i in range(len(triset)):
        triset[i][0] = mat * triset[i][0]
    img = Image(500,500)
    mat = transform.T(250,400,0)*transform.R('y',5)*transform.T(-250,-400,0)
    textureTriMtxs(triset,img,tc)
    print len(tc)
    img.display()
    for i in range(72):
        img = Image(500,500)
        for j in range(len(triset)):
            triset[j][0] = mat * triset[j][0]
        textureTriMtxs(triset, img,tc)
        img.savePpm('../animar/%d.ppm'%(i))
        print i, 'drawn'
