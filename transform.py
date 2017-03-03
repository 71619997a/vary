import matrix
import math

sin = lambda t: math.sin(t * math.pi / 180)
cos = lambda t: math.cos(t * math.pi / 180)

class TransMatrix(object):
    def __init__(self, lst=-1):
        self.lst = matrix.id(4)
        if lst != -1:
            self.lst = lst

    def __getitem__(self, i):
        return self.lst[i]
    
    def __setitem__(self, i, v):
        self.lst[i] = v

    def __str__(self):
        return matrix.toStr(self.lst)

    def __mul__(self, mat):
        if isinstance(mat, TransMatrix):
            return TransMatrix(matrix.multiply(self.lst, mat.lst))
        else:
            return matrix.multiply(self.lst, mat)
            
    

def T(a, b, c):
    mat = TransMatrix()
    mat[0][3] = a
    mat[1][3] = b
    mat[2][3] = c
    return mat


def S(a, b, c):
    mat = TransMatrix()
    mat[0][0] = a
    mat[1][1] = b
    mat[2][2] = c
    return mat


def relativeScale(oa, ob, oc, sa, sb, sc):
    return T(oa, ob, oc)*S(sa, sb, sc)*T(-oa, -ob, -oc)


def R(axis, t):
    mat = TransMatrix()
    c = cos(t)
    s = sin(t)
    if axis == 'x':
        mat[0][0] = c
        mat[0][1] = -s
        mat[1][0] = s
        mat[1][1] = c
    if axis == 'y':
        mat[1][1] = c
        mat[1][2] = -s
        mat[2][1] = s
        mat[2][2] = c
    if axis == 'z':
        mat[0][0] = c
        mat[0][2] = s
        mat[2][0] = -s
        mat[2][2] = c
    return mat


def iparse(inp):
    return [float(i.strip()) for i in inp.split(' ')]


if __name__ == '__main__':  # parser
    from edgeMtx import edgemtx, addEdge, drawEdges
    from base import Image
    edges = edgemtx()
    trans = TransMatrix()
    while(True):
        try:
            inp = raw_input('\n')
        except EOFError:  # script file
            break
        if inp == 'line':
            inp = raw_input('\n')
            addEdge(edges, *iparse(inp))
        elif inp == 'ident':
            trans = TransMatrix()
        elif inp == 'scale':
            inp = raw_input('\n')
            trans = S(*iparse(inp)) * trans
        elif inp == 'move':
            inp = raw_input('\n')
            trans = T(*iparse(inp)) * trans
        elif inp == 'rotate':
            inp = raw_input('\n')
            axis, t = (i.strip() for i in inp.split(' '))
            trans = R(axis, float(t)) * trans
        elif inp == 'apply':
            edges = trans * edges
        elif inp == 'display':
            img = Image(500, 500)
            drawEdges(edges, img)
            img.display()
        elif inp == 'save':
            print edges
            inp = raw_input('\n').strip()
            img = Image(500, 500)
            drawEdges(edges, img)
            if inp[-4:] == '.ppm':
                img.savePpm(inp)
            else:
                img.saveAs(inp)
