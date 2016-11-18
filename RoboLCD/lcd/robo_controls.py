from .. import roboprinter
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.uix.image import Image
from kivy.graphics import *
from .. import roboprinter
from kivy.clock import Clock

class Extruder_Controls(Button):
    pass
class Manual_Control_Button(Button):
    pass
class Preheat_Button(Button):
    pass
class Cooldown_Button(Button):
    pass
class PLA_Button(Button):
    def _preheat_pla(self):
        # pre heat to 200 degrees celsius
        roboprinter.printer_instance._printer.set_temperature('tool0', 200.0)
class ABS_Button(Button):
    def _preheat_abs(self):
        # pre heat to 230 degrees celsius
        roboprinter.printer_instance._printer.set_temperature('tool0', 230.0)
class Empty_Button(Button):
    pass
class Preheat_Screen(BoxLayout):
    extruder_one_temp = NumericProperty(0)
    extruder_one_max_temp = NumericProperty(200)
    extruder_two_max_temp = NumericProperty(200)
    extruder_two_temp = NumericProperty(0)
    bed_max_temp = NumericProperty(200)
    bed_temp = NumericProperty(0)
    progress = StringProperty('')
    screen_up = True

    def update(self, dt):
        temps = roboprinter.printer_instance._printer.get_current_temperatures()
        current_data = roboprinter.printer_instance._printer.get_current_data()
        if 'tool0' in temps.keys():
            self.extruder_one_temp = temps['tool0']['actual']
            self.extruder_one_max_temp = temps['tool0']['target']
        else:
            self.extruder_one_temp = 0
            self.extruder_one_max_temp = 0

        if 'bed' in temps.keys():
            self.bed_temp = temps['bed']['actual']
            self.bed_max_temp = temps['bed']['target']
        else:
            self.bed_temp = 0
            self.bed_max_temp = 0

        if 'tool1' in temps.keys():
            self.extruder_two_temp = temps['tool1']['actual']
            self.extruder_two_max_temp = temps['tool1']['target']
        else:
            self.extruder_two_temp = 0
            self.extruder_two_max_temp = 0

        if self.screen_up != True:
            return False

    def schedule_update(self):
        Clock.schedule_interval(self.update, 1/30)

    def update_screen(self):
        self.screen_up = False

    def stop_button(self):
        roboprinter.printer_instance._printer.set_temperature('tool0', 0)

    


    