'''
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.core.image import Image
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.textfield import MDTextField
from kivy.uix.screenmanager import Screen
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import glEnable, glDisable, GL_DEPTH_TEST
from kivy.graphics import RenderContext, Callback, PushMatrix, PopMatrix, \
    Color, Translate, Rotate, Mesh, UpdateNormalMatrix, ChangeState
from objloader import ObjFile, ALL_INDEX_SETS, INDICES_LENS
from functools import partial

import re
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
        if touch.x - touch.ox < -10:
            app.root.ids.sm.transition.direction = 'left'
            app.root.ids.sm.current = 'in_screen'
        if touch.x - touch.ox > 10:
            app.root.ids.sm.transition.direction = 'right'
            app.root.ids.sm.current = 'render_screen'


class RenderScreen(Screen):
    
    def __init__(self, **kwargs):
        super(RenderScreen, self).__init__(**kwargs)
        
        self.canvas = RenderContext(compute_normal_mat=True)
        self.canvas.shader.source = resource_find('simple.glsl')
        
        Clock.schedule_once(self._prepare, 0.1)
        self.rot = Rotate(1, 0, 1, 0)
        Clock.schedule_interval(self.update_glsl, 1 / 60.)
        
    def _prepare(self, dt):
        with self.canvas:
            self.cb = Callback(self.setup_gl_context)
            PushMatrix()
            
            self.setup_scene()
            PopMatrix()
            self.cb = Callback(self.reset_gl_context)

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
        self.main_mesh.vertices = app.vertices
        for mesh_idx in range(len(self.measurement_meshes)):
            self.measurement_meshes[mesh_idx].vertices = app.faces_data[mesh_idx]

    def setup_scene(self):
        Color(1, 1, 1, 1)
        PushMatrix()
        Translate(0, 0, -2)
        #Translate(0, 0, -1.5)
        self.rot = Rotate(1, 0, 1, 0)
        UpdateNormalMatrix()
        
        vertex_format = [
            (b'v_pos', 3, 'float'),
            (b'v_normal', 3, 'float'),
            (b'v_tc0', 2, 'float')]
        
        texture = Image('bricks.png').texture
        
        self.measurement_meshes = []
        for set_idx in range(len(ALL_INDEX_SETS)):
            # NOTE: Indices should actually be of the expected size.
            self.measurement_meshes.append(Mesh(
                vertices=[],
                indices=list(range(INDICES_LENS[set_idx])),
                fmt=vertex_format,
                mode='triangles',
                texture=texture))
        
        # NOTE: Indices should actually be of the expected size.
        self.main_mesh = Mesh(
            vertices=[],
            indices=list(range(41328)),
            fmt=vertex_format,
            mode='triangles'
        )

        self.update_mesh_callback = Callback(self.update_mesh, needs_redraw=True)
        PopMatrix()

    def on_touch_move(self, touch):
        if touch.x - touch.ox < -10:
            app.root.ids.sm.transition.direction = 'left'
            app.root.ids.sm.current = 'measurements_screen'
        if touch.x - touch.ox > 10:
            app.root.ids.sm.transition.direction = 'right'
            app.root.ids.sm.current = 'in_screen'
            
    def on_enter(self):
        app.root.ids.render_button.text = 'Render'
        self.update_mesh_callback.ask_update()
        
        
class InputScreen(Screen):
    
    def on_touch_move(self, touch):
        if app.root.rendered:
            if touch.x - touch.ox < -10:
                app.root.ids.sm.transition.direction = 'left'
                app.root.ids.sm.current = 'render_screen'
            if touch.x - touch.ox > 10:
                app.root.ids.sm.transition.direction = 'right'
                app.root.ids.sm.current = 'measurements_screen'

        
class RenderButton(MDFillRoundFlatButton):

    class _TriggerFuncArgs():
        
        def __init__(self):
            self.height = 1.80
            self.weight = 80
            self.gender = 'female'

    def __init__(self, **kwargs):
        super(RenderButton, self).__init__(**kwargs)
        
        self._args = self._TriggerFuncArgs()
        self._calc_trigger = Clock.create_trigger(partial(self._calculate_all, self._args), timeout=0)
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            inputs = self._check_inputs()
            if inputs is not None:
                app.root.ids.render_button.text = 'Rendering...'
                
                self._args.height = inputs[0]
                self._args.weight = inputs[1]
                self._args.gender = inputs[2]
                
                self._calc_trigger()
                app.root.rendered = True
                
    @staticmethod
    def _calculate_all(args, dt):
        RenderButton._calculate_measurements(args.height, args.weight, args.gender)
        RenderButton._calculate_vertices(args.gender)
        
        app.root.ids.sm.transition.direction = 'left'
        app.root.ids.sm.current = 'render_screen'
        
    def _check_inputs(self):
        def _check_height(height_text):
            if not (len(height_text) == 4 and height_text[0].isdigit() and height_text[1] == '.' and \
                height_text[2].isdigit() and height_text[3].isdigit()):
                app.root.ids.height_text.error = True
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
        measurements = np.array([height, weight, weight / height ** 2, weight * height, 1.]) @ coefs_baseline * 100.
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
        
        app.vertices = m.vertices
        app.faces_data = m.smpl_faces_data
                

class FilteredTextField(MDTextField):
    
    pat = re.compile('[^0-9]')
    
    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join(
                re.sub(pat, '', s)
                for s in substring.split('.', 1)
            )
        return super().insert_text(s, from_undo=from_undo)
    

class RootWidget(Screen):
    
    rendered = False
    
    def verify_height(self, instance, text):
        if len(text) != 4 or (len(text) == 4 and not all([
                text[0].isdigit(),
                text[1] == '.',
                text[2].isdigit(),
                text[3].isdigit()])):
            instance.on_error(instance, True)
        else:
            instance.on_error(instance, False)
            
    def verify_weight(self, instance, text):
        if len(text) > 0 and all([x.isdigit() for x in text]) and (int(text) < 40 or int(text) > 200):
            instance.on_error(instance, True)
        elif all([x.isdigit() for x in text]):
            instance.on_error(instance, False)
        else: 
            instance.on_error(instance, True)


class RendererApp(MDApp):
    
    
    with open(resource_find('coefs.pkl'), 'rb') as handle:
        _coefs = pickle.load(handle)
        
    coefs_baseline_dict = {
        'male': _coefs['male_meas_coefs'].swapaxes(0, 1),
        'female': _coefs['female_meas_coefs'].swapaxes(0, 1)
    }
    
    coefs_shape = {
        'male': _coefs['male_shape_coefs'].swapaxes(0, 1),
        'female': _coefs['female_shape_coefs'].swapaxes(0, 1)
    }
    
    measurements = ListProperty([0.] * 15)
    vertices = ListProperty([0.] * 330624)
    smpl_vertices = np.zeros((6890, 3), dtype=np.float32).flatten()
    smpl_faces = np.zeros((13776, 3), dtype=np.float32).flatten()
    betas = ListProperty([0.] * 10)
    
    waist_mesh_indices = ListProperty([0])
    faces_data = ListProperty([0.] * 330624)
    
    smpl_model = {    
        'male': SMPLModel(resource_find('PY3_SMPL_MALE.pkl')),
        'female': SMPLModel(resource_find('PY3_SMPL_FEMALE.pkl'))
    }
    np.random.seed(9608)
    pose = np.zeros(shape=smpl_model['male'].pose_shape)
    trans = np.zeros(smpl_model['male'].trans_shape)
    
    def build(self):
        self.theme_cls.theme_style = "Dark"  # "Light"
        self.root = RootWidget()
        
        return self.root


if __name__ == "__main__":
    app = RendererApp()
    app.run()
'''

import kivy

from kivy.app import App
from kivy.uix.label import Label


class MyApp(App):

    def build(self):
        return Label(text='Hello world')


if __name__ == '__main__':
    MyApp().run()