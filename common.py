from collections import namedtuple

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
Point = _record('x y z nx ny nz tx ty')
Texture = _record('type col texture')
Material = _record('amb diff spec exp')
Light = _record('x y z Ia Id Is')
Camera = _record('x y z dx dy dz vx vy vz')