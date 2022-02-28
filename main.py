from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivymd.uix.button import MDFillRoundFlatButton
from kivy.uix.screenmanager import Screen
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import glEnable, glDisable, GL_DEPTH_TEST
from kivy.graphics import RenderContext, Callback, PushMatrix, PopMatrix, \
    Color, Translate, Rotate, Mesh, UpdateNormalMatrix
from objloader import ObjFile

import pickle
import numpy as np
import trimesh

from smpl_numpy import SMPLModel


Window.size = (360, 600)


MEASUREMENT_NAMES = [
    ('A', 'Head circumference'),
    ('B', 'Neck circumference'),
    ('C', 'Shoulder to crotch'),
    ('D', 'Chest circumference'),
    ('E', 'Waist circumference'),
    ('F', 'Hip circumference'),
    ('G', 'Wrist circumference'),
    ('H', 'Bicep circumference'),
    ('I', 'Forearm circumference'),
    ('J', 'Arm length'),
    ('K', 'Inside leg length'),
    ('L', 'Thigh circumference'),
    ('M', 'Calf circumference'),
    ('N', 'Ankle circumference'),
    ('O', 'Shoulder breadth')
]


class MeasurementsScreen(Screen):
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            app.root.ids.sm.current = 'in_screen'


class RenderScreen(Screen):
    
    def __init__(self, **kwargs):
        super(RenderScreen, self).__init__(**kwargs)
        
        self.canvas = RenderContext(compute_normal_mat=True)
        self.canvas.shader.source = resource_find('simple.glsl')
        
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
        
    def update_mesh(self, *args):
        self.mesh.vertices = app.vertices

    def setup_scene(self):
        Color(1, 1, 1, 1)
        PushMatrix()
        Translate(0, 0, -3)
        self.rot = Rotate(1, 0, 1, 0)
        UpdateNormalMatrix()
        
        beta = (np.random.rand(*app.smpl.beta_shape) - 0.5) * 0.06
        app.smpl.set_params(beta=beta, pose=app.pose, trans=app.trans)

        vertices = app.smpl.verts.squeeze()
        faces = app.smpl.faces.squeeze()

        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, vertex_colors=np.tile([.7, .7, .7], (6890, 1)))

        vertex_normals = trimesh.geometry.weighted_vertex_normals(
            vertex_count=len(mesh.vertices),
            faces=mesh.faces,
            face_normals=mesh.face_normals,
            face_angles=mesh.face_angles)
        setattr(mesh, 'vertex_normals', vertex_normals)
        
        scene = ObjFile(trimesh.exchange.export.export_obj(mesh))
        m = list(scene.objects.values())[0]
        
        self.mesh = Mesh(
            vertices=app.vertices,
            indices=m.indices,
            fmt=m.vertex_format,
            mode='triangles',
        )
        
        self.update_mesh_callback = Callback(self.update_mesh, needs_redraw=True)
        PopMatrix()
        
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            app.root.ids.sm.current = 'measurements_screen'
            
    def on_enter(self):
        Logger.info('renderscreen resumed')  
        self.update_mesh_callback.ask_update()

        
class RenderButton(MDFillRoundFlatButton):
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            inputs = self._check_inputs()
            if inputs is not None:
                self._calculate_measurements(*inputs)
                self._calculate_vertices()
                app.root.ids.sm.current = 'render_screen'
            
    @staticmethod
    def _check_inputs():
        def _check_height(height_text):
            if not (len(height_text) == 4 and height_text[0].isdigit() and height_text[1] == '.' and \
                height_text[2].isdigit() and height_text[3].isdigit()):
                app.root.ids.height_text.error = True
                return False
            return float(height_text)
            
        def _check_weight(weight_text):
            if not (len(weight_text) > 0 and all([weight_text[x] for x in range(len(weight_text))])):
                app.root.ids.weight_text.error = True
                return False
            return float(weight_text)
            
        height = _check_height(app.root.ids.height_text.text)
        weight = _check_weight(app.root.ids.weight_text.text)
        
        return (height, weight) if (height and weight) else None
    
    @staticmethod
    def _calculate_measurements(height, weight):
        measurements = np.array([height, weight, 1.]) @ app.male_coefs_baseline * 100.
        betas = np.array([height, weight, 1.]) @ app.male_coefs_shape
        
        app.measurements = list(measurements)
        for i in range(10):
            app.betas[i] = betas[i]
        
        for midx, mvalue in enumerate(app.measurements):
            app.root.ids[f'meas{midx+1}'].text = f'{MEASUREMENT_NAMES[midx]}: {mvalue:.2f}cm'
            
    @staticmethod
    def _calculate_vertices():
        app.smpl.set_params(beta=app.betas, pose=app.pose, trans=app.trans)

        vertices = app.smpl.verts.squeeze()
        faces = app.smpl.faces.squeeze()

        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, vertex_colors=np.tile([.7, .7, .7], (6890, 1)))

        vertex_normals = trimesh.geometry.weighted_vertex_normals(
            vertex_count=len(mesh.vertices),
            faces=mesh.faces,
            face_normals=mesh.face_normals,
            face_angles=mesh.face_angles)
        setattr(mesh, 'vertex_normals', vertex_normals)
        
        scene = ObjFile(trimesh.exchange.export.export_obj(mesh))
        m = list(scene.objects.values())[0]
        
        app.vertices = m.vertices
        

class RootWidget(Screen):
    
    pass
        


class RendererApp(MDApp):
    
    with open(resource_find('coefs.pkl'), 'rb') as handle:
        _coefs = pickle.load(handle)
    
    male_coefs_baseline = ListProperty(list(
        _coefs['male_meas_coefs'].swapaxes(0, 1)))
    female_coefs_baseline = ListProperty(list(
        _coefs['female_meas_coefs'].swapaxes(0, 1)))
    
    male_coefs_shape = ListProperty(list(
        _coefs['male_shape_coefs'].swapaxes(0, 1)))
    female_coefs_shape = ListProperty(list(
        _coefs['female_shape_coefs'].swapaxes(0, 1)))
    
    male_coefs_meas_to_shae = ListProperty(list(
        _coefs['male_meas_to_shape_coefs'].swapaxes(0, 1)))
    female_coefs_meas_to_shae = ListProperty(list(
        _coefs['female_meas_to_shape_coefs'].swapaxes(0, 1)))
    
    measurements = ListProperty([0.] * 15)
    vertices = ListProperty([0.] * 330624)
    betas = ListProperty([0.] * 10)
    
    smpl_model_resource = resource_find('updated_smpl_model.pkl')
        
    smpl = SMPLModel(smpl_model_resource)
    np.random.seed(9608)
    pose = np.zeros(shape=smpl.pose_shape)
    trans = np.zeros(smpl.trans_shape)
    
    def build(self):
        self.theme_cls.theme_style = "Dark"  # "Light"
        self.root = RootWidget()
        return self.root


if __name__ == "__main__":
    app = RendererApp()
    app.run()
