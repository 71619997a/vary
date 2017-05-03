from collections import namedtuple
import math

def _record(props):
    if isinstance(props, str):
        props = props.split(' ')
    class Record:
        __slots__ = props
        def __init__(self, *args, **kwargs):
            i = 0
            for v in args:
                setattr(self, self.__slots__[i], v)
                i += 1
            for k, v in kwargs.iteritems():
                setattr(self, k, v)
    return Record


EDGE = 2
POLY = 3
Point = _record('x y z nx ny nz tx ty')
Texture = _record('type col texture')
Material = _record('amb diff spec exp')
Light = _record('x y z Ia Id Is')
Camera = _record('x y z dx dy dz vx vy vz')

def normalize(*v):
    return normalizeList(list(v))

def normalizeList(v):
    norm = math.sqrt(sum([i**2 for i in v]))
    for i in xrange(len(v)):
        v[i] /= norm
    return v
