import mdl
from transform import TransMatrix
import transform
from edgeMtx import edgemtx, addEdge, addTriangle, drawEdges, addBezier, addHermite, addCircle, drawTriangles
from base import Image
from render import renderTriangle, phongShader, drawObjectsNicely, drawObjects
import shape
from sys import argv

EDGE = 2
POLY = 3
def run(filename):
    """
    This function runs an mdl script
    """
    color = [255, 255, 255]
    tmp = TransMatrix()

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return


    cstack = [TransMatrix()]
    frc = 0
    img = Image(500, 500)
    objects = []
    for command in commands:
        inp = command[0]
        if inp == 'line':
            edges = edgemtx()
            addEdge(edges, *command[1:7])
            edges = cstack[-1] * edges
            objects.append((EDGE, edges))
            #drawEdges(cstack[-1] * edges, img)
        elif inp == 'ident':
            cstack[-1] = TransMatrix()
        elif inp == 'scale':
            cstack[-1] *= transform.S(*command[1:4])
        elif inp == 'move':
            cstack[-1] *= transform.T(*command[1:4])
        elif inp == 'rotate':
            cstack[-1] *= transform.R(*command[1:3])
        elif inp == 'display':
            drawObjects(objects, img)
            img.flipUD().display()
        elif inp == 'save':
            drawObjects(objects, img)
            if inp[-4:] == '.ppm':
                img.flipUD().savePpm(command[1])
            else:
                img.flipUD().saveAs(command[1])
        elif inp == 'saveframe':
            drawObjects(objects, img)
            img.flipUD().savePpm('%s%d.ppm' % (command[1], frc))
            frc += 1
        elif inp == 'circle':
            edges = edgemtx()
            addCircle(*(edges,)+command[1:5]+(.01,))
            edges = cstack[-1] * edges
            objects.append((EDGE, edges))
            #drawEdges(cstack[-1] * edges, img)
        elif inp == 'bezier':
            edges = edgemtx()
            addBezier(*(edges,)+command[1:9]+(.01,))
            edges = cstack[-1] * edges
            objects.append((EDGE, edges))
            #drawEdges(cstack[-1] * edges, img)
        elif inp == 'hermite':
            edges = edgemtx()
            addHermite(*(edges,)+command[1:9]+(.01,))
            edges = cstack[-1] * edges
            objects.append((EDGE, edges))
            #drawEdges(cstack[-1] * edges, img)
        elif inp == 'clear':
            img = Image(500, 500)
        elif inp == 'clearstack':
            cstack = [TransMatrix()]
        elif inp == 'box':
            polys = edgemtx()
            shape.addBox(*(polys,) + command[1:7])
            polys = cstack[-1] * polys
            objects.append((POLY, polys))
            #drawTriangles(cstack[-1] * polys, img, wireframe=True)
        elif inp == 'sphere':
            polys = edgemtx()
            shape.addSphere(*(polys,) + command[1:5] + (.05,))
            polys = cstack[-1] * polys
            objects.append((POLY, polys))
            #drawTriangles(cstack[-1] * polys, img, wireframe=True)
        elif inp == 'torus':
            polys = edgemtx()
            shape.addTorus(*(polys,) + command[1:6] + (.05, .05))
            polys = cstack[-1] * polys
            objects.append((POLY, polys))
            #drawTriangles(cstack[-1] * polys, img, wireframe=True)
        elif inp == 'push':
            cstack.append(cstack[-1].clone())
        elif inp == 'pop':
            cstack.pop()











    
    stack = [ [x[:] for x in tmp] ]
    img = Image(500, 500)
    tmp = []
    step = 0.1
    for command in commands:
        print command

if __name__ == '__main__':
    if len(argv) < 2:
        raise Exception('\nUsage: python script.py [mdl file]')
    run(argv[1])
