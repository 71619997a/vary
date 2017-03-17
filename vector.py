import math

class Vector(object):
    def __init__(self, *args):
        self.comp = list(args)
        self.dim = len(args)
        self.ran = xrange(self.dim)  # skip creation call later
        
    def __mul__(self, other):
        if isinstance(other, Vector):  # no assert checking for dim, gotta go fast
            s = 0
            for i in self.ran:
                s += self.comp[i] * other.comp[i]
            return s
        # otherwise, hope it's a scalar
        return Vector(*[i * other for i in self.comp])

    def __imul__(self, other):  # by scalar only
        for i in self.ran:
            self.comp[i] *= other

    def __rmul__(self, other):
        return self * other
            
    def __add__(self, other):  # by vector only
        return Vector(*[self.comp[i] + other.comp[i] for i in self.ran])

    def __iadd__(self, other):
        for i in self.ran:
            self.comp[i] += other.comp[i]

    def __neg__(self):
        return Vector(*[-c for c in self.comp])

    def __div__(self, other):  # by scalar only
        f = float(other)
        return Vector(*[c / f for c in self.comp])

    def __idiv__(self, other):
        f = float(other)
        for i in self.ran:
            self.comp[i] /= f

    def __getitem__(self, key):
        return self.comp[key]

    def __setitem__(self, key, val):
        self.comp[key] = val

    def __delitem__(self, key):
        del self.comp[key]

    def __int__(self):
        return Vector(*[int(c) for c in self.comp])

    def __float__(self):
        return Vector(*[float(c) for c in self.comp])
            
    def normSquared(self):
        return sum([c ** 2 for c in self.comp])

    def norm(self):
        return math.sqrt(self.normSquared())

    def normalized(self):
        return self / self.norm()

    def normalize(self):
        self /= self.norm()

    def comps(self):
        return tuple(self.comp)

    def to(self, n):
        return Vector(*self.comp[:n])

def concat(*vecs):
    return [i for vec in vecs for i in vec.comp]

def transVecs(*vecs):
    ret = ()
    for i in range(vecs[0].dim):
        ret += Vector(*[vecs[j][i] for j in range(len(vecs))])
    return ret