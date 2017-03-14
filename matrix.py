from numba import cuda, jit
import numba as nb

@cuda.jit
def mat_23_3n_mult_kernel(m23, m3n, mres, n):
        xIdx = cuda.grid(1)
        if xIdx >= n:
                return
        m3npart = cuda.shared.array((3, 256), dtype=nb.float32)
        m23sh = cuda.shared.array((2, 3), dtype=nb.float32)
        if cuda.threadIdx.x < 32:
                for i in range(cuda.threadIdx.x, 256, 32):
                        m3npart[0][i] = m3n[0][xIdx + i]
                        m3npart[1][i] = m3n[1][xIdx + i]
                        m3npart[2][i] = m3n[2][xIdx + i]
                if cuda.threadIdx.x == 31:
                        for i in range(2):
                                for j in range(3):
                                        m23sh[i][j] = m23[i][j]
        cuda.syncthreads()
        for i in range(2): # 1 out = 
                s = 0
                for j in range(3):
                        s += m23sh[i][j] * m3npart[j][cuda.threadIdx.x]
                mres[i][xIdx] = s

def getcolumn(arr2d, idx):
        col = []
        for row in arr2d:
                col.append(row[idx])
        return col
        
def transpose(m):
        return [getcolumn(m, i) for i in range(len(m[0]))]

def multiply(fac1, fac2):  # chooses between matrix or scalar multiplication
        try:
                a = fac1[0]
                f1scalar = False
        except TypeError:
                f1scalar = True

        try:
                a = fac2[0]
                f2scalar = False
        except TypeError:
                f2scalar = True

        if f1scalar:
                if f2scalar:  # easy case
                        return fac1 * fac2
                else:  # k1 * m2
                        return scalarMult(fac2, fac1)
        else:
                if f2scalar:  # m1 * k2
                        return scalarMult(fac1, fac2)
                else:  # matrix mult
                        return mtxMult(fac1, fac2)

def mtxMult(m1, m2):
        if len(m1[0]) != len(m2):
                raise ArithmeticError("Size mismatch in matrices")
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


def scalarMult(m, k):
        return [[k * i for i in j] for j in m]

def id(n):
        return [[0 if i != j else 1 for i in range(n)] for j in range(n)]

def toStr(m):
        ret = '[\n'
        for row in m:
                ret += '\t'
                for n in row:
                        ret += "{:7.2f}  ".format(n)  # width of 7, 2 decimal prec
                ret += '\n'
        return ret + ']'
