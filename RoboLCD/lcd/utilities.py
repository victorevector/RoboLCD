from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanelHeader
from scrollbox import ScrollBox, Scroll_Box_Even, Scroll_Box_Icons, Robo_Icons
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from .. import roboprinter
from netconnectd import NetconnectdClient
from kivy.logger import Logger
from kivy.clock import Clock

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

        self.state = 'NOT_PRINTING'
        self.last_state = None
        Clock.schedule_interval(self.monitor_layout, 1)

    def monitor_layout(self, dt):
        if roboprinter.printer_instance._printer.is_printing() != True:
            self.state = 'NOT_PRINTING'
        elif roboprinter.printer_instance._printer.is_printing() == True:
            self.state = 'PRINTING'

        if self.last_state != self.state:
            self.last_state = self.state
            self.clear_widgets()

            wiz = Robo_Icons('Icons/White_Utilities/Wizards.png', 'Wizards', 'WIZARDS')

            if self.state == 'NOT_PRINTING':
                rc = Robo_Icons('Icons/White_Utilities/Controls.png', 'Robo Controls', 'ROBO_CONTROLS')
                wiz.button_state = False
            elif self.state == 'PRINTING' :
                rc = Robo_Icons('Icons/White_Utilities/Print tuning_White.png', 'Print Tuning', 'PRINT_TUNING')
                wiz.button_state = True
            
            net = Robo_Icons('Icons/White_Utilities/Networking.png', 'Network', 'NETWORK')
            upd = Robo_Icons('Icons/White_Utilities/Updates.png', 'Update', 'UPDATES')
            sys = Robo_Icons('Icons/System_Icons/Shutdown 2.png', 'System', 'SYSTEM')
            opt = Robo_Icons('Icons/White_Utilities/Options.png', 'Options', 'OPTIONS')

            icons = [rc, wiz, net, upd, opt, sys]

            layout = Scroll_Box_Icons(icons)

            self.add_widget(layout)




class QRCodeScreen(BoxLayout):
    img_source = roboprinter.printer_instance.get_plugin_data_folder() + '/qr_code.png'
