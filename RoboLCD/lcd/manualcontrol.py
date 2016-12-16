from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.graphics import *
from kivy.uix.label import Label
from connection_popup import Mintemp_Warning_Popup
from .. import roboprinter
from printer_jog import printer_jog

# class Control(Widget):
#     manualcontrol = ObjectProperty(ManualControl() )
#     tempcontrol = ObjectProperty(TemperatureControl() )
#     active = StringProperty('manual')
#
#     def toggle_control(self, *args, **kwargs):
#         if self.active == 'manual':
#             self.

class MotorControl(GridLayout):
    mms = ListProperty([0.1,1,10,100])
    inx = NumericProperty(0)
    toggle_pic = ['Icons/Manual_Control/increments_4_1.png', 'Icons/Manual_Control/increments_4_2.png', 'Icons/Manual_Control/increments_4_3.png', 'Icons/Manual_Control/increments_4_4.png' ]

    def move_pos(self, axis):
        if axis == 'e' and self.temperature() < 175:
            Mintemp_Warning_Popup(self.temperature())
        else:
            amnt = self.mms[self.inx]
            self._move(axis, amnt)

    def move_neg(self, axis):
        if axis == 'e' and self.temperature() < 175:
            Mintemp_Warning_Popup(self.temperature())
        else:
            amnt = -self.mms[self.inx]
            self._move(axis, amnt)

    def _move(self, axis, amnt):
        jogger = {axis:amnt}
        printer_jog.jog(desired=jogger, speed=1500, relative=True)

    def toggle_mm(self):
        if self.inx == 3:
            self.inx = 0
        else:
            self.inx += 1
       
        self.ids.toggle_pic.source = self.toggle_pic[self.inx]

    def home(self):
        roboprinter.printer_instance._printer.home(['x', 'y', 'z'])

    def temperature(self):
        temps  = roboprinter.printer_instance._printer.get_current_temperatures()
        current_temperature = ''
        current_temperature = int(temps['tool0']['actual'])
        
        return current_temperature

class TemperatureControl(GridLayout):
    current_temp = StringProperty('--')
    input_temp = StringProperty('')

    def __init__(self, **kwargs):
        super(TemperatureControl, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, .1)

    def update(self, dt):
        if self.input_temp == '':
            self.ids.set_cool.text = 'Cooldown'
            self.ids.set_cool.background_normal = 'Icons/blue_button_style.png'
        else:
            self.ids.set_cool.text = 'Set'
            self.ids.set_cool.background_normal = 'Icons/green_button_style.png'
        if len(self.input_temp) > 3:
            self.input_temp = self.input_temp[:3]
        self.current_temp = self.temperature()
        if self.current_temp == self.input_temp:
            self.ids.c_temp.color = 0,1,0,1

    def temperature(self):
        temps  = roboprinter.printer_instance._printer.get_current_temperatures()
        current_temperature = ''
        try:
            current_temperature = str(int(temps['tool0']['actual']))
        except Exception as e:
            current_temperature = '--'
        return current_temperature

    def set_temperature(self, ext):
        self.ids.c_temp.color = 1,0,0,0.8
        if self.input_temp == '':
            temp = 0
            self.input_temp = "0"
        else:
            temp = int(self.input_temp)
            if temp > 290:
                temp = 290
                self.input_temp = "290"

        
            
        roboprinter.printer_instance._printer.set_temperature(ext, temp )

class Motor_Control(Button):
    pass
class Temperature_Control(Button):
    pass