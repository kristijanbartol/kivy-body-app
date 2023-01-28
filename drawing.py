import kivy

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Color, RenderContext, PushMatrix, PopMatrix
from kivy.graphics.fbo import Fbo


class Renderer(Widget):
    
    def __init__(self, **kwargs):
        super(Renderer, self).__init__(**kwargs)
        self.canvas = Fbo()
        with self.canvas:
            PushMatrix()
            Color(1, 0, 0)
            #PopMatrix()
            PushMatrix()
            Rectangle(pos=(10, 10), size=(500, 500))
            PushMatrix()
            #PopMatrix()


class MyApp(App):

    def build(self):
        return Renderer()


if __name__ == '__main__':
    MyApp().run()