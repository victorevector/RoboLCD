from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty, ListProperty
from .. import roboprinter
from printer_jog import printer_jog
from kivy.clock import Clock


class Z_Offset_Wizard_1_4(FloatLayout):
    pass

class Z_Offset_Wizard_2_4(FloatLayout):
    
    def __init__(self):
        super(Z_Offset_Wizard_2_4, self).__init__()
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
        jogger = {'z': increment}
        printer_jog.jog(desired=jogger, speed=1500, relative=True)

class Z_Offset_Wizard_4_4(FloatLayout):
    pass

class Z_Offset_Wizard_Finish(FloatLayout):
    z_value = NumericProperty(0)
    pass

class Z_Offset_Temperature_Wait_Screen(FloatLayout):

    body_text = StringProperty("To avoid melting the bed, the printer will now wait for\nthe Extruder to cool down")
    temperature = StringProperty("999")
    bed_temp = StringProperty("999")


    def __init__(self, callback):
        super(Z_Offset_Temperature_Wait_Screen, self).__init__()
        #setup callback
        model = roboprinter.printer_instance._settings.get(['Model'])
        if model == "Robo R2": 
            self.body_text = "To avoid melting the bed, the printer will now wait for\nthe Extruder and the bed to cool down"
            Clock.schedule_interval(self.temp_callback_R2, 0.5)
        else:
            Clock.schedule_interval(self.temperature_callback, 0.5)

        self.callback = callback
        

    def temperature_callback(self,dt):
        temps = roboprinter.printer_instance._printer.get_current_temperatures()
        position_found_waiting_for_temp = False

        #get current temperature
        if 'tool0' in temps.keys():
            temp = temps['tool0']['actual']
            self.temperature = str(temp)

            if temp < 100:
                position_found_waiting_for_temp = True
                #go to the next screen
                self.callback()
                return False
        

    def temp_callback_R2(self, dt):
        temps = roboprinter.printer_instance._printer.get_current_temperatures()
        position_found_waiting_for_temp = False
        bed = 100
        #get current temperature
        if 'tool0' in temps.keys():
            temp = temps['tool0']['actual']
            self.temperature = str(temp)

        if 'bed' in temps.keys():
            bed = temps['bed']['actual']
            self.bed_temp = str(bed)

            if temp < 100 and bed < 60:
                position_found_waiting_for_temp = True
                #go to the next screen
                self.callback()
                return False

        




