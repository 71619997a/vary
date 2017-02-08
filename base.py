from random import randint, random
import math
import os

WIDTH = 500
HEIGHT = 500

class Image(object):
        def __init__(self, w, h):
                self.pixels = [[(0,0,0) for _ in xrange(w)] for __ in xrange(h)]
                self.width = w
                self.height = h

        def drawTo(self, name):
                with open(name, 'w') as f:
                        f.write('P3 %d %d 255\n' % (self.width, self.height))
                        for row in self.pixels:
                                for rgb in row:
                                        f.write('%d %d %d ' % rgb)
                                f.write('\n')
                
        def setPixel(self, x, y, col):
                self.pixels[y][x] = col

        def setPixels(self, ls):  # list of (x, y, color)
                for x, y, col in ls:
                        self.setPixel(x, y, col)
                
        def fromFunc(self, func):
                for y in xrange(self.height):
                        for x in xrange(self.width):
                                setPixel(x, y, func(x, y))


