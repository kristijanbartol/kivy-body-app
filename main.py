from kivymd.app import MDApp
#from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.uix.button import Button
from kivymd.uix.button import MDFillRoundFlatButton
from kivy.uix.screenmanager import Screen
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import glEnable, glDisable, GL_DEPTH_TEST
from kivy.graphics import RenderContext, Callback, PushMatrix, PopMatrix, \
    Color, Translate, Rotate, Mesh, UpdateNormalMatrix
from objloader import ObjFile
import sys

import pickle
import numpy as np
import trimesh

from smpl_numpy import SMPLModel


#Window.size = (360, 600)


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
       
    def on_touch_move(self, touch):
        if touch.x < touch.ox:
            app.root.ids.sm.transition.direction = 'left'
            app.root.ids.sm.current = 'in_screen'
        if touch.x > touch.ox:
            app.root.ids.sm.transition.direction = 'right'
            app.root.ids.sm.current = 'render_screen'


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
        
        beta = (np.random.rand(*app.smpl_model['male'].beta_shape) - 0.5) * 0.06
        app.smpl_model['male'].set_params(beta=beta, pose=app.pose, trans=app.trans)
        app.smpl_model['female'].set_params(beta=beta, pose=app.pose, trans=app.trans)

        vertices = app.smpl_model['male'].verts.squeeze()
        faces = app.smpl_model['male'].faces.squeeze()

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

    def on_touch_move(self, touch):
        if touch.x < touch.ox:
            app.root.ids.sm.transition.direction = 'left'
            app.root.ids.sm.current = 'measurements_screen'
        if touch.x > touch.ox:
            app.root.ids.sm.transition.direction = 'right'
            app.root.ids.sm.current = 'in_screen'
            
    def on_enter(self):
        #app.root.ids['spinner'].active = False
        self.update_mesh_callback.ask_update()

        
class RenderButton(MDFillRoundFlatButton):

    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            inputs = self._check_inputs()
            if inputs is not None:
                app.root.ids['spinner'].active = True
                self._calculate_measurements(*inputs)
                self._calculate_vertices(inputs[2])
                app.root.ids.sm.transition.direction = 'left'
                app.root.ids.sm.current = 'render_screen'
                
    def _check_inputs(self):
        def _check_height(height_text):
            if not (len(height_text) == 4 and height_text[0].isdigit() and height_text[1] == '.' and \
                height_text[2].isdigit() and height_text[3].isdigit()):
                #app.root.ids.height_text.error = True
                #app.root.ids.height_text.bind(text=self.verify)
                return False
            
            app.root.ids.height_text.error = False
            return float(height_text)
            
        def _check_weight(weight_text):
            if not (len(weight_text) > 0 and all([weight_text[x] for x in range(len(weight_text))])):
                app.root.ids.weight_text.error = True
                return False
            
            app.root.ids.weight_text.error = False
            return float(weight_text)
        
        gender = 'male' if app.root.ids['male_check'].active else 'female'
            
        height = _check_height(app.root.ids.height_text.text)
        weight = _check_weight(app.root.ids.weight_text.text)
        
        return (height, weight, gender) if (height and weight) else None
    
    @staticmethod
    def _calculate_measurements(height, weight, gender):
        coefs_baseline = app.coefs_baseline_dict[gender]
        coefs_shape = app.coefs_shape[gender]
        measurements = np.array([height, weight, 1.]) @ coefs_baseline * 100.
        betas = np.array([height, weight, 1.]) @ coefs_shape
        
        app.measurements = list(measurements)
        for i in range(10):
            app.betas[i] = betas[i]
        
        for midx, mvalue in enumerate(app.measurements):
            app.root.ids[f'meas{midx+1}'].text = f'{MEASUREMENT_NAMES[midx]}: {mvalue:.2f}cm'
            
    @staticmethod
    def _calculate_vertices(gender):
        app.smpl_model[gender].set_params(beta=app.betas, pose=app.pose, trans=app.trans)

        vertices = app.smpl_model[gender].verts.squeeze()
        faces = app.smpl_model[gender].faces.squeeze()

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
    
    def verify_height(self, instance, text):
        if len(text) != 4 or (len(text) == 4 and not all([
                text[0].isdigit(),
                text[1] == '.',
                text[2].isdigit(),
                text[3].isdigit()])):
            instance.error = True
        else:
            instance.error = False
            
    def verify_weight(self, instance, text):
        if len(text) > 0 and all([x.isdigit() for x in text]) and (int(text) < 40 or int(text) > 200):
            instance.error = True
        elif all([x.isdigit() for x in text]):
            instance.error = False
        else: 
            instance.error = True
            
    #def test(self, instance):
    #    print('tested')


class RendererApp(MDApp):
    
    
    with open(resource_find('coefs.pkl'), 'rb') as handle:
        _coefs = pickle.load(handle)
        
    coefs_baseline_dict = {
        'male': _coefs['male_meas_coefs'].swapaxes(0, 1),
        'female': _coefs['female_meas_coefs'].swapaxes(0, 1)
    }
    
    male_coefs_baseline = ListProperty(list(
        _coefs['male_meas_coefs'].swapaxes(0, 1)))
    female_coefs_baseline = ListProperty(list(
        _coefs['female_meas_coefs'].swapaxes(0, 1)))
    
    coefs_shape = {
        'male': _coefs['male_shape_coefs'].swapaxes(0, 1),
        'female': _coefs['female_shape_coefs'].swapaxes(0, 1)
    }
    
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
    
    smpl_model_male_path = resource_find('PY3_SMPL_MALE.pkl')
    smpl_model_female_path = resource_find('PY3_SMPL_FEMALE.pkl')
    
    smpl_model = {    
        'male': SMPLModel(smpl_model_male_path),
        'female': SMPLModel(smpl_model_female_path)
    }
    np.random.seed(9608)
    pose = np.zeros(shape=smpl_model['male'].pose_shape)
    trans = np.zeros(smpl_model['male'].trans_shape)
    
    def build(self):
        self.theme_cls.theme_style = "Dark"  # "Light"
        self.root = RootWidget()
        
        #self.root.ids.height_text.bind(on_focus=self.root.test)
        #self.root.ids.weight_text.bind(text=self.root.verify_weight)
        
        return self.root


if __name__ == "__main__":
    app = RendererApp()
    app.run()
