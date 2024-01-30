from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from Picker import createShader
import numpy as np
import time
from objloader import *


# PA1-Task2: function from conversion mouse coordinate
event_start_time = 0
def conversion(x, y):
    x = (x - 200) / 200
    y = (200 - y) / 200

    return (x, y)


def return_small(x, y):
    if x < y:
        return x
    else:
        return y

#PA3: drawing sandbox
def draw_cube():
    vertices= (
    (0.5, -0.5, -0.5),
    (0.5, 0.5, -0.5),
    (-0.5, 0.5, -0.5),
    (-0.5, -0.5, -0.5),
    (0.5, -0.5, 0.5),
    (0.5, 0.5, 0.5),
    (-0.5, -0.5, 0.5),
    (-0.5, 0.5, 0.5)
    )

    edges = (
        (0,1),
        (0,3),
        (0,4),
        (2,1),
        (2,3),
        (2,7),
        (6,3),
        (6,4),
        (6,7),
        (5,1),
        (5,4),
        (5,7)
        )
    
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()



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


class Teapot(Object):
    def __init__(self):
        super().__init__()

    def draw(self):
        glPushMatrix()
        glMultMatrixf(self.mat.T)
        glutSolidTeapot(0.2)
        glPopMatrix()

#PA3: object for bullet implementation
class Bullet(Object):
    def __init__(self, speed):
        super().__init__()
        self.pos = np.array([1.0, 1.0, 1.0])
        self.speed = speed
        self.direction = np.array([-1.0, -1.0, -1.0])
        self.is_in_sandbox = False
        self.paused = False

    def sandbox_detection(self):
        if (((self.pos[0] > -0.5) and (self.pos[0] < 0.5)) and 
            ((self.pos[1] > -0.5) and (self.pos[1] < 0.5)) and 
            ((self.pos[2] > -0.5) and (self.pos[2] < 0.5))):
            self.is_in_sandbox = True

        if self.is_in_sandbox:
            if self.pos[0] > 0.5 or self.pos[0] < -0.5:
                self.direction[0] = self.direction[0] * -1

            if self.pos[1] > 0.5 or self.pos[1] < -0.5:
                self.direction[1] = self.direction[1] * -1

            if self.pos[2] > 0.5 or self.pos[2] < -0.5:
                self.direction[2] = self.direction[2] * -1

    def draw(self):
        glPushMatrix()
        glMultMatrixf(self.mat.T)
        glTranslatef(self.pos[0], self.pos[1], self.pos[2])
        glutSolidSphere(0.02, 10, 10)
        if not self.paused:
            self.sandbox_detection()
            self.pos += (self.direction/np.linalg.norm(self.direction)) * self.speed
        glPopMatrix() 

#PA3: object for bunny implementation
class Bunny(Object):
    def __init__(self):
        super().__init__()
        self.vertices = []
        self.normals = []
        self.indices = []
        self.obj_file = open("./bunny_1024.obj", 'r')
        self.x_max = 0
        self.x_min = 0
        self.y_max = 0
        self.y_min = 0
        self.z_max = 0
        self.z_min = 0
        self.load_obj()
        self.aabb_vertices= (
        (self.x_max, self.y_min, self.z_min),
        (self.x_max, self.y_max, self.z_min),
        (self.x_min, self.y_max, self.z_min),
        (self.x_min, self.y_min, self.z_min),
        (self.x_max, self.y_min, self.z_max),
        (self.x_max, self.y_max, self.z_max),
        (self.x_min, self.y_min, self.z_max),
        (self.x_min, self.y_max, self.z_max)
        )
        self.aabb_edges = (
        (0,1),
        (0,3),
        (0,4),
        (2,1),
        (2,3),
        (2,7),
        (6,3),
        (6,4),
        (6,7),
        (5,1),
        (5,4),
        (5,7)
        )
        self.is_aabb = False
        self.time_spend = 0
        self.collision_detected = False

    def load_obj(self):
        while True:
            line = self.obj_file.readline()
            if not line: break
            line = line.split()

            if line[0] == 'v':
                vertice = [float(line[1]), float(line[2]), float(line[3])]
                self.vertices.append(vertice)
            elif line[0] == 'vn':
                normal = [float(line[1]), float(line[2]), float(line[3])]
                self.normals.append(normal)
            elif line[0] == 'f':
                index = []
                for i in range(3):
                    parsing_index = i + 1
                    parsing_target = line[parsing_index]
                    parsing_target = parsing_target.split('//')
                    if len(parsing_target[0]) != 0 and len(parsing_target[len(parsing_target)-1]) != 0:
                        index.append([int(parsing_target[0]), int(parsing_target[len(parsing_target)-1])])
                self.indices.append(index)

        self.x_max = max(list(zip(*self.vertices))[0]) * 0.2
        self.x_min = min(list(zip(*self.vertices))[0]) * 0.2
        self.y_max = max(list(zip(*self.vertices))[1]) * 0.2
        self.y_min = min(list(zip(*self.vertices))[1]) * 0.2
        self.z_max = max(list(zip(*self.vertices))[2]) * 0.2
        self.z_min = min(list(zip(*self.vertices))[2]) * 0.2

    def draw(self):
        if self.collision_detected:
            self.time_spend += 1
            print(self.time_spend)
        glPushMatrix()
        glMultMatrixf(self.mat.T)
        if self.is_aabb:
            glBegin(GL_LINES)
            for edge in self.aabb_edges:
                for vertex in edge:
                    glVertex3fv(self.aabb_vertices[vertex])
            glEnd()
        glScalef(0.2, 0.2, 0.2)
        glBegin(GL_TRIANGLES)
        for index in self.indices:
            for index_value in index:
                vertex_index = index_value[0]
                normal_index = index_value[1]
                vertex = self.vertices[vertex_index - 1]
                normal = self.normals[normal_index - 1]
                glNormal3fv(normal)
                glVertex3fv(vertex)
        glEnd()
        glPopMatrix()

class SubWindow:
    """
    SubWindow Class.\n
    Used to display objects in the obj_list, with different camera configuration.
    """

    windows = []
    path_list = []

    # PA1-Task5: list containing the objects which should be represented in window, and selected
    obj_list = []
    selected_obj_list = []

    target_obj = []
    detection_obj = []

    col_detected_obj_id = []

    is_aabb = False
    paused = True

    # PA2-Task4: configure default environmnet
    camera_position = np.array([1.0, 1.0, 1.0])
    camera_rot_mat = np.eye(3)
    camera_at = np.array([0.0, 0.0, 0.0])
    camera_up_vec = np.array([0.0, 1.0, 0.0])
    camera_trans = np.array([0.0, 0.0, 0.0])

    fov = 0
    scale_num = 5

    def __init__(self, win, x, y, width, height):
        print("initialize subwindow")
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

    #PA3: function for static collision dectection
    def static_collision_detection(self):
        if len(self.target_obj) > 0:
            for target_obj in self.target_obj:
                if target_obj.x_max >= 0.5 or target_obj.y_max >= 0.5 or target_obj.z_max >= 0.5:
                    return ["sandbox", target_obj]
                
                if target_obj.x_min <= -0.5 or target_obj.y_min <= -0.5 or target_obj.z_min <= -0.5:
                    return ["sandbox", target_obj]

        if len(self.target_obj) > 0 and len(self.detection_obj) > 0:
            for target_obj in self.target_obj:
                detection_list = []
                for detection_obj in self.detection_obj:
                    detection_list = [0, 0, 0]
                    if ((target_obj.x_max >= detection_obj.x_min) and (target_obj.x_min <= detection_obj.x_min)) or ((target_obj.x_max >= detection_obj.x_max) and (target_obj.x_min <= detection_obj.x_max)):
                        print("x is overlapped")
                        detection_list[0] = 1
                    
                    if ((target_obj.y_max >= detection_obj.y_min) and (target_obj.y_min <= detection_obj.y_min)) or ((target_obj.y_max >= detection_obj.y_max) and (target_obj.y_min <= detection_obj.y_max)):
                        print("y is overlapped")
                        detection_list[1] = 1
                    
                    if ((target_obj.z_max >= detection_obj.z_min) and (target_obj.z_min <= detection_obj.z_min)) or ((target_obj.z_max >= detection_obj.z_max) and (target_obj.z_min <= detection_obj.z_max)):
                        print("z is overlapped")
                        detection_list[2] = 1

                    print(detection_list)
                    if detection_list[0] != 0 and detection_list[1] != 0 and detection_list[2] != 0:
                        print("collition")
                        return ["bunny", target_obj]
                
        return ["", None]
            

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

        glViewport(0, 0, glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT))
        w = glutGet(GLUT_WINDOW_WIDTH)
        h = glutGet(GLUT_WINDOW_HEIGHT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMultMatrixf(self.projectionMat)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        if self.id == 2:
            glMultMatrixf(np.array([[400/w, 0, 0, 0],
                                [0, 400/h, 0, 0],
                                [0, 0, 1, 0],
                                [0, 0, 0, 1],]))
        elif self.id == 3:
            glMultMatrixf(np.array([[0, 0, -1, 0],
                                [0, 400/h, 0, 0],
                                [400/w, 0, 0, 0],
                                [0, 0, 0, 1],]))
        elif self.id == 4:
            glMultMatrixf(np.array([[400/w, 0, 0, 0],
                                [0, 0, -1, 0],
                                [0, 400/h, 0, 0],
                                [0, 0, 0, 1],]))
        elif self.id == 5:
            glMultMatrixf(self.viewMat.T)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glMultMatrixf(np.eye(4))

            #PA2-Task2: implement orthographic/perspective projection according to fov(it manages the distance in the part of implementing interface for fov)
            if self.fov == 0:
                glOrtho(-5 * w/400, 5 * w/400, -5 * h/400, 5 * h/400, -10, 10)
            else:
                gluPerspective(
                    self.fov,
                    glutGet(GLUT_WINDOW_WIDTH) / glutGet(GLUT_WINDOW_HEIGHT),
                    0.1,
                    200,
                )

            gluLookAt(
                self.camera_position[0],
                self.camera_position[1],
                self.camera_position[2],
                self.camera_at[0],
                self.camera_at[1],
                self.camera_at[2],
                self.camera_up_vec[0],
                self.camera_up_vec[1],
                self.camera_up_vec[2],
            )
            glScalef(self.scale_num, self.scale_num, self.scale_num)

        self.drawAxes(0, 0, 0,)

        for obj in SubWindow.obj_list:
            if obj.id in [i[1] for i in self.col_detected_obj_id]:
                print(obj.time_spend)
                glColor3f(0, 1, 0)
            else:
                if obj.id in self.selected_obj_list:
                    glColor3f(0, 0, 1)
                else:
                    glColor3f(1, 1, 1)

            obj.draw()

        glColor3f(1, 1, 1)
        draw_cube()

        
        if len(self.col_detected_obj_id) > 0:
            for reason, target_id in self.col_detected_obj_id:
                for obj in self.obj_list:
                    if obj.id == target_id and obj.time_spend > 5:
                        if reason == "create":
                            self.obj_list.remove(obj)
                            self.col_detected_obj_id.remove([reason, obj.id])
                        else:
                            obj.time_spend = 0
                            obj.collision_detected = False
                            self.col_detected_obj_id.remove([reason, obj.id])
                

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
        glMultMatrixf(self.projectionMat)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glMultMatrixf(self.viewMat.T)

        # an object is recognized by its id encoded by unique color
        for obj in SubWindow.obj_list:
            r = (obj.id & 0x000000FF) >> 0
            g = (obj.id & 0x0000FF00) >> 8
            b = (obj.id & 0x00FF0000) >> 16
            glUniform4f(self.pickingColor, r / 255.0, g / 255.0, b / 255.0, 1.0)
            obj.draw()

        glColor3f(1, 1, 1)
        draw_cube()

    def mouse(self, button, state, x, y):
        """
        Mouse callback function.
        """
        # button macros: GLUT_LEFT_BUTTON, GLUT_MIDDLE_BUTTON, GLUT_RIGHT_BUTTON
        self.path_list.clear()

        print(
            f"Display #{self.id} mouse press event: button={button}, state={state}, x={x}, y={y}"
        )
        if self.id != 5:
            if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
                obj_id = self.pickObject(x, y)
                if obj_id != 0xFFFFFF:
                    print(f"{obj_id} selected")
                else:
                    print("Nothing selected")
            if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
                print(f"Add teapot at ({x}, {y})")
                if self.paused:
                    self.addBunny(x, y)

        self.button = button
        self.modifier = glutGetModifiers()

        glutPostRedisplay()

    def motion(self, x, y):
        """
        Motion (Dragging) callback function.
        """
        print(
            f"Display #{self.id} mouse move event: x={x}, y={y}, modifer={self.modifier}"
        )
        self.path_list.append((x, y))

        # PA1-Task4: object manipulation for each operation
        x0 = 0
        y0 = 0
        x_naive = x
        y_naive = y
        x, y = conversion(x, y)
        dx = 0
        dy = 0

        if len(self.path_list) >= 2:
            x0 = self.path_list[len(self.path_list) - 2][0]
            y0 = self.path_list[len(self.path_list) - 2][1]
            x0_naive = x0
            y0_naive = y0
            x0, y0 = conversion(x0, y0)

            dx = x - x0
            dy = y - y0

            x_o = 0
            y_o = 0
            if len(self.selected_obj_list) > 0:
                last_obj_id = self.selected_obj_list[len(self.selected_obj_list) - 1]
                for obj in self.obj_list:
                    if obj.id == last_obj_id:
                        if self.id == 2:
                            x_o = obj.mat[0][3]
                            y_o = obj.mat[1][3]
                        elif self.id == 3:
                            x_o = obj.mat[2][3]
                            y_o = obj.mat[1][3]
                        elif self.id == 4:
                            x_o = obj.mat[0][3]
                            y_o = obj.mat[2][3]

            cross_result = np.cross(
                np.array([x0 - x_o, y0 - y_o, 0]), np.array([dx, dy, 0])
            )[2]

            if self.button == GLUT_LEFT_BUTTON:
                #PA2-Task3-1: Interface for trackball rotation
                if self.id == 5:
                    pass
                    # result = self.track_ball([x0_naive, y0_naive], [x_naive, y_naive])
                    # rot_mat = result[0]

                    # # camera position update
                    # new_cam_pos = np.matmul(rot_mat, np.transpose(self.camera_position))
                    # new_cam_pos = np.transpose(new_cam_pos)
                    # self.camera_position = new_cam_pos

                    # # camera up-vetor update
                    # new_cam_axis = np.matmul(rot_mat, np.transpose(self.camera_up_vec))
                    # new_cam_axis = np.transpose(new_cam_axis)
                    # self.camera_up_vec = new_cam_axis

                else:
                    for obj in self.obj_list:
                        if obj.id in self.selected_obj_list:
                            current_obj = obj

                            O1 = 0
                            O2 = 0
                            if self.id == 2:
                                O1 = current_obj.mat[0][3]
                                O2 = current_obj.mat[1][3]
                            elif self.id == 3:
                                O1 = current_obj.mat[2][3]
                                O2 = current_obj.mat[1][3]
                            elif self.id == 4:
                                O1 = current_obj.mat[0][3]
                                O2 = current_obj.mat[2][3]

                            # PA1-Task3: I'm not sure which one is correct between the operation in real code and comments
                            if self.modifier & GLUT_ACTIVE_ALT:
                                print("Rotation")
                                if cross_result >= 0:
                                    current_obj.mat = (
                                        self.translation(O1, O2)
                                        @ self.rotation(np.sqrt(dx * dx + dy * dy) * 10)
                                        @ self.translation(-1 * O1, -1 * O2)
                                        @ current_obj.mat
                                    )  # current_obj.mat@self.rotation(np.sqrt(dx*dx + dy*dy)*10)
                                else:
                                    current_obj.mat = (
                                        self.translation(O1, O2)
                                        @ self.rotation(
                                            -1 * np.sqrt(dx * dx + dy * dy) * 10
                                        )
                                        @ self.translation(-1 * O1, -1 * O2)
                                        @ current_obj.mat
                                    )  # current_obj.mat@self.rotation(-1 * np.sqrt(dx*dx + dy*dy)*10)
                            elif self.modifier & GLUT_ACTIVE_SHIFT:
                                print("Scaling")
                                current_obj.mat = (
                                    self.translation(O1, O2)
                                    @ self.scale(1 + dx * 0.1, 1 + dy * 0.1)
                                    @ self.translation(-1 * O1, -1 * O2)
                                    @ current_obj.mat
                                )  # current_obj.mat@self.scale(1 + dx*0.1, 1 + dy*0.1)
                            else:
                                print(self.paused)
                                #PA3: check static collision when translating
                                if self.paused:
                                    for obj in self.obj_list:
                                        if str(type(obj)) == "<class '__main__.Bunny'>":
                                            if obj.id in self.selected_obj_list:
                                                self.target_obj.append(obj)
                                            else:
                                                self.detection_obj.append(obj)

                                    trans = self.translation(dx, dy)
                                    dx_world = trans[0][3]
                                    dy_world = trans[1][3]
                                    dz_world = trans[2][3]
                                    current_obj.x_max += dx_world
                                    current_obj.x_min += dx_world
                                    current_obj.y_max += dy_world
                                    current_obj.y_min += dy_world
                                    current_obj.z_max += dz_world
                                    current_obj.z_min += dz_world
                                    reason, target = self.static_collision_detection()
                                    if target != None:
                                        target.collision_detected = True
                                        self.col_detected_obj_id.append([reason, target.id])
                                        current_obj.x_max -= dx_world
                                        current_obj.x_min -= dx_world
                                        current_obj.y_max -= dy_world
                                        current_obj.y_min -= dy_world
                                        current_obj.z_max -= dz_world
                                        current_obj.z_min -= dz_world
                                    else:
                                        print(current_obj.mat)
                                        current_obj.mat = trans @ current_obj.mat

                                    self.target_obj.clear()
                                    self.detection_obj.clear()

            elif self.button == GLUT_RIGHT_BUTTON:
                #PA2-Task3-3: Interface for panning the scene
                cam_trans = np.array([float(dx), float(dy)])
                cam_dy = cam_trans[1] * self.camera_up_vec
                cam_dx = cam_trans[0] * np.cross(
                    self.camera_up_vec, self.camera_position
                )
                translation_vec = cam_dx + cam_dy
                self.camera_trans = translation_vec
                self.camera_position += translation_vec
                self.camera_at += translation_vec

        glutPostRedisplay()

    def pickObject(self, x, y):
        """
        Object picking function.\n
        obj_id can be used to identify which object is clicked, as each object is assigned with unique id.
        """
        self.drawPickingScene()

        data = glReadPixels(x, self.height - y, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE)

        obj_id = data[0] + data[1] * (2**8) + data[2] * (2**16)

        if obj_id != 0xFFFFFF:
            self.selected_obj_list.append(obj_id)
        else:
            self.selected_obj_list.clear()

        self.drawScene()

        return obj_id

    def drawAxes(self, x, y, z):
        glPushMatrix()
        glBegin(GL_LINES)
        glColor3f(1, 0, 0)
        glVertex3f(x, y, z)
        glVertex3f(x + 0.1, y, z)
        glColor3f(0, 1, 0)
        glVertex3f(x, y, z)
        glVertex3f(x, y + 0.1, z)
        glColor3f(0, 0, 1)
        glVertex3f(x, y, z)
        glVertex3f(x, y, z + 0.1)
        glColor3f(1, 1, 1)
        glEnd()
        glPopMatrix()

    def addTeapot(self, x, y):
        # this function should be implemented
        teapot = Teapot()
        # update teapot.mat, etc. to complete your tasks

        # PA1-Task1: rotate teapot for each plane in which that teapot is created
        rotation_mat = np.eye(4)
        if self.id == 3:
            rotation_mat = np.array(
                [[0, 0, -1, 0], [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]]
            )
        elif self.id == 4:
            rotation_mat = np.array(
                [[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]
            )

        teapot.mat = np.matmul(rotation_mat, teapot.mat)
        print(teapot.mat)
        SubWindow.obj_list.append(teapot)

    def addBunny(self, x, y):
        x, y = conversion(x, y)
        bunny = Bunny()
        bunny.is_aabb = SubWindow.is_aabb
        rotation_mat = np.eye(4)
        trans_mat = np.eye(4)
        if self.id == 2:
            trans_mat = np.array(
                [[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, 0], [0, 0, 0, 1]]
            )
            bunny.x_max += x
            bunny.x_min += x
            bunny.y_max += y
            bunny.y_min += y
        elif self.id == 3:
            bunny.y_max += y
            bunny.y_min += y
            bunny.z_max += x
            bunny.z_min += x
            trans_mat = np.array(
                [[1, 0, 0, 0], [0, 1, 0, y], [0, 0, 1, x], [0, 0, 0, 1]]
            )
            rotation_mat = np.array(
                [[0, 0, -1, 0], [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]]
            )
        elif self.id == 4:
            bunny.x_max += x
            bunny.x_min += x
            bunny.z_max += y
            bunny.z_min += y
            trans_mat = np.array(
                [[1, 0, 0, x], [0, 1, 0, 0], [0, 0, 1, y], [0, 0, 0, 1]]
            )
            rotation_mat = np.array(
                [[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]
            )

        bunny.mat = trans_mat@rotation_mat@bunny.mat
        print(bunny.mat)

        self.target_obj.append(bunny)
        for obj in self.obj_list:
            if str(type(obj)) == "<class '__main__.Bunny'>":
                self.detection_obj.append(obj)
        
        SubWindow.obj_list.append(bunny)

        reason, target = self.static_collision_detection()
        if target != None:
            target.collision_detected = True
            print("detect collision when creating")
            self.col_detected_obj_id.append(["create", target.id])

        self.target_obj.clear()
        self.detection_obj.clear()

    def addBullet(self, speed):
        bullet = Bullet(speed)
        if SubWindow.paused:
            bullet.paused = True
        print(bullet.mat)
        SubWindow.obj_list.append(bullet)


    def keyboard(self, key, x, y):
        """
        Keyboard callback function.
        """
        print(f"Display #{glutGetWindow()} keyboard event: key={key}, x={x}, y={y}")

        # PA1-Task2: for this, I moved keyboard callback function to "Subwindow". And then it deletes objects whose id is in "selected_obj_list"
        if key == b"\x7f":
            for target_id in self.selected_obj_list:
                for obj in self.obj_list:
                    if obj.id == target_id:
                        self.obj_list.remove(obj)

        #PA2-Task3-2: Interface for scaling
        if key == b"=":
            if self.scale_num < 10:
                if self.scale_num < 5:
                    self.scale_num += 0.1
                else:
                    self.scale_num += 1

        if key == b"-":
            if self.scale_num > 4.2:
                if self.scale_num > 5:
                    self.scale_num -= 1
                else:
                    self.scale_num -= 0.1

        #PA2-Task3-5: camera reset
        if key == b"d":
            self.camera_position = np.array([0.0, 0.0, 1.0])
            self.camera_at = np.array([0.0, 0.0, 0.0])
            self.camera_up_vec = np.array([0.0, 1.0, 0.0])
            self.camera_trans = np.array([0.0, 0.0, 0.0])
            self.scale_num = 5

         #PA2-Task3-6: projection reset
        if key == b"0":
            self.fov = 0
            self.camera_position = self.camera_position/np.linalg.norm(self.camera_position)

        #PA3: shooting a bullet
        if key == b" ":
            global event_start_time
            if event_start_time == 0:
                event_start_time = time.time()
                print(event_start_time)

        #PA3: showing aabb structure for each bunny
        if key == b"b":
            if SubWindow.is_aabb:
                for obj in self.obj_list:
                    if str(type(obj)) == "<class '__main__.Bunny'>":
                        obj.is_aabb = False
                SubWindow.is_aabb = False
            else:
                for obj in self.obj_list:
                    if str(type(obj)) == "<class '__main__.Bunny'>":
                        obj.is_aabb = True
                SubWindow.is_aabb = True

        #PA3: toggle the window activate
        if key == b"p":
            if SubWindow.paused:
                for obj in self.obj_list:
                    if str(type(obj)) == "<class '__main__.Bullet'>":
                        obj.paused = False
                SubWindow.paused = False
            else:
                for obj in self.obj_list:
                    if str(type(obj)) == "<class '__main__.Bullet'>":
                        obj.paused = True
                SubWindow.paused = True

        if glutGetModifiers() & GLUT_ACTIVE_SHIFT:
            print("shift pressed")
        if glutGetModifiers() & GLUT_ACTIVE_ALT:
            print("alt pressed")
        if glutGetModifiers() & GLUT_ACTIVE_CTRL:
            print("ctrl pressed")

        glutPostRedisplay()

    def special(self, key, x, y):
        """
        Special key callback function.
        """
        print(f"Display #{glutGetWindow()} special key event: key={key}, x={x}, y={y}")

        #PA2-Task3-4: Interface for fov
        if key == 101:
            if self.fov < 90:
                self.fov += 5
                self.camera_position = self.camera_position/np.linalg.norm(self.camera_position) * (5/np.tan(np.pi/180 * self.fov * 0.5))

        if key == 103:
            if self.fov > 0:
                self.fov -= 5
                if self.fov == 0:
                    self.camera_position = self.camera_position/np.linalg.norm(self.camera_position)
                else:
                    self.camera_position = self.camera_position/np.linalg.norm(self.camera_position) * (5/np.tan(np.pi/180 * self.fov * 0.5))

        print(self.fov)

        glutPostRedisplay()

        return
    
    #PA3: function for determine the speed of bullet
    def special_up(self, key, x, y):
        """
        Special key callback function.
        """
        print(f"Display #{glutGetWindow()} special key event: key={key}, x={x}, y={y}")

        global event_start_time
        if key == 32: 
            self.addBullet((time.time() - event_start_time) * 0.01)
            event_start_time = 0
        
        glutPostRedisplay()

        return
    # PA1-Task3-1: it returns proper rotation matrix taking degree
    def rotation(self, degree):
        id = self.id
        radian = degree * (np.pi / 180)
        rotation_mat = np.eye(4)
        if id == 2:
            rotation_mat = np.array(
                [
                    [np.cos(radian), -np.sin(radian), 0, 0],
                    [np.sin(radian), np.cos(radian), 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, 1],
                ]
            )
        elif id == 3:
            rotation_mat = np.array(
                [
                    [1, 0, 0, 0],
                    [0, np.cos(radian), np.sin(radian), 0],
                    [0, -np.sin(radian), np.cos(radian), 0],
                    [0, 0, 0, 1],
                ]
            )
        elif id == 4:
            rotation_mat = np.array(
                [
                    [np.cos(radian), 0, -np.sin(radian), 0],
                    [0, 1, 0, 0],
                    [np.sin(radian), 0, np.cos(radian), 0],
                    [0, 0, 0, 1],
                ]
            )

        return rotation_mat

    # PA1-Task3-2: it returns proper scaling matrix taking sx, sy
    def scale(self, sx, sy):
        id = self.id
        scale_mat = np.eye(4)
        if id == 2:
            scale_mat = np.array(
                [[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
            )
        elif id == 3:
            scale_mat = np.array(
                [[1, 0, 0, 0], [0, sy, 0, 0], [0, 0, sx, 0], [0, 0, 0, 1]]
            )
        elif id == 4:
            scale_mat = np.array(
                [[sx, 0, 0, 0], [0, 1, 0, 0], [0, 0, sy, 0], [0, 0, 0, 1]]
            )

        return scale_mat

    # PA1-Task3-3: it returns proper scaling matrix taking dx, dy
    def translation(self, dx, dy):
        id = self.id
        translation_mat = np.eye(4)
        if id == 2:
            translation_mat = np.array(
                [[1, 0, 0, dx], [0, 1, 0, dy], [0, 0, 1, 0], [0, 0, 0, 1]]
            )
        elif id == 3:
            translation_mat = np.array(
                [[1, 0, 0, 0], [0, 1, 0, dy], [0, 0, 1, dx], [0, 0, 0, 1]]
            )
        elif id == 4:
            translation_mat = np.array(
                [[1, 0, 0, dx], [0, 1, 0, 0], [0, 0, 1, dy], [0, 0, 0, 1]]
            )

        return translation_mat

    # PA2-Task1: the function which returns rotation matrix for trackball (I think it is correct theoretically, but it works weird)
    def track_ball(self, start, end):
        start[0] = glutGet(GLUT_WINDOW_WIDTH) / 2 - start[0]
        end[0] = glutGet(GLUT_WINDOW_WIDTH) / 2 - end[0]
        start[1] = glutGet(GLUT_WINDOW_HEIGHT) / 2 - start[1]
        end[1] = glutGet(GLUT_WINDOW_HEIGHT) / 2 - end[1]

        radius = (
            return_small(glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)) / 2
        )
        if radius**2 - start[0] ** 2 - start[1] ** 2 >= 0:
            position1 = np.array(
                [
                    start[0],
                    start[1],
                    np.sqrt(radius**2 - start[0] ** 2 - start[1] ** 2),
                ]
            )
        else:
            len = np.sqrt(start[0] ** 2 + start[1] ** 2)
            position1 = radius * np.array([start[0] / len, start[1] / len, 0])

        if radius**2 - end[0] ** 2 - end[1] ** 2 >= 0:
            position2 = np.array(
                [end[0], end[1], np.sqrt(radius**2 - end[0] ** 2 - end[1] ** 2)]
            )
        else:
            len = np.sqrt(end[0] ** 2 + end[1] ** 2)
            position2 = radius * np.array([end[0] / len, end[1] / len, 0])

        rot_axis = np.cross(position1, position2) / np.linalg.norm(
            np.cross(position1, position2)
        )
        rot_axis = rot_axis@np.transpose(self.camera_rot_mat)
        degree = np.linalg.norm(np.cross(position1, position2)) / (
            np.linalg.norm(position1) * np.linalg.norm(position2)
        )
        k = np.array(
            [
                [0, -rot_axis[2], rot_axis[1]],
                [rot_axis[2], 0, -rot_axis[0]],
                [-rot_axis[1], rot_axis[0], 0],
            ]
        )
        radian = degree
        rot_mat = (
            np.eye(3) + (1 - np.cos(radian)) * np.matmul(k, k) + np.sin(radian) * k
        )
        if radian == 0:
            return (np.eye(3), rot_axis)
        else:
            self.camera_rot_mat = rot_mat@self.camera_rot_mat
            return (rot_mat, rot_axis)


class Viewer:
    width, height = 800, 800

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
        self.width = w
        self.height = h

        #PA2-Task3-7: for implementing window resizing
        for index, subWindow in enumerate(SubWindow.windows):
            glutSetWindow(subWindow.id)
            if index == 1:
                glutPositionWindow(self.width // 2 + 1, 0)
            elif index == 2:
                glutPositionWindow(0, self.height // 2 + 1)
            elif index == 3:
                glutPositionWindow(self.width // 2 + 1, self.height // 2 + 1)

            glutReshapeWindow(self.width // 2, self.height // 2)

        glutPostRedisplay()

    def run(self):
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)

        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(0, 0)
        self.mainWindow = glutCreateWindow(b"CS471 Computer Graphics #1")
        glutDisplayFunc(self.display)
        glutIdleFunc(self.idle)
        glutReshapeFunc(self.reshape)

        # sub-windows
        # xy plane
        SubWindow.windows.append(
            SubWindow(self.mainWindow, 0, 0, self.width // 2, self.height // 2)
        )
        # zy plane
        SubWindow.windows.append(
            SubWindow(
                self.mainWindow,
                self.width // 2 + 1,
                0,
                self.width // 2,
                self.height // 2,
            )
        )
        SubWindow.windows[1].viewMat = np.array(
            [[0, 0, 1, 0], [0, 1, 0, 0], [-1, 0, 0, 0], [0, 0, 0, 1]]
        )
        # xz plane
        SubWindow.windows.append(
            SubWindow(
                self.mainWindow,
                0,
                self.height // 2 + 1,
                self.width // 2,
                self.height // 2,
            )
        )
        SubWindow.windows[2].viewMat = np.array(
            [[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]]
        )
        # 3D
        SubWindow.windows.append(
            SubWindow(
                self.mainWindow,
                self.width // 2 + 1,
                self.height // 2 + 1,
                self.width // 2,
                self.height // 2,
            )
        )

        for subWindow in SubWindow.windows:
            glutSetWindow(subWindow.id)
            glutDisplayFunc(subWindow.display)
            glutKeyboardFunc(subWindow.keyboard)
            glutSpecialFunc(subWindow.special)
            glutSpecialUpFunc(subWindow.special_up)
            glutMouseFunc(subWindow.mouse)
            glutMotionFunc(subWindow.motion)

            self.light()

        glutMainLoop()


if __name__ == "__main__":
    viewer = Viewer()
    viewer.run()
