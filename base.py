from random import randint, random
import math
import os
import re

WIDTH = 500
HEIGHT = 500

class Image(object):
        def __init__(self, w, h):
                self.pixels = [[(0,0,0) for _ in xrange(w)] for __ in xrange(h)]
                self.width = w
                self.height = h

        def savePpm(self, name):
                with open(name, 'w') as f:
                        f.write('P3 %d %d 255\n' % (self.width, self.height))
                        for row in self.pixels:
                                for rgb in row:
                                        f.write('%d %d %d ' % rgb)
                                f.write('\n')


        def saveAs(self, name):
                self.savePpm('temp.ppm')
                os.system('convert temp.ppm ' + name)
                os.system('rm temp.ppm')

        def display(self):  # displays image and deletes after
                self.savePpm('temp.ppm')
                os.system('display temp.ppm')
                os.system('rm temp.ppm')

        def setPixel(self, x, y, col):
                self.pixels[y][x] = col

        def setPixels(self, ls):  # list of (x, y, color)
                for x, y, col in ls:
                        self.setPixel(x, y, col)
                
        def fromFunc(self, func):
                for y in xrange(self.height):
                        for x in xrange(self.width):
                                setPixel(x, y, func(x, y))

        @staticmethod
        def fromImage(filename):  # use as img = Image.fromImage(...)
                with open(filename) as f:
                        body = f.read()
                words = filter(None, re.split('[ \n\t]+', body))
                assert words[0] == 'P3'
                vals = [int(i) for i in words[1:]]
                assert len(vals) % 3 == 0
                width = int(vals[0])
                height = int(vals[1])
                img = Image(width, height)
                maxcol = int(vals[2])
                if not maxcol == 255:
                        scalefac = 255. / maxcol
                        vals = [int(i * scalefac) for i in vals]
                for i in range(3, len(vals), 3):
                        s3 = i / 3 - 1
                        rgb = tuple(vals[i : i+3])
                        img.setPixel(s3 % width, s3 / width, rgb)
                return img

        
def getcolumn(arr2d, idx):
        col = []
        for row in arr2d:
                col.append(row[idx])
        return col
        
def transpose(m):
        return [getcolumn(m, i) for i in range(len(m[0]))]

def mtxMult(m1, m2):
        m2t = transpose(m2)
        mret = []
        for row in m1:
                mret.append([])
                for i in range(len(m2t)):
                        col = m2t[i]
                        dot = 0
                        for j in range(len(row)):
                                dot += col[j] * row[j]
                        mret[-1].append(dot)
        return mret


def scalarMult(k, m):
        return [[k * i for i in j] for j in m]

def idMtx(n):
        return [[0 if i != j else 1 for i in range(n)] for j in range(n)]

def mtxStr(m):
        ret = '[\n'
        for row in m:
                ret += '\t'
                for n in row:
                        ret += str(n) + '\t'
                ret += '\n'
        return ret + ']'
