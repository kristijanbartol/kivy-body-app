from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ListProperty
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
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


MEASUREMENT_NAMES = [
    'A',
    'B',
    'C',
    'D',
    'E',
    'F',
    'G',
    'H',
    'I',
    'J',
    'K',
    'L',
    'M',
    'N',
    'O'
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
        
        smpl_model_resource = resource_find('updated_smpl_model.pkl')

        
        smpl = SMPLModel(smpl_model_resource)
        np.random.seed(9608)
        pose = np.zeros(shape=smpl.pose_shape)
        #beta = (np.random.rand(*smpl.beta_shape) - 0.5) * 0.06
        trans = np.zeros(smpl.trans_shape)
        smpl.set_params(beta=app.betas, pose=pose, trans=trans)

        vertices = smpl.verts.squeeze()
        faces = smpl.faces.squeeze()

        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, vertex_colors=np.tile([.7, .7, .7], (6890, 1)))

        vertex_normals = trimesh.geometry.weighted_vertex_normals(
            vertex_count=len(mesh.vertices),
            faces=mesh.faces,
            face_normals=mesh.face_normals,
            face_angles=mesh.face_angles)
        setattr(mesh, 'vertex_normals', vertex_normals)
        
        self.scene = ObjFile(trimesh.exchange.export.export_obj(mesh))
        
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
        
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            app.root.ids.sm.current = 'measurements_screen'
        
        
class RenderButton(Button):
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._calculate_measurements()
            app.root.ids.sm.current = 'render_screen'
    
    @staticmethod
    def _calculate_measurements():
        try:
            height = float(app.root.ids.height_text.text)
            weight = float(app.root.ids.weight_text.text)
            
            app.measurements = np.array([height, weight, 1.]) @ app.male_coefs_baseline * 100.
            app.betas = np.array([height, weight, 1.]) @ app.male_coefs_shape
            
            # TODO: Need to update measurements and betas as ListProperties.
            
            for midx, mvalue in enumerate(app.measurements):
                app.root.ids[f'meas{midx+1}'].text = f'{MEASUREMENT_NAMES[midx]}: {mvalue:.2f}cm'
                
            #for bidx in range(10):
            #    app.root.betas[bidx] = 
        except ValueError:
            pass
        

class RootWidget(Screen):
    
    pass


class RendererApp(App):
    
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
    betas = ListProperty([0.] * 10)
    
    def build(self):
        self.root = RootWidget()
        return self.root


if __name__ == "__main__":
    app = RendererApp()
    app.run()
