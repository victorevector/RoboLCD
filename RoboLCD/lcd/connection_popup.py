from kivy.graphics import *
from .. import roboprinter
from kivy.clock import Clock
from kivy.uix.popup import Popup
from pconsole import pconsole
from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty, NumericProperty
from wizard import ZoffsetWizard


class Connection_Popup(ModalView):
    def reconnect_button(self):
        options = roboprinter.printer_instance._printer.connect()

class Updating_Popup(ModalView) :
    pass

class Zoffset_Warning_Popup(ModalView):
    """docstring for Zoffset_Warning_Popup(ModalView)"""
    current_z_offset = StringProperty('--')
    
    def __init__(self, _file_printer):
        super(Zoffset_Warning_Popup, self).__init__()
        self.file_printer = _file_printer

        self.current_z_offset = str(pconsole.zoffset['Z'])
        roboprinter.printer_instance._logger.info("Starting up the Zoffset Warning!")

    def update_z_offset(self):
        self.current_z_offset = str(pconsole.zoffset['Z'])
        
    def dismiss_popup(self):
        self.dismiss()
    def start_print_button(self):
        self.dismiss()
        self.file_printer.force_start_print()

class Mintemp_Warning_Popup(ModalView):
    current_temp = StringProperty('--')
    def __init__(self, temp):
        super(Mintemp_Warning_Popup, self).__init__()
        self.current_temp = 'Min Temp: ' + str(temp)
        self.open()
        Clock.schedule_once(self.popup_timer, 5)

    def popup_timer(self,dt):
        self.dismiss()

