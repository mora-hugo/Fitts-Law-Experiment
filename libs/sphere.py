import math
import libs.geometry as _geo

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    from OpenGL.GLUT import *
except:
    print('''ERROR: PyOpenGL not installed properly.''')


class sphere:
    numero = 0 #Attribut de classe permettant de les creer avec leurs propres numéro ( compteur )
    def __init__(self, p, r):
        self.position = p
        self.radius = r
        self.numero = sphere.numero 
        sphere.numero = sphere.numero+1  #Incrementation du numero

    # This function computes and returns the projection of a sphere position on the screen, AND the projected radius (use Thales)
    # Be careful !!! This function takes the current camera stack !!!
    def project(self, camera):
        x1, y1, z1 = gluProject(self.position[0], self.position[1], self.position[2], glGetDoublev(
            GL_MODELVIEW_MATRIX), glGetDoublev(GL_PROJECTION_MATRIX), glGetIntegerv(GL_VIEWPORT))
        x2, y2, z2 = gluProject(self.position[0]+self.radius*camera.up[0], self.position[1]+self.radius*camera.up[1], self.position[2] +
                                self.radius*camera.up[2], glGetDoublev(GL_MODELVIEW_MATRIX), glGetDoublev(GL_PROJECTION_MATRIX), glGetIntegerv(GL_VIEWPORT))
        xFinal = x2-x1
        yFinal = y2-y1
        self.proj_position = [x1, glutGet(GLUT_WINDOW_HEIGHT) - y1]
        self.proj_radius = math.sqrt(xFinal**2+yFinal**2)

        return self.proj_position, self.proj_radius
