'''
from kivy.app import App
from kivy.uix.image import Image
from kivy.graphics import Triangle
from kivy.clock import Clock

class MyApp(App):

    def build(self):
        self.my_image = Image(source='rain.png')
        #with self.my_image.canvas:
        #    Triangle(point=(0, 0, 30, 30, 60, 0))

        Clock.schedule_once(self.export, 1)
        return self.my_image

    def export(self, dt):
        self.my_image.export_to_png('test2.png')
        self.my_image.export_as_image().save('test3.png')


myapp = MyApp().run()
'''



from turtle import onclick
from kivy.uix.screenmanager import Screen

from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatButton

from email_util import send_email

from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.core.image import Image
from kivymd.uix.button import MDFillRoundFlatButton
from kivy.uix.widget import Widget
from kivymd.uix.textfield import MDTextField
from kivy.uix.screenmanager import Screen
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import glEnable, glDisable, GL_DEPTH_TEST
from kivy.graphics import RenderContext, Callback, PushMatrix, PopMatrix, \
    Color, Translate, Rotate, Mesh, UpdateNormalMatrix, ChangeState
from objloader import ObjFile, ALL_INDEX_SETS
from functools import partial

import re
import pickle
import numpy as np
import trimesh

from smpl_numpy import SMPLModel

# TODO: Create the class similar to RenderScreen, where the class will inherit from Widget only,
# and then try to save it as image.
class RenderWidget(Widget):
    
    def __init__(self, **kwargs):
        self.canvas = RenderContext(compute_normal_mat=True)
        self.canvas.shader.source = resource_find('simple.glsl')
        
        super(RenderWidget, self).__init__(**kwargs)
        
        with self.canvas:
            self.cb = Callback(self.setup_gl_context)
            PushMatrix()
            self.setup_scene()
            PopMatrix()
            self.cb = Callback(self.reset_gl_context)
        
        #Clock.schedule_interval(self.update_glsl, 1 / 60.)
        Clock.schedule_once(self.update_glsl)

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
        #self.rot.angle += delta * 100

    def setup_scene(self):
        Color(1, 1, 1, 1)
        PushMatrix()
        Translate(0, 0, -3)
        self.rot = Rotate(1, 0, 1, 0)
        UpdateNormalMatrix()
        
        smpl_model = SMPLModel(resource_find('PY3_SMPL_MALE.pkl'))
        pose = np.zeros(shape=smpl_model.pose_shape)
        trans = np.zeros(smpl_model.trans_shape)
        
        smpl_model.set_params(beta=np.zeros(10), pose=pose, trans=trans)
        
        vertices = smpl_model.verts.squeeze()
        faces = smpl_model.faces.squeeze()

        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)   # process=False bites again!!!!!

        vertex_normals = trimesh.geometry.weighted_vertex_normals(
            vertex_count=len(mesh.vertices),
            faces=mesh.faces,
            face_normals=mesh.face_normals,
            face_angles=mesh.face_angles)
        setattr(mesh, 'vertex_normals', vertex_normals)
        
        mesh_obj = trimesh.exchange.export.export_obj(mesh)
        scene = ObjFile(mesh_obj)
        m = list(scene.objects.values())[0]
        
        vertex_format = [
            (b'v_pos', 3, 'float'),
            (b'v_normal', 3, 'float'),
            (b'v_tc0', 2, 'float')]
        
        self.main_mesh = Mesh(
            vertices=m.vertices,
            indices=list(range(41328)),
            fmt=vertex_format,
            mode='triangles'
        )

        PopMatrix()


class MainApp(MDApp):
    
    def export(self, dt):
        img = self.render_widget.export_as_image()
        img.save('render.png')
        
    def my_screenshot(self, dt):
        Window.screenshot()
    
    def build(self):
        self.screen = Screen()
        # TODO: Send email asynchronously
        button_widget = MDRectangleFlatButton(
                text="Hello, World",
                pos_hint={"center_x": 0.5, "center_y": 0.5},
                on_press=send_email,
            )
        self.screen.add_widget(button_widget)
    
        self.render_widget = RenderWidget()
        
        #Clock.schedule_once(self.export, 1)
        Clock.schedule_once(self.my_screenshot, 5)
        
        #return self.screen
        return self.render_widget


MainApp().run()

