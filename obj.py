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
            materials[materialNext] = {'color':color}
        elif line[:8] == '\tmap_Ka ':
            materials[materialNext]['texture'] = line[8:].strip()
    vertices = []
    tcors = []
    triangles = []
    colors = []
    with open(objfile) as f:
        r = f.readlines()
    for line in r:
        if line[:3] == 'v  ':
            coords = tuple(float(i) for i in line[3:].strip().split(' '))
            vertices.append(coords)
        elif line[:3] == 'vt ':
            coords = tuple(float(i) for i in line[3:].strip().split(' '))[:2]
            print coords
            tcors.append(coords)
        elif line[:2] == 'f ':
            indices = tuple(int(i.split('/')[0]) for i in line[2:].strip().split(' '))
            tindices = tuple(int(i.split('/')[1]) for i in line[2:].strip().split(' '))
            triangles.append((indices,tindices))
        elif line[:7] == 'usemtl ':
            mtl = line[7:].strip()
            mat = materials[mtl]
            if 'texture' in mat:
              colors.append((len(triangles), mat['texture'], mat['color']))
            else:
              colors.append((len(triangles), None, mat['color']))
    triset = []
    for i in range(len(colors)):
        start, texture, col = colors[i]
        triset.append([edgemtx(),[[],[]],texture,col])
        if i + 1 < len(colors):
            end = colors[i + 1][0]
            thiscol = triangles[start:end]
        else:
            thiscol = triangles[start:]
        for ind, tind in thiscol:
            i,j,k = ind
            x,y,z = tind
            print x, y, z
            print tcors[x-1][0]
            addTriangle(triset[-1][0], *vertices[i - 1] + vertices[j - 1] + vertices[k - 1])
            triset[-1][1][0].extend([tcors[x - 1][0], tcors[y - 1][0], tcors[z - 1][0]])
            triset[-1][1][1].extend([tcors[x - 1][1], tcors[y - 1][1], tcors[z - 1][1]])
    return triset
