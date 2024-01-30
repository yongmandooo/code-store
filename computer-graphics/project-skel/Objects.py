from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
from obj_loader import load_obj, draw_obj

class Object:
    cnt = 0

    def __init__(self):
        # Do NOT modify: Object's ID is automatically increased
        self.id = Object.cnt
        Object.cnt += 1
        # self.mat needs to be updated by every transformation
        self.mat = np.eye(4)

    def draw(self):
        raise NotImplementedError

class Player(Object):
    def __init__(self):
        super().__init__()
        self.player_z = 0.7
        self.step = 0.03
        self.obj_filename = "./models/jet.obj" # vscode debugger 안쓸때 경로 수정 필요
        # self.texture_filename = "./Beriev_A50/textures/Beriev_2048.png" # vscode debugger 안쓸때 경로 수정 필요
        self.vertices, self.normals, self.faces = load_obj(self.obj_filename)
        self.min_v = [min(self.vertices[:, 0]) * 0.004, min(self.vertices[:, 1]) * 0.004,
                      min(self.vertices[:, 2]) * 0.004 + self.player_z]
        self.max_v = [max(self.vertices[:, 0]) * 0.004, max(self.vertices[:, 1]) * 0.004,
                      max(self.vertices[:, 2]) * 0.004 + self.player_z]

    def draw(self):
        glPushMatrix()
        glMultMatrixf(self.mat.T)
        glTranslatef(0, 0, self.player_z)
        draw_obj(self.vertices * 0.004, self.normals, self.faces)
        glPopMatrix()

        # glPushMatrix()
        # glMultMatrixf(self.mat.T)
        # glTranslatef(0, 0, self.player_z)
        # glutSolidSphere(0.05, 10, 10)
        # glPopMatrix()

    def move_right(self):
        translation_matrix = np.array([
            [1, 0, 0, self.step],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        self.mat = np.dot(self.mat, translation_matrix)
        self.min_v[0] += self.step
        self.max_v[0] += self.step

    def move_left(self):
        translation_matrix = np.array([
            [1, 0, 0, -self.step],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        self.mat = np.dot(self.mat, translation_matrix)
        self.min_v[0] -= self.step
        self.max_v[0] -= self.step

    def move_up(self):
        translation_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, self.step],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        self.mat = np.dot(self.mat, translation_matrix)
        self.min_v[1] += self.step
        self.max_v[1] += self.step

    def move_down(self):
        translation_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, -self.step],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        self.mat = np.dot(self.mat, translation_matrix)
        self.min_v[1] -= self.step
        self.max_v[1] -= self.step

    def get_position(self):
        return np.array([self.mat[0][3], self.mat[1][3], self.player_z])

    def draw_volume(self):
        glBegin(GL_LINES)
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.min_v[0], self.min_v[1], self.min_v[2])
        glVertex3f(self.min_v[0], self.min_v[1], self.max_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.min_v[0], self.min_v[1], self.min_v[2])
        glVertex3f(self.min_v[0], self.max_v[1], self.min_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.min_v[0], self.min_v[1], self.min_v[2])
        glVertex3f(self.max_v[0], self.min_v[1], self.min_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.max_v[0], self.min_v[1], self.min_v[2])
        glVertex3f(self.max_v[0], self.max_v[1], self.min_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.max_v[0], self.min_v[1], self.min_v[2])
        glVertex3f(self.max_v[0], self.min_v[1], self.max_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.min_v[0], self.max_v[1], self.min_v[2])
        glVertex3f(self.max_v[0], self.max_v[1], self.min_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.min_v[0], self.max_v[1], self.min_v[2])
        glVertex3f(self.min_v[0], self.max_v[1], self.max_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.min_v[0], self.min_v[1], self.max_v[2])
        glVertex3f(self.max_v[0], self.min_v[1], self.max_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.min_v[0], self.min_v[1], self.max_v[2])
        glVertex3f(self.min_v[0], self.max_v[1], self.max_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.max_v[0], self.max_v[1], self.min_v[2])
        glVertex3f(self.max_v[0], self.max_v[1], self.max_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.max_v[0], self.min_v[1], self.max_v[2])
        glVertex3f(self.max_v[0], self.max_v[1], self.max_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.min_v[0], self.max_v[1], self.max_v[2])
        glVertex3f(self.max_v[0], self.max_v[1], self.max_v[2])
        glEnd()

class Bullet(Object):
    def __init__(self, pos, speed):
        super().__init__()
        self.pos = pos
        self.speed = speed
        self.direction = np.array([0, 0, -1.0])

    def draw(self):
        glPushMatrix()
        glMultMatrixf(self.mat.T)
        glTranslatef(self.pos[0], self.pos[1], self.pos[2])
        glutSolidSphere(0.01, 10, 10)
        self.pos += (self.direction/np.linalg.norm(self.direction)) * self.speed
        glPopMatrix() 

class Enemy(Object):
    def __init__(self, pos, speed, filename):
        super().__init__()
        self.pos = pos
        self.speed = speed
        self.direction = np.array([0, 0, 1.0])
        self.obj_filename = filename # vscode debugger 안쓸때 경로 수정 필요
        self.vertices, self.normals, self.faces = load_obj(self.obj_filename)
        self.min_v = [min(self.vertices[:, 0])*0.04 + pos[0], min(self.vertices[:, 1])*0.04 + pos[1], min(self.vertices[:, 2])*0.04 + pos[2]]
        self.max_v = [max(self.vertices[:, 0])*0.04 + pos[0], max(self.vertices[:, 1])*0.04 + pos[1], max(self.vertices[:, 2])*0.04 + pos[2]]

    def draw(self):
        glPushMatrix()
        glMultMatrixf(self.mat.T)
        glTranslatef(self.pos[0], self.pos[1], self.pos[2])
        draw_obj(self.vertices * 0.04, self.normals, self.faces)
        self.pos += (self.direction/np.linalg.norm(self.direction)) * self.speed
        self.min_v += (self.direction/np.linalg.norm(self.direction)) * self.speed
        self.max_v += (self.direction / np.linalg.norm(self.direction)) * self.speed
        glPopMatrix()

    def draw_volume(self):
        glBegin(GL_LINES)
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.min_v[0], self.min_v[1], self.min_v[2])
        glVertex3f(self.min_v[0], self.min_v[1], self.max_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.min_v[0], self.min_v[1], self.min_v[2])
        glVertex3f(self.min_v[0], self.max_v[1], self.min_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.min_v[0], self.min_v[1], self.min_v[2])
        glVertex3f(self.max_v[0], self.min_v[1], self.min_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.max_v[0], self.min_v[1], self.min_v[2])
        glVertex3f(self.max_v[0], self.max_v[1], self.min_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.max_v[0], self.min_v[1], self.min_v[2])
        glVertex3f(self.max_v[0], self.min_v[1], self.max_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.min_v[0], self.max_v[1], self.min_v[2])
        glVertex3f(self.max_v[0], self.max_v[1], self.min_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.min_v[0], self.max_v[1], self.min_v[2])
        glVertex3f(self.min_v[0], self.max_v[1], self.max_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.min_v[0], self.min_v[1], self.max_v[2])
        glVertex3f(self.max_v[0], self.min_v[1], self.max_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.min_v[0], self.min_v[1], self.max_v[2])
        glVertex3f(self.min_v[0], self.max_v[1], self.max_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.max_v[0], self.max_v[1], self.min_v[2])
        glVertex3f(self.max_v[0], self.max_v[1], self.max_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.max_v[0], self.min_v[1], self.max_v[2])
        glVertex3f(self.max_v[0], self.max_v[1], self.max_v[2])
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(self.min_v[0], self.max_v[1], self.max_v[2])
        glVertex3f(self.max_v[0], self.max_v[1], self.max_v[2])
        glEnd()