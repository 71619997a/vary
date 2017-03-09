from edgeMtx import edgemtx, addTriangle

def parse(objfile, mtlfile):
    with open(mtlfile) as f:
        mtllines = f.readlines()
    materialNext = ''
    materials = {}
    for line in mtllines:
        if line[:7] == 'newmtl ':
            materialNext = line[7:].strip()
        elif line[:4] == '\tKa ':
            color = tuple(int(float(i) * 255) for i in line[4:].strip().split(' '))
            materials[materialNext] = color
    vertices = []
    triangles = []
    colors = []
    with open(objfile) as f:
        r = f.readlines()
    for line in r:
        if line[:3] == 'v  ':
            coords = tuple(float(i) for i in line[3:].strip().split(' '))
            vertices.append(coords)
        elif line[:2] == 'f ':
            indices = tuple(int(i.split('/')[0]) for i in line[2:].strip().split(' '))
            triangles.append(indices)
        elif line[:7] == 'usemtl ':
            mtl = line[7:].strip()
            col = materials[mtl]
            colors.append((len(triangles), col))
            
    triset = []
    for i in range(len(colors)):
        start, col = colors[i]
        triset.append([edgemtx(), col])
        if i + 1 < len(colors):
            end = colors[i + 1][0]
            thiscol = triangles[start:end]
        else:
            thiscol = triangles[start:]
        for i, j, k in thiscol:
            addTriangle(triset[-1][0], *vertices[i - 1] + vertices[j - 1] + vertices[k - 1]) 
    return triset


