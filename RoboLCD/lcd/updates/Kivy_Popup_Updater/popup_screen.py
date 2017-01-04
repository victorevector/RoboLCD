from kivy.properties import NumericProperty, ObjectProperty, StringProperty,  BooleanProperty
from kivy.clock import Clock
from kivy.uix.modalview import ModalView


class Updating_Popup(ModalView):
    def __init__(self,**kwargs):
        super(Updating_Popup,self).__init__(**kwargs)
        self.open()

