from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty, ListProperty
from .. import roboprinter


class Z_Offset_Wizard_1_4(FloatLayout):
    pass

class Z_Offset_Wizard_2_4(FloatLayout):
    pass

class Z_Offset_Wizard_3_4(FloatLayout):
    i_toggle_mm = ['Icons/Manual_Control/increments_2_1.png', 'Icons/Manual_Control/increments_2_2.png']
    s_toggle_mm = ['0.1mm', '0.2mm']
    f_toggle_mm = [0.1, 0.2]
    toggle_mm = 0
    def toggle_mm_z(self):
        self.toggle_mm += 1
        if self.toggle_mm > 1:
            self.toggle_mm = 0

        Logger.info(self.s_toggle_mm[self.toggle_mm])
        self.ids.toggle_label.text = self.s_toggle_mm[self.toggle_mm]
        self.ids.toggle_icon.source = self.i_toggle_mm[self.toggle_mm]
    def _jog(self, direction):
        # determine increment value
        increment = direction * self.f_toggle_mm[self.toggle_mm]
       
        roboprinter.printer_instance._printer.jog('z', increment)

class Z_Offset_Wizard_4_4(FloatLayout):
    pass

class Z_Offset_Wizard_Finish(FloatLayout):
    z_value = NumericProperty(0)
    pass