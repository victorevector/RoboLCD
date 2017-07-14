from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty, ListProperty
from .. import roboprinter


class Filament_Wizard_1_5(FloatLayout):
    callback = ObjectProperty(None)
    def __init__(self, callback, **kwargs):
        self.callback = callback
        super(Filament_Wizard_1_5, self).__init__()
    

class Filament_Wizard_2_5(FloatLayout):
    extruder_temp = NumericProperty(0)
    extruder_max_temp = NumericProperty(230)
    def __init__(self, extruder_temp):
        super(Filament_Wizard_2_5, self).__init__()
        self.extruder_max_temp = extruder_temp
    
    def update_temp(self, temp):
        self.extruder_temp = temp
        #Logger.info('temp sent: ' + str(self.extruder_temp))

class Filament_Wizard_3_5(FloatLayout):
    callback = ObjectProperty(None)
    def __init__(self, callback, **kwargs):
        self.callback = callback
        super(Filament_Wizard_3_5, self).__init__()

class Filament_Wizard_4_5(FloatLayout):
    callback = ObjectProperty(None)
    def __init__(self, callback, **kwargs):
        self.callback = callback
        super(Filament_Wizard_4_5, self).__init__()

class Filament_Wizard_5_5(FloatLayout):
    callback = ObjectProperty(None)
    def __init__(self, callback, **kwargs):
        self.callback = callback
        super(Filament_Wizard_5_5, self).__init__()

class Filament_Wizard_Finish(FloatLayout):
    def __init__(self):
        super(Filament_Wizard_Finish, self).__init__()
        pass
    
    def button_function(self):
        Logger.info("Button was pushed")
        roboprinter.robosm.go_back_to_main()