from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanelHeader
from scrollbox import ScrollBox, Scroll_Box_Even, Scroll_Box_Icons, Robo_Icons
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
        #icon way
        rc = Robo_Icons('Icons/Icon_Buttons/Robo_Controls.png', 'Robo Controls', 'ROBO_CONTROLS')
        wiz = Robo_Icons('Icons/Icon_Buttons/Wizards.png', 'Wizards', 'WIZARDS')
        net = Robo_Icons('Icons/Icon_Buttons/Networking.png', 'Network', 'NETWORK')
        upd = Robo_Icons('Icons/Icon_Buttons/Updates.png', 'Updates', 'UPDATES')
        fac = Robo_Icons('Icons/Icon_Buttons/Factory Reset.png', 'Factory Reset', 'FACTORY_RESET')
        opt = Robo_Icons('Icons/Icon_Buttons/Options.png', 'Options', 'OPTIONS')

        icons = [rc, wiz, net, upd, fac, opt]

        layout = Scroll_Box_Icons(icons)

        self.add_widget(layout)
        # list way
        # rc = Robo_Controls()
        # wiz = Wizards()
        # net = Network()
        # upd = Updates()
        # fac = Factory_Reset()
    
        # buttons = [rc, wiz, net, upd, fac]
    
        # layout = Scroll_Box_Even(buttons)
        # self.add_widget(layout)







class QRCodeScreen(BoxLayout):
    img_source = roboprinter.printer_instance.get_plugin_data_folder() + '/qr_code.png'

