import numpy
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

def get_ray(x, y):
    """ Utility function to generate a ray from the mouse click position """
    viewport = glGetIntegerv(GL_VIEWPORT)
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    winX = float(x)
    winY = float(viewport[3] - y)
    start = gluUnProject(winX, winY, 0.0, modelview, projection, viewport)
    end = gluUnProject(winX, winY, 1.0, modelview, projection, viewport)
    return start, end

class Viewer(object):
    def __init__(self):
        self.init_interface()
        self.init_opengl()
        self.init_scene()
        self.init_interaction()
        self.setup_callbacks()

    def init_interface(self):
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(1022, 768)
        glutCreateWindow("3D Modeller")

    def setup_callbacks(self):
        glutDisplayFunc(self.render)
        glutIdleFunc(self.render)
        glutKeyboardFunc(self.interaction.handle_keystroke)
        glutMouseFunc(self.interaction.handle_mouse_click)
        glutMotionFunc(self.interaction.handle_mouse_move)
        glutSpecialFunc(self.interaction.handle_special_keystroke)

    def init_opengl(self):
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        glClearColor(0.4, 0.4, 0.4, 0.0)
        glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, (1022/768), 1, 100)
        glMatrixMode(GL_MODELVIEW)

    def init_scene(self):
        self.scene = Scene()
        self.create_sample_scene()

    def create_sample_scene(self):
        cube = Cube()
        cube.translate(-1, 0, 0)
        self.scene.add_node(cube)

        sphere = Sphere()
        sphere.translate(2, 0, 0)
        self.scene.add_node(sphere)

        snow_figure = SnowFigure()
        snow_figure.translate(4, 0, 0)
        self.scene.add_node(snow_figure)

    def init_interaction(self):
        self.interaction = Interaction(self.scene)

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(5, 5, 5, 0, 0, 0, 0, 1, 0)
        self.draw_grid()
        self.draw_axes()
        self.scene.render()
        glutSwapBuffers()

    def draw_grid(self):
        glBegin(GL_LINES)
        glColor3f(0.6, 0.6, 0.6)
        for x in range(-20, 21, 1):
            glVertex3f(x, 0, -20)
            glVertex3f(x, 0, 20)
            glVertex3f(-20, 0, x)
            glVertex3f(20, 0, x)
        glEnd()

    def draw_axes(self):
        axes_length = 5
        glBegin(GL_LINES)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(axes_length, 0, 0)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, axes_length, 0)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, axes_length)
        glEnd()

    def main_loop(self):
        glutMainLoop()

class Scene(object):
    def __init__(self):
        self.node_list = []
        self.selected_node = None

    def add_node(self, node):
        self.node_list.append(node)

    def render(self):
        for node in self.node_list:
            node.render()

class Node(object):
    def __init__(self):
        self.translation_matrix = numpy.identity(4)
        self.is_selected = False

    def translate(self, x, y, z):
        translation = numpy.array([[1, 0, 0, x],
                                   [0, 1, 0, y],
                                   [0, 0, 1, z],
                                   [0, 0, 0, 1]])
        self.translation_matrix = numpy.dot(self.translation_matrix, translation)

    def render(self):
        glPushMatrix()
        glMultMatrixf(numpy.transpose(self.translation_matrix))
        if self.is_selected:
            glColor3f(1.0, 0.5, 0.5)  # Highlight selected object
        else:
            glColor3f(1.0, 1.0, 1.0)  # Default color
        self.draw()
        glPopMatrix()

    def draw(self):
        pass  # To be overridden by subclasses

class Cube(Node):
    def draw(self):
        glColor3f(0.0, 0.0, 1.0)
        glutSolidCube(1)

class Sphere(Node):
    def draw(self):
        glColor3f(1.0, 0.0, 0.0)
        glutSolidSphere(1, 32, 32)

class SnowFigure(Node):
    def __init__(self):
        super().__init__()
        self.children = [Sphere(), Sphere(), Sphere()]
        self.children[0].translate(0, -0.6, 0)
        self.children[1].translate(0, 0.1, 0)
        self.children[2].translate(0, 0.75, 0)

    def render(self):
        for child in self.children:
            child.render()

class Interaction(object):
    def __init__(self, scene):
        self.scene = scene
        self.selected_node = None
        self.last_mouse_pos = None

    def handle_mouse_click(self, button, state, x, y):
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            self.select_object(x, y)
            self.last_mouse_pos = (x, y)
        elif state == GLUT_UP:
            self.selected_node = None  # Deselect on mouse up

    def handle_mouse_move(self, x, y):
        if self.selected_node and self.last_mouse_pos:
            dx = x - self.last_mouse_pos[0]
            dy = y - self.last_mouse_pos[1]
            factor = 0.01
            self.selected_node.translate(dx * factor, -dy * factor, 0)
            self.last_mouse_pos = (x, y)
            glutPostRedisplay()

    def handle_keystroke(self, key, x, y):
        if key == b'w':
            self.selected_node.translate(0, 0, -0.1)
        elif key == b's':
            self.selected_node.translate(0, 0, 0.1)
        glutPostRedisplay()

    def handle_special_keystroke(self, key, x, y):
        if self.selected_node:
            if key == GLUT_KEY_UP:
                self.selected_node.translate(0, 0.1, 0)
            elif key == GLUT_KEY_DOWN:
                self.selected_node.translate(0, -0.1, 0)
            elif key == GLUT_KEY_LEFT:
                self.selected_node.translate(-0.1, 0, 0)
            elif key == GLUT_KEY_RIGHT:
                self.selected_node.translate(0.1, 0, 0)
            glutPostRedisplay()

    def select_object(self, x, y):
        start, end = get_ray(x, y)
        closest_node = None
        min_distance = float('inf')
        for node in self.scene.node_list:
            node_pos = numpy.dot(node.translation_matrix, [0, 0, 0, 1])
            dist = numpy.linalg.norm(numpy.cross(end-start, start-node_pos[:3])/numpy.linalg.norm(end-start))
            if dist < min_distance:
                closest_node = node
                min_distance = dist
        self.scene.selected_node = closest_node
        if self.scene.selected_node:
            self.scene.selected_node.is_selected = True



if __name__ == "__main__":
    viewer = Viewer()
    viewer.main_loop()
