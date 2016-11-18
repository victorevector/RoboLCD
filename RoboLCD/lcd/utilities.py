from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanelHeader
from scrollbox import ScrollBox, Scroll_Box_Even
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from .. import roboprinter
from netconnectd import NetconnectdClient
from kivy.logger import Logger

#Buttons

class Robo_Controls(Button):
    pass
class Wizards(Button):
    pass
class Network(Button):
    pass
class Updates(Button):
    pass
class Factory_Reset(Button):
    pass

class UtilitiesTab(TabbedPanelHeader):
    """
    Represents the Utilities tab header and dynamic content
    """
    pass


class UtilitiesContent(BoxLayout):
    def __init__(self, **kwargs):
        super(UtilitiesContent, self).__init__()

        rc = Robo_Controls()
        wiz = Wizards()
        net = Network()
        upd = Updates()
        fac = Factory_Reset()
    
        buttons = [rc, wiz, net, upd, fac]
    
        layout = Scroll_Box_Even(buttons)
        self.add_widget(layout)







class QRCodeScreen(BoxLayout):
    img_source = roboprinter.printer_instance.get_plugin_data_folder() + '/qr_code.png'

