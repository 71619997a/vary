from edgeMtx import edgemtx, addTriangle, addEdge

def box(x,y,z,w,h,d):
    p = (x,y,z)
    d = (w,h,d)
    m = edgemtx()
    n = edgemtx()
    for i in xrange(3):
        j = (i + 1) % 3
        ai = [0,0,0]
        aj = [0,0,0]
        ak = [0,0,0]
        ai[i] = d[i]
        aj[j] = d[j]
        for k in xrange(2):
            addTriangle(m, x+ak[0], y+ak[1], z+ak[2], x+ai[0]+ak[0], y+ai[1]+ak[1], z+ai[2]+ak[2], x+aj[0]+ak[0], y+aj[1]+ak[1], z+aj[2]+ak[2])
            addTriangle(m, x+ai[0]+ak[0], y+ai[1]+ak[1], z+ai[2]+ak[2], x+aj[0]+ak[0], y+aj[1]+ak[1], z+aj[2]+ak[2], x+ai[0]+aj[0]+ak[0], y+ai[1]+aj[1]+ak[1], z+ai[2]+aj[2]+ak[2])
            norm = [0,0,0]
            dir = 1 - k * 2
            norm[3 - i - j] = dir
            addEdge(n, *norm*2)
            ak[3 - i - j] += d[3 - i - j]
    return m, n
            
