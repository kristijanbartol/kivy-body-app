'''
3D Rotating Monkey Head
========================

This example demonstrates using OpenGL to display a rotating monkey head. This
includes loading a Blender OBJ file, shaders written in OpenGL's Shading
Language (GLSL), and using scheduled callbacks.

The monkey.obj file is an OBJ file output from the Blender free 3D creation
software. The file is text, listing vertices and faces and is loaded
using a class in the file objloader.py. The file simple.glsl is
a simple vertex and fragment shader written in GLSL.
'''

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import glEnable, glDisable, GL_DEPTH_TEST
from kivy.graphics import RenderContext, Callback, PushMatrix, PopMatrix, \
    Color, Translate, Rotate, Mesh, UpdateNormalMatrix
from objloader import ObjFile

from kivy.logger import Logger
from kivy import kivy_data_dir
import kivy
from os.path import join, dirname, exists, abspath
import sys
import numpy as np
import trimesh

from smpl_numpy import SMPLModel


resource_paths = ['.', dirname(sys.argv[0])]
resource_paths += [dirname(kivy.__file__), join(kivy_data_dir, '..')]


'''
def resource_find(filename):
    #if not filename:
    #    return
    #if filename[:8] == 'atlas://':
    #    return filename
    #if exists(abspath(filename)):
    #    return abspath(filename)
    for path in reversed(resource_paths):
        output = abspath(join(path, filename))
        if exists(output):
            return output
    #if filename[:5] == 'data:':
    #    return filename
'''


class Renderer(Widget):
    def __init__(self, **kwargs):
        self.canvas = RenderContext(compute_normal_mat=True)
        self.canvas.shader.source = resource_find('simple.glsl')
        #mesh_resource = resource_find("template.obj")

        #smpl_model_resource = resource_find('SMPL_MALE.pkl')
        smpl_model_resource = resource_find('updated_smpl_model.pkl')

        
        smpl = SMPLModel(smpl_model_resource)
        np.random.seed(9608)
        pose = (np.random.rand(*smpl.pose_shape) - 0.5) * 0.4
        beta = (np.random.rand(*smpl.beta_shape) - 0.5) * 0.06
        trans = np.zeros(smpl.trans_shape)
        smpl.set_params(beta=beta, pose=pose, trans=trans)

        vertices = smpl.verts.squeeze()
        faces = smpl.faces.squeeze()

        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, vertex_colors=np.tile([.7, .7, .7], (6890, 1)))
        #mesh.vertex_normals     # trigger @property method to calculate vertex normals
        vertex_normals = trimesh.geometry.weighted_vertex_normals(
            vertex_count=len(mesh.vertices),
            faces=mesh.faces,
            face_normals=mesh.face_normals,
            face_angles=mesh.face_angles)
        setattr(mesh, 'vertex_normals', vertex_normals)

        #self.scene = ObjFile(mesh_resource, mode='filename')
        self.scene = ObjFile(trimesh.exchange.export.export_obj(mesh))
        super(Renderer, self).__init__(**kwargs)
        with self.canvas:
            self.cb = Callback(self.setup_gl_context)
            PushMatrix()
            self.setup_scene()
            PopMatrix()
            self.cb = Callback(self.reset_gl_context)
        Clock.schedule_interval(self.update_glsl, 1 / 60.)

    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)

    def update_glsl(self, delta):
        asp = self.width / float(self.height)
        proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 100, 1)
        self.canvas['projection_mat'] = proj
        self.canvas['diffuse_light'] = (1.0, 1.0, 0.8)
        self.canvas['ambient_light'] = (0.1, 0.1, 0.1)
        self.rot.angle += delta * 100

    def setup_scene(self):
        Color(1, 1, 1, 1)
        PushMatrix()
        Translate(0, 0, -3)
        self.rot = Rotate(1, 0, 1, 0)
        m = list(self.scene.objects.values())[0]
        UpdateNormalMatrix()

        self.mesh = Mesh(
            vertices=m.vertices,
            indices=m.indices,
            fmt=m.vertex_format,
            mode='triangles',
        )
        PopMatrix()


class RendererApp(App):
    def build(self):
        return Renderer()


if __name__ == "__main__":
    RendererApp().run()