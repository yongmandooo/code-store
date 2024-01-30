from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from Picker import createShader
from Objects import Player, Bullet, Enemy
from Cube_drawer import draw_cube
import numpy as np
import time
import random

event_start_time = 0

class SubWindow:
    """
    SubWindow Class.\n
    Used to display objects in the obj_list, with different camera configuration.
    """

    windows = []
    bullet_list = []
    enemy_list = []
    player = Player()
    is_overlap = False
    timer = 0

    def __init__(self, win, x, y, width, height):
        # identifier for the subwindow
        self.id = glutCreateSubWindow(win, x, y, width, height)
        # projection matrix
        self.projectionMat = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
        # view matrix, you do not need to modify the matrix for now
        self.viewMat = np.eye(4)
        # shader program used to pick objects, and its associated value. DO NOT MODIFY.
        self.pickingShader, self.pickingColor = createShader()
        self.width = width
        self.height = height

    def display(self):
        """
        Display callback function for the subwindow.
        """
        glutSetWindow(self.id)

        self.drawScene()

        glutSwapBuffers()

    def drawScene(self):
        """
        Draws scene with objects to the subwindow.
        """
        glutSetWindow(self.id)

        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if self.id == 2:
            glMultMatrixf(self.projectionMat.T)
        if self.id == 3:
            glMultMatrixf(np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]))
        if self.id == 4:
            glMultMatrixf(np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]))
        if self.id == 5:
            glMultMatrixf(self.projectionMat.T)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glMultMatrixf(self.viewMat.T)

        if self.id == 5:
            gluLookAt(0.1, 0.1, 0.1, 0, 0, 0, 0, 1, 0)

        # self.drawAxes()

        for enemy in SubWindow.enemy_list:
            glColor3f(0.6, 0.1, 0.9)
            enemy.draw()
            # enemy.draw_volume()

        for bullet in SubWindow.bullet_list:
            glColor3f(1, 0, 0)
            bullet.draw()
            for enemy in SubWindow.enemy_list:
                if enemy.min_v[0] <= bullet.pos[0] <= enemy.max_v[0]:
                    if enemy.min_v[1] <= bullet.pos[1] <= enemy.max_v[1]:
                        if enemy.min_v[2] <= bullet.pos[2] <= enemy.max_v[2]:
                            SubWindow.enemy_list.remove(enemy)
                            SubWindow.bullet_list.remove(bullet)

        # draw_cube()

        if SubWindow.is_overlap == False:
            glColor3f(0.7, 0.7, 0.7)
            self.player.draw()
            # self.player.draw_volume()
        # else:
            # self.drawGameOver()
        #     glColor3f(1, 0, 0)
        #     glRasterPos2f(-0.6, 0.0)
        #     text = "GAME OVER"
        #     for char in text:
        #         glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
        #     return

        # 적 생성
        SubWindow.timer += 1
        if SubWindow.timer == 10:
            self.addEnemy(2, 0.0001, "./models/ufo.obj")
        if SubWindow.timer == 1000: # 약 10초 뒤
            self.addEnemy(3, 0.0001, "./models/ufo.obj")
        if SubWindow.timer == 2000: # 약 10초 뒤
            self.addEnemy(4, 0.0002, "./models/ufo.obj")
        if SubWindow.timer == 3000: # 약 10초 뒤
            self.addEnemy(5, 0.0002, "./models/ufo.obj")
        if SubWindow.timer == 4500: # 약 15초 뒤
            self.addEnemy(6, 0.0003, "./models/ufo.obj")
        if SubWindow.timer == 6000: # 약 15초 뒤
            self.addEnemy(7, 0.0003, "./models/ufo.obj")
        if SubWindow.timer == 7500: # 약 15초 뒤
            self.addEnemy(8, 0.0004, "./models/ufo.obj")
        if SubWindow.timer == 9000: # 약 15초 뒤
            self.addEnemy(9, 0.0004, "./models/ufo.obj")
        # if SubWindow.timer % 1000 == 0:
        #     print(f"{SubWindow.timer} 입니다.")

        for enemy in SubWindow.enemy_list:
            num_overlap = 0
            for i in range(3):
                overlap = False
                if enemy.min_v[i] < self.player.max_v[i] < enemy.max_v[i]:
                        overlap = True
                if enemy.min_v[i] < self.player.min_v[i] < enemy.max_v[i]:
                        overlap = True
                if self.player.max_v[i] == enemy.max_v[i]:
                    if self.player.min_v[i] == enemy.min_v[i]:
                        overlap = True
                if overlap:
                    num_overlap += 1
            if num_overlap == 3:
                SubWindow.is_overlap = True
                SubWindow.enemy_list.remove(enemy)
                break


    # def drawGameOver(self):
    #     glClearColor(0, 0, 0, 1)
    #     glColor3f(1, 0, 0)
    #     glRasterPos2f(-0.4, 0.0)
    #     text = "***GAME OVER***"
    #     for char in text:
    #         glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
    #     glFlush()
    #     return


    def drawPickingScene(self):
        """
        Function related to object picking scene drawing.\n
        DO NOT MODIFY THIS.
        """
        glutSetWindow(self.id)

        glClearColor(1, 1, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.pickingShader)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMultMatrixf(self.projectionMat.T)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glMultMatrixf(self.viewMat.T)

        # an object is recognized by its id encoded by unique color
        # for obj in SubWindow.obj_list:
        #     r = (obj.id & 0x000000FF) >> 0
        #     g = (obj.id & 0x0000FF00) >> 8
        #     b = (obj.id & 0x00FF0000) >> 16
        #     glUniform4f(self.pickingColor, r / 255.0, g / 255.0, b / 255.0, 1.0)
        #     obj.draw()

    def mouse(self, button, state, x, y):
        """
        Mouse callback function.
        """
        # button macros: GLUT_LEFT_BUTTON, GLUT_MIDDLE_BUTTON, GLUT_RIGHT_BUTTON
        print(f"Display #{self.id} mouse press event: button={button}, state={state}, x={x}, y={y}")
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            print("Left click")
        if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
            print("Right click")

        self.button = button
        self.modifier = glutGetModifiers()

        glutPostRedisplay()

    def motion(self, x, y):
        """
        Motion (Dragging) callback function.
        """
        print(f"Display #{self.id} mouse move event: x={x}, y={y}, modifer={self.modifier}")

        if self.button == GLUT_LEFT_BUTTON:
            if self.modifier & GLUT_ACTIVE_ALT:
                print("Rotation")
            elif self.modifier & GLUT_ACTIVE_SHIFT:
                print("Scaling")
            else:
                print("Translation")

        glutPostRedisplay()

    def pickObject(self, x, y):
        """
        Object picking function.\n
        obj_id can be used to identify which object is clicked, as each object is assigned with unique id.
        """
        self.drawPickingScene()

        data = glReadPixels(x, self.height - y, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE)

        obj_id = data[0] + data[1] * (2**8) + data[2] * (2**16)

        self.drawScene()

        return obj_id

    def drawAxes(self):
        glPushMatrix()
        glBegin(GL_LINES)
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0.1, 0, 0)
        glColor3f(0, 1, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0.1, 0)
        glColor3f(0, 0, 1)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 0.1)
        glColor3f(1, 1, 1)
        glEnd()
        glPopMatrix()

    def addBullet(self, speed):
        bullet = Bullet(self.player.get_position(), speed)
        SubWindow.bullet_list.append(bullet)

    def addEnemy(self, enemy_num, speed, filename):
        # enemy_num = 5 # Subwindow의 멤버 변수로 만들어 별도로 핸들링 필요
        for _ in range(enemy_num):
            x = random.randrange(1, 161)/100 - 0.8
            y = random.randrange(1, 161)/100 - 0.8
            z = -1 * (random.randrange(1, 101)/200) 
            enemy = Enemy(np.array([x, y, z]), speed, filename) # speed도 조절 필요 default: 0.0001
            SubWindow.enemy_list.append(enemy)

class Viewer:
    width, height = 1250, 500

    def __init__(self):
        pass

    def light(self):
        """
        Light used in the scene.
        """
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)

        # feel free to adjust light colors
        lightAmbient = [0.5, 0.5, 0.5, 1.0]
        lightDiffuse = [0.5, 0.5, 0.5, 1.0]
        lightSpecular = [0.5, 0.5, 0.5, 1.0]
        lightPosition = [1, 1, -1, 0]  # vector: point at infinity
        glLightfv(GL_LIGHT0, GL_AMBIENT, lightAmbient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, lightDiffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, lightSpecular)
        glLightfv(GL_LIGHT0, GL_POSITION, lightPosition)
        glEnable(GL_LIGHT0)

    def idle(self):
        """
        Idle callback function.\n
        Used to update all the subwindows.
        """
        self.display()
        for subWindow in SubWindow.windows:
            subWindow.display()

    def display(self):
        """
        Display callback function for the main window.
        """
        glutSetWindow(self.mainWindow)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(1, 1, 1, 1)

        glutSwapBuffers()

    def reshape(self, w, h):
        """
        Reshape callback function.\n
        Does notihing as of now.
        """
        print(f"reshape to width: {w}, height: {h}")

        glutPostRedisplay()

    def keyboard(self, key, x, y):
        """
        Keyboard callback function.
        """
        print(f"Display #{glutGetWindow()} keyboard event: key={key}, x={x}, y={y}")
        if glutGetModifiers() & GLUT_ACTIVE_SHIFT:
            print("shift pressed")
        if glutGetModifiers() & GLUT_ACTIVE_ALT:
            print("alt pressed")
        if glutGetModifiers() & GLUT_ACTIVE_CTRL:
            print("ctrl pressed")

        if key == b" ":
            global event_start_time
            if event_start_time == 0:
                event_start_time = time.time()
                print(event_start_time)

        # if key == b"s":
        #     SubWindow.addEnemy(SubWindow)

        glutPostRedisplay()

    def special(self, key, x, y):
        """
        Special key callback function.
        """
        print(f"Display #{glutGetWindow()} special key event: key={key}, x={x}, y={y}")

        if key == 102:
            SubWindow.player.move_right()
        
        if key == 100:
            SubWindow.player.move_left()

        if key == 101:
            SubWindow.player.move_up()

        if key == 103:
            SubWindow.player.move_down()

        glutPostRedisplay()

    def special_up(self, key, x, y):
        """
        Special key callback function.
        """
        print(f"Display #{glutGetWindow()} special key event: key={key}, x={x}, y={y}")

        global event_start_time
        if key == 32: 
            SubWindow.addBullet(SubWindow, (time.time() - event_start_time) * 0.02)
            event_start_time = 0
        
        glutPostRedisplay()

    def run(self):
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)

        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(0, 0)
        self.mainWindow = glutCreateWindow(b"CG Project")
        glutDisplayFunc(self.display)
        glutIdleFunc(self.idle)
        glutReshapeFunc(self.reshape)

        # # sub-windows
        # # xy plane
        # SubWindow.windows.append(SubWindow(self.mainWindow, 0, 0, self.width // 2, self.height // 2))
        # # zy plane
        # SubWindow.windows.append(SubWindow(self.mainWindow, self.width // 2 + 1, 0, self.width // 2, self.height // 2))
        # SubWindow.windows[1].viewMat = np.array([[0, 0, -1, 0], [0, 1, 0, 0], [-1, 0, 0, 0], [0, 0, 0, 1]])
        # # xz plane
        # SubWindow.windows.append(SubWindow(self.mainWindow, 0, self.height // 2 + 1, self.width // 2, self.height // 2))
        # SubWindow.windows[2].viewMat = np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, -1, 0, 0], [0, 0, 0, 1]])
        # # 3D
        # SubWindow.windows.append(
        #     SubWindow(self.mainWindow, self.width // 2 + 1, self.height // 2 + 1, self.width // 2, self.height // 2)
        # )

        # sub-windows
        # xy plane
        SubWindow.windows.append(SubWindow(self.mainWindow, 0, 0, 500, 500))
        # zy plane
        SubWindow.windows.append(SubWindow(self.mainWindow, 501, 0, 500, 500))
        SubWindow.windows[1].viewMat = np.array([[0, 0, -1, 0], [0, 1, 0, 0], [-1, 0, 0, 0], [0, 0, 0, 1]])
        # xz plane
        SubWindow.windows.append(SubWindow(self.mainWindow, 1002, 0, 250, 250))
        SubWindow.windows[2].viewMat = np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, -1, 0, 0], [0, 0, 0, 1]])
        # 3D
        SubWindow.windows.append(
            SubWindow(self.mainWindow, 1002, 251, 250, 250)
        )

        for subWindow in SubWindow.windows:
            # print(subWindow.id)
            glutSetWindow(subWindow.id)
            glutDisplayFunc(subWindow.display)
            glutKeyboardFunc(self.keyboard)
            glutSpecialFunc(self.special)
            glutSpecialUpFunc(self.special_up)
            glutMouseFunc(subWindow.mouse)
            glutMotionFunc(subWindow.motion)

            self.light()

        glutMainLoop()


if __name__ == "__main__":
    viewer = Viewer()
    viewer.run()
