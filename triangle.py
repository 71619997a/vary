from line import line
import transform

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

if __name__ == '__main__':
    from base import Image
    from math import sqrt
    from edgeMtx import edgemtx, addTriangle, drawTriangles, drawColoredTriangles
    from obj import parse
    print 'top tests'
    print topTriangle(10, 0, 5, 4, 6)
    print topTriangle(10, -2, 3, 4, 6)
    print topTriangle(10, 8, 13, 4, 6)
    print 'bot tests'
    print botTriangle(10, 0, 5, 4, 14)
    print botTriangle(10, -2, 3, 4, 14)
    print botTriangle(10, 8, 13, 4, 14)
    print 'tri tests'
    t = triangle(100, 300, 250, 100, 350, 200)
    print t
    colpts = [i + ((255, 0, 0),) for i in t]
    img = Image(500, 500)
    img.setPixels(colpts)
    img.display()
    # icosa
    t = int((1 + sqrt(5)) * 50)
    p = []
    p.append((-100,  t,  0))
    p.append(( 100,  t,  0))
    p.append((-100, -t,  0))
    p.append(( 100, -t,  0))

    p.append(( 0, -100,  t))
    p.append(( 0,  100,  t))
    p.append(( 0, -100, -t))
    p.append(( 0,  100, -t))

    p.append(( t,  0, -100))
    p.append(( t,  0,  100))
    p.append((-t,  0, -100))
    p.append((-t,  0,  100))

    combos = []
    combos.append((0, 11, 5));
    combos.append((0, 5, 1));
    combos.append((0, 1, 7));
    combos.append((0, 7, 10));
    combos.append((0, 10, 11));

    combos.append((1, 5, 9));
    combos.append((5, 11, 4));
    combos.append((11, 10, 2));
    combos.append((10, 7, 6));
    combos.append((7, 1, 8));

    combos.append((3, 9, 4));
    combos.append((3, 4, 2));
    combos.append((3, 2, 6));
    combos.append((3, 6, 8));
    combos.append((3, 8, 9));

    combos.append((4, 9, 5));
    combos.append((2, 4, 11));
    combos.append((6, 2, 10));
    combos.append((8, 6, 7));
    combos.append((9, 8, 1));

    icosatris = edgemtx()
    
    for i, j, k in combos:
        addTriangle(icosatris, *(p[i] + p[j] + p[k]))
    icosatris = transform.T(250, 250, 0) * transform.R('z', 20) * transform.R('x', 20) * icosatris
    mat = transform.T(250, 250, 0) * transform.R('y', 5) * transform.T(-250, -250, 0)
    for i in range(0):
        img = Image(500,500)
        drawTriangles(icosatris, img)
        if i == 0:
            img.display()
        img.savePpm('anim1/%d.ppm' % (i))
        print 'Frame %d done' % (i)
        icosatris = mat * icosatris
    # supa mario baybee
    print 'SM64 test'
    triset = parse('mario.obj', 'mario.mtl')
    coltris = []
    for i in range(len(triset)):
        triset[i][0] = transform.T(250, 400, 0) * transform.R('z', 180) * transform.S(1.5, 1.5, 1.5) * triset[i][0]
    mat = transform.T(250, 400, 0) * transform.R('y', 5) * transform.T(-250, -400, 0)
    for i in range(72):
        img = Image(500,500)
        drawColoredTriangles(triset, img, (180, 180, 180))
        if i == 0:
            img.display()
        img.savePpm('mario/%d.ppm' % (i))
        print 'Frame %d done' % (i)
        for j in range(len(triset)):
            triset[j][0] = mat * triset[j][0]
        
    
    
    
