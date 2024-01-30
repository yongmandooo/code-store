from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np

# import pygame
# from pygame.locals import *
# from PIL import Image
#
# def load_obj_texture(filename, texture_filename):
#     vertices = []
#     normals = []
#     tex_coords = []
#     faces = []
#     texture_id = glGenTextures(1)
#
#     with open(filename, 'r') as file:
#         for line in file:
#             if line.startswith('v '):
#                 vertices.append(list(map(float, line[2:].split())))
#             elif line.startswith('vt '):
#                 tex_coords.append(list(map(float, line[3:].split())))
#             elif line.startswith('vn '):
#                 normals.append(list(map(float, line[3:].split())))
#             elif line.startswith('f '):
#                 face = line[2:].split()
#                 faces.append([list(map(int, vertex.split('/'))) for vertex in face])
#
#     texture_surface = pygame.image.load(texture_filename)
#     texture_data = pygame.image.tostring(texture_surface, 'RGBA', 1)
#     width, height = texture_surface.get_size()
#
#     glBindTexture(GL_TEXTURE_2D, texture_id)
#     glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
#     glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
#     glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
#
#     return vertices, normals, tex_coords, faces, texture_id
#
# def draw_obj_texture(vertices, normals, tex_coords, faces, texture_id):
#     glEnable(GL_TEXTURE_2D)
#     glBindTexture(GL_TEXTURE_2D, texture_id)
#
#     glBegin(GL_TRIANGLES)
#     for face in faces:
#         for vertex in face:
#             vertex_index, tex_coord_index, normal_index = vertex
#             glTexCoord2fv(tex_coords[tex_coord_index - 1][:2])
#             glVertex3fv(vertices[vertex_index - 1])
#     glEnd()
#
#     glDisable(GL_TEXTURE_2D)

def load_obj(filename):
    vertices = []
    normals = []
    faces = []

    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('v '):
                vertices.append(list(map(float, line[2:].split())))
            elif line.startswith('vn '):
                normals.append(list(map(float, line[3:].split())))
            elif line.startswith('f '):
                face = line[2:].split()
                faces.append([list(map(int, vertex.split('/'))) for vertex in face])

    return np.array(vertices), np.array(normals), faces

def draw_obj(vertices, normals, faces):

    glBegin(GL_TRIANGLES)
    for face in faces:
        for vertex in face:
            vertex_index, _, normal_index  = vertex
            glNormal3fv(normals[normal_index - 1])
            glVertex3fv(vertices[vertex_index - 1])
    glEnd()