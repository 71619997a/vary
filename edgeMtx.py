from base import Image
from line import line
import matrix

def addPoint(m, x, y, z):
    m.append([x, y, z, 1.])


def addEdge(m, x0, y0, z0, x1, y1, z1):
    addPoint(m, x0, y0, z0)
    addPoint(m, x1, y1, z1)


def drawEdges(m, image, color=(255, 0, 0)):  # draws the edges to an image
    for i in range(0, len(m) - 1, 2):
        lin = line(m[i][0], m[i][1], m[i + 1][0], m[i + 1][1])
        coloredlin = [xy + (color,) for xy in lin]
        image.setPixels(coloredlin)


if __name__ == '__main__':
    m1 = [[2, 2, 3], [3, 2, 2]]
    m2 = [[1, 5], [6.5, 4], [1, -0.7]]
    k1 = 2.5
    k2 = 3.5
    id3 = matrix.id(3)
    id2 = matrix.id(2)
    print 'identity 3x3'
    print matrix.toStr(id3)
    print 'identity 2x2'
    print matrix.toStr(id2)
    print 'm1 2x3'
    print matrix.toStr(m1)
    print 'sanity checks: m1 * id3 = m1, id2 * m1 = m1'
    m1again = matrix.multiply(m1, id3)
    m1evenmore = matrix.multiply(id2, m1)
    print matrix.toStr(m1again)
    print matrix.toStr(m1evenmore)
    print 'testing size mismatch id3 * m1:'
    try:
        matrix.multiply(id3, m1)
    except ArithmeticError:
        print 'it errored, that\'s good'
    print 'm2 3x2'
    print matrix.toStr(m2)
    m12 = matrix.multiply(m1, m2)
    print 'm1 * m2, should be a 2x2'
    print matrix.toStr(m12)
    m21 = matrix.multiply(m2, m1)
    print 'm2 * m1, should be a 3x3'
    print matrix.toStr(m21)
    print '10 * (m2 * m1)'
    print matrix.toStr(matrix.multiply(10, m21))
    print '(m2 * m1) * 10'
    print matrix.toStr(matrix.multiply(m21, 10))
    print '10 * 10'
    print matrix.multiply(10, 10)
    
    img = Image(500, 500)
    for loc in range(0, 500, 4):
        edges = []
        addEdge(edges, 125, loc, 0, loc + 1, 375, 0)
        addEdge(edges, loc + 1, 375, 0, 375, 500 - loc - 2, 0)
        addEdge(edges, 375, 500 - loc - 2, 0, 500 - loc - 3, 125, 0)
        addEdge(edges, 500 - loc - 3, 125, 0, 125, loc + 4, 0)
        drawEdges(edges, img, (255 - loc / 2, loc / 2, 127))  # crossfade r + g
    
    img.display()