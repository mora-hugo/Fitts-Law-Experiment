#!/usr/bin/env python3

from cmath import isnan
import sys
import time
import math
import random
import csv
import libs.camera as _cam
import libs.sphere as _sph
import libs.geometry as _geo

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    from OpenGL.GLUT import *
except:
    print('''ERROR: PyOpenGL not installed properly.''')

################################################################################
# GLOBAL VARS

camera = _cam.camera([0, 0, 10], [0, 0, 0])  # main camera
starting_time = time.time()  # starting time of course
mouse = [0, 0]  # mouse current position
animation = False  # (des)activating animation (juste for fun)
spheres = []
current_sequence = 1

bubbleClick = random.choice([True, False])
difficulty = {"3": {"width": 0.5, "distance": (0.5)*((2**3)-1), "occurence": 0}, "4": {"width": 0.35, "distance": (
    0.35)*((2**4)-1), "occurence": 0}, "5": {"width": 0.15, "distance": (0.15)*((2**5)-1), "occurence": 0}}
distance = 4.5
current_difficulty = len(difficulty)
current_numero = 0
difficulty_count = 0
nbCircle = 11
clicks = []
lastTimeClicked = 0
nomUtilisateur = ""
fin = False
################################################################################
# SETUPS


def stopApplication():
    sys.exit(0)


def setupScene():
    '''OpenGL and Scene objects settings
    '''
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (0., 100., 100., 1.))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (.1, .1, .1, 1.))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (.7, .7, .7, 1.))

    glEnable(GL_CULL_FACE)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_NORMALIZE)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    glEnable(GL_DEPTH_TEST)
    glClearColor(.4, .4, .4, 1)

    global spheres
    spheres = create_spheres()


################################################################################
# COMPUTATIONS

def create_spheres():
    _sph.sphere.numero = 0
    s = []
    for i in range(0, nbCircle):
        rad = i*2*math.pi/(nbCircle)  # Change ici pour l'orientation

        x = difficulty[str(current_difficulty)]["distance"]*math.sin(rad)
        y = difficulty[str(current_difficulty)]["distance"]*math.cos(rad)
        s.append(_sph.sphere(
            [x, y, 0], difficulty[str(current_difficulty)]["width"]/2))

    return s


def closest_sphere(sphs, cam, m):
    '''Returns the index of the sphere (in list 'sphs') whose projection is the closest to the 2D position 'm'
    '''
    sphsMin = 0
    distanceMin = 1000000000
    for i in range(0, len(sphs)):
        coord, radius = sphs[i].project(cam)
        distance = math.sqrt((m[0]-coord[0])**2+(m[1]-coord[1])**2)-radius
        if(distance < distanceMin):
            sphsMin = i
            distanceMin = distance
    return sphsMin


################################################################################
# DISPLAY FUNCS

def display_frame():
    glColor(1, 0, 0, 1)


def display_scene(sphs):
    for sphere in spheres:
        glTranslate(sphere.position[0], sphere.position[1], sphere.position[2])
        if(sphere.numero == current_numero):
            glColor(0, 1, 0)
        else:
            glColor(1, 0, 0)
        glutSolidSphere(sphere.radius, 30, 30)
        glTranslate(-sphere.position[0], -
                    sphere.position[1], -sphere.position[2])


def display_2d_disc(p2d, r, c):
    '''Display a disc on a 2d position of the screen
    '''
    w, h = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
    glDisable(GL_LIGHTING)
    glPushMatrix()
    reshape_ortho(w, h)
    glLoadIdentity()
    glTranslate(p2d[0], p2d[1], -1)
    glColor(*c)
    glScale(1, 1, 0.000001)
    glutSolidSphere(r, 20, 20)
    glEnable(GL_LIGHTING)
    reshape_persp(w, h)
    glPopMatrix()


def display_bubble(sphere, pos_2d, color):
    '''display the bubble, i.e display a 2d transparent disc that encompasses the mouse and
        the 2d projection of the sphere
    '''
    glColor(color)

    display_2d_disc(sphere.proj_position, sphere.proj_radius+10, color)


def display():
    '''Global Display function
    '''

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()             # clear the matrix

    ###############
    # Point of View
    gluLookAt(camera.position[0], camera.position[1], camera.position[2],
              camera.viewpoint[0], camera.viewpoint[1], camera.viewpoint[2],
              camera.up[0], camera.up[1], camera.up[2])

    ###############
    # Frame
    display_frame()
    display_scene(spheres)
    if(bubbleClick):
        ind = closest_sphere(spheres, camera, mouse)
        display_bubble(spheres[ind], mouse, [0, 2, 0, .2])
    else:
        sphere = sphereOverred()
        if(sphere != None):
            display_bubble(sphere, mouse, [0, 2, 0, .2])
    glutSwapBuffers()

# Methode retournant la sphere qui est survolé, s'il n'y en a pas, retourne none


def sphereOverred():
    # renvoie la sphere survolé
    global bubbleClick
    global mouse
    global camera

    if(bubbleClick):
        return spheres[closest_sphere(spheres, camera, mouse)]
    for i in range(0, len(spheres)):
        coord, radius = spheres[i].project(camera)

        distance = math.sqrt((mouse[0]-coord[0]) **
                             2+(mouse[1]-coord[1])**2)-radius

        if(distance <= 0):
            return spheres[i]


def reshape_ortho(w, h):
    '''Orthogonal matrix for the projection
        Also called by windows rescaling events
    '''
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, 800, 600, 0, camera.near, camera.far)
    glMatrixMode(GL_MODELVIEW)


def reshape_persp(w, h):
    '''Perspective matrix for the projection
        Called by windows rescaling events
    '''
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(w)/float(h), camera.near, camera.far)
    glMatrixMode(GL_MODELVIEW)


def idle():
    '''Called when opengl has nothing else to do ...
    '''
    pass
    glutPostRedisplay()


################################################################################
# INTERACTION FUNCS

def keyboard(key, x, y):
    '''Called when a keyboard ascii key is pressed
    '''
    if key == b'\x1b':
        stopApplication()
    elif key == b'a':
        global animation
        animation = not animation
    else:
        print("key", key)

# Methode


def clickCircle():
    # Quand un click est detecté
    global current_numero
    global nbCircle
    global clicks
    global lastTimeClicked

    global spheres
    global current_sequence
    global bubbleClick
    global current_difficulty
    global nomUtilisateur
    global difficulty_count
    global fin
    sphere = sphereOverred()  # Recupere la sphere survolé

    # Tableau [Nom,utilisateur, type de click, difficulte, Temps entre le dernier click et celui là ainsi que si la cible a été touchée ou pas]
    clicks.append([nomUtilisateur, "Bubbleclick" if bubbleClick else "normal", current_difficulty, time.time()-lastTimeClicked,
                  sphere != None and sphere.numero == current_numero])
    lastTimeClicked = time.time()

    current_numero = ((current_numero+6) % (nbCircle)) #Change la prochaine cible
    if(current_numero == 0): #Si la cible est la 0, passer a la sequence suivante

        current_sequence = current_sequence + 1

    # Si on passe une sequence (test sur les clicks)
    if(len(clicks) % (nbCircle) == 0):

        if(difficulty_count < 14):  # Si 15 sequences ne se sont pas écoulés alors changer la diffulté

            current_difficulty = getRandomId() #Change la difficulté aléatoire 
            difficulty_count = difficulty_count + 1 
            spheres = []
            spheres = create_spheres() #Recreation des spheres
        elif not fin:  # Si pas changé de mode, changer de mode
            fin = True
            difficulty_count = 0
            bubbleClick = not bubbleClick #Change le type de click
            resetDifficultyOcurrences()
            current_difficulty = getRandomId()
            difficulty_count = difficulty_count + 1
        else:
            print("Fin du programme")
            sauvegarder()
            glutLeaveMainLoop()


def resetDifficultyOcurrences():  # Remet les compteurs des difficultés à 0
    for i in difficulty:
        difficulty[i]["occurence"] = 0


def getRandomId():  # Renvoie un ID rendom si ils peuvent encore apparaitre
    tableau = []

    for i in difficulty:

        if(difficulty[i]["occurence"] < 5):
            tableau.append(i)

    difficulty_choosen = random.choice(tableau)
    # Augmente de 1 l'occurence de la difficulte
    difficulty[difficulty_choosen]["occurence"] = difficulty[difficulty_choosen]["occurence"] + 1

    return difficulty_choosen


def sauvegarder():  # Sauvegarde les clicks dans le fichier infos.csv
    global clicks
    f = open('infos.csv', 'w')

    writer = csv.writer(f)

    for row in clicks:
        writer.writerow(row)

    # close the file
    f.close()


def mouse_clicks(button, state, x, y):
    '''Called when a mouse's button is pressed or released
    button is in [GLUT_LEFT_BUTTON, GLUT_MIDDLE_BUTTON, GLUT_RIGHT_BUTTON],
    state is in [GLUT_DOWN, GLUT_UP]
    '''
    global mouse
    mouse = [x, y]
    if(state == GLUT_DOWN and (button == GLUT_LEFT_BUTTON or button == GLUT_RIGHT_BUTTON)):
        clickCircle()
    glutPostRedisplay()


def mouse_active(x, y):
    '''Called when mouse moves while on of its button is pressed
    '''
    global mouse
    mouse = [x, y]
    glutPostRedisplay()


def mouse_passive(x, y):
    '''Called when mouse hovers over the window
    '''
    global mouse
    mouse = [x, y]
    glutPostRedisplay()


################################################################################
# MAIN

print("Commands:")

print("\tesc:\texit")

print("------------------------------------------")
nomUtilisateur = input("Saisissez votre nom : ")
print("Salut " + nomUtilisateur)
print("------------------------------------------")
lastTimeClicked = time.time()
glutInit(sys.argv)
glutInitDisplayString(b'double rgba depth')
glutInitWindowSize(800, 600)
glutInitWindowPosition(0, 0)
glutCreateWindow(b'Bubble')

setupScene()

glutDisplayFunc(display)
glutReshapeFunc(reshape_persp)
glutKeyboardFunc(keyboard)
glutMouseFunc(mouse_clicks)
glutMotionFunc(mouse_active)
glutPassiveMotionFunc(mouse_passive)
glutIdleFunc(idle)
glutMainLoop()
