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

class Error_Popup(ModalView):
    error = StringProperty('Error')
    body_text = StringProperty('error')
    def __init__(self, error, body_text):
        super(Error_Popup, self).__init__()
        self.error = error
        self.body_text = body_text
        self.ids.error_ok.bind(on_press = self.dismiss)

    def show(self):
        self.open()
       

class Warning_Popup(ModalView):
    warning = StringProperty("None")
    body_text = StringProperty("none")
    def __init__(self, warning, body_text):
        super(Warning_Popup, self).__init__()
        self.warning = warning
        self.body_text = body_text

    def show(self):
        self.open()

class Status_Popup(ModalView):
    error = StringProperty('Error')
    body_text = StringProperty('error')
    def __init__(self, error, body_text):
        super(Status_Popup, self).__init__()
        self.error = error
        self.body_text = body_text
        

    def show(self):
        self.open()
    def hide(self):
        self.dismiss()

class USB_Progress_Popup(ModalView):
    max_progress = NumericProperty(100)
    value_progress = NumericProperty(0)

    error = StringProperty('Error')
    
    def __init__(self, error, max_progress):
        super(USB_Progress_Popup, self).__init__()
        self.error = error
        self.max_progress = max_progress

    def show(self):
        self.open()
    def hide(self):
        self.dismiss()

    def update_progress(self, progress):
        self.value_progress = progress
    def update_max(self, max_prog):
        self.max_progress = max_prog
