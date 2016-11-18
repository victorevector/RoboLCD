def start():
    import os
    os.environ["KIVY_NO_ARGS"] = "1"
    os.environ["KIVY_NO_CONSOLELOG"] = "1"

    import sys
    sys.dont_write_bytecode = True
    import logging
    import re
    import sysv_ipc
    import json
    import threading
    import kivy
    import subprocess
    import shlex

    kivy.require('1.9.1')
    from kivy.config import Config
    Config.set('kivy', 'keyboard_mode', 'dock')
    Config.set('graphics', 'height', '320')
    Config.set('graphics', 'width', '480')
    Config.set('graphics', 'borderless', '1')
    Config.set('input', '%(name)s', 'probesysfs,provider=hidinput,param=rotation=270,param=invert_y=1')

    from kivy.app import App
    from kivy.lang import Builder
    from kivy.resources import resource_add_path
    from kaapopup import KaaPopup, UpdateScreen
    from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.button import Button
    from kivy.uix.togglebutton import ToggleButton
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label
    from functools import partial
    from kaapopup import KaaPopup, UpdateScreen,CompletePopup, ErrorPopup, get_update_lists, UPDATE_LOG, NoupdatePopup
    from mainscreen import MainScreen, MainScreenTabbedPanel
    from files import FilesTab, FilesContent, PrintFile, PrintUSB
    from utilities import UtilitiesTab, UtilitiesContent, QRCodeScreen
    from printerstatus import PrinterStatusTab, PrinterStatusContent
    from wifi import WifiButton, WifiPasswordInput, WifiConfirmation, WifiConfigureButton, APButton, AP_Mode, APConfirmation, IPAddressButton, SuccessButton, WifiUnencrypted, WifiConfiguration, WifiConnecting
    from robo_controls import Extruder_Controls,Preheat_Screen, Empty_Button, ABS_Button, PLA_Button, Manual_Control_Button, Preheat_Button, Cooldown_Button
    from wifi import QR_Button, WifiButton, WifiPasswordInput, WifiConfirmation, WifiConfigureButton, APButton, StartAPButton, APConfirmation, IPAddressButton, SuccessButton, WifiUnencrypted
    from backbuttonscreen import BackButtonScreen
    from noheaderscreen import NoHeaderScreen
    from manualcontrol import MotorControl, TemperatureControl, Motor_Control, Temperature_Control
    from wizard import Filament_Change_Wizard_Button, WizardButton, PreheatWizard, FilamentWizard, ZoffsetWizard, Z_Offset_Wizard_Button, Filament_Loading_Wizard_Button
    from scrollbox import ScrollBox, Scroll_Box_Even
    from netconnectd import NetconnectdClient
    from .. import roboprinter
    from kivy.logger import Logger
    import thread
    from kivy.core.window import Window
    from kivy.clock import Clock
    from kivy.uix.popup import Popup
    from pconsole import pconsole
    from robo_sm import screen_manager
    from connection_popup import Connection_Popup, Updating_Popup
    import subprocess
    Logger.info('Start')

    # ========== Starting Message queue thread.===================
	# queue key
    QUEUE_KEY = 2016
    SEND_QUEUE_KEY = 6102
    mq = None
    try:
        mq = sysv_ipc.MessageQueue(QUEUE_KEY, sysv_ipc.IPC_CREAT)

        Logger.info("Found mq")
    except Exception as e:
        Logger.info("no Found mq: {}".format(e))
        pass

    class RoboScreenManager(ScreenManager):
        """
        Root widget
        Encapsulates methods that are both neeeded globally and needed by descendant widgets to execute screen related functions. For example, self.generate_file_screen(**) is stored in this class but gets used by its descendant, the FileButton widget.
        """
        connection_popup = None
        wifi_grid = []
        wifi_list = []

        def __init__(self, **kwargs):
            super(RoboScreenManager, self).__init__(transition=NoTransition())
            kaa_thread = threading.Thread(target=self.receive_message)
            kaa_thread.start()
            Logger.info("Starting kaa_thread...")
            Clock.schedule_interval(self.check_connection_status, .5)
            pconsole.initialize_eeprom()
            pconsole.generate_eeprom()


        def check_connection_status(self, dt):
            """Is aware of printer-sbc connection """
            is_closed_or_error = roboprinter.printer_instance._printer.is_closed_or_error()

            if roboprinter.printer_instance._printer.get_current_connection()[0] == 'Closed':
                is_closed = True
            else:
                is_closed = False

            is_error = roboprinter.printer_instance._printer.is_error()

            if is_closed and self.connection_popup is None:
                Logger.info('Popup: Init')
                self.connection_popup = self.generate_connection_popup()

            if is_error and self.connection_popup is None:
                self.connection_popup = self.generate_connection_popup()

            if not is_closed_or_error and self.connection_popup is not None:
                Logger.info('Popup: Dismissed')
                self.connection_popup.dismiss()
                self.connection_popup = None

        def generate_connection_popup(self, *args, **kwargs):
            if roboprinter.printer_instance.firmware_updating() == False:
            
                p = Connection_Popup()

                p.open()
                return p
            elif roboprinter.printer_instance.firmware_updating() == True:
                p = Updating_Popup()

                p.open()

                Clock.schedule_interval(self.check_flashing, 1)

                return p
        def check_flashing(self, dt):
            if roboprinter.printer_instance.firmware_updating() == False:
                #restart the server
                subprocess.call("sudo service octoprint restart", shell=True)

                return False
            

        def receive_message(*args):
            """
            Receive Message from C SDK on Raspberry pi.
            :return:
            """
            Logger.info("Received message started:")

            while True:

                (message, priority) = mq.receive()

                Logger.info('Received message: {}'.format(message))
                try:
                    match = re.match('^\#R\#(.*)\#E\#$', message)
                    if match.group(1) is not None:
                      command = match.group(1)

                    msg = json.loads(command.decode("utf-8"))
                    Logger.info('Received message as json: {}'.format(msg))
                except Exception as e:
                    Logger.info('json error:  {}'.format(e))

                try:
                    if msg["type"] == "NEW":
                        id = int(msg["id"])
                        Logger.info('id: {}'.format(id))
                        p = KaaPopup(message=id)
                        p.open()
                    # response = {"type": "NEW_REQ" "id": id, "res", res}

                    # when receive update response.
                    elif msg["type"] == "UPDATE_RES":
                        result = msg["result"]
                        if result == "success":
                            complete = CompletePopup()
                            complete.open()
                        elif result == "error":
                            error = ErrorPopup()
                            error.open()
                        elif result == "NoUpdates":
                            noupdate = NoupdatePopup()
                            noupdate.open()
                        else:
                            error = ErrorPopup()
                            error.open()

                    elif msg["type"] == "NEW_RES":
                        result = msg["result"]
                        if result == "success":
                            complete = CompletePopup()
                            complete.open()
                        else:
                            error = ErrorPopup()
                            error.open()
                except Exception as e:
                    Logger.info("receive message error: {}".format(e))

        def generate_update_screen(self, **kwargs):

            Logger.info('starting update screen')
            update_screen = UpdateScreen()
            Logger.info('ending updatge screen')
            self._generate_backbutton_screen(name=kwargs['name'], title=kwargs['title'], back_destination=kwargs['back_destination'], content=update_screen)

            return

        def run_kaapopup(self, **kwargs):
            Logger.info('starting run_kaapopup')
            update_lists = get_update_lists()
            Logger.info('update_lists: {}'.format(update_lists))
            if len(update_lists) != 0:
                p = KaaPopup(update="True")
                p.open()
            else:
                n = NoupdatePopup()
                n.open()

        def generate_file_screen(self, **kwargs):
            # Accesible to FilesButton
            # Instantiates BackButtonScreen and passes values for dynamic properties:
            # backbutton label text, print information, and print button.
            file_name = kwargs['filename']
            print_layer_height = kwargs['layer_height']
            print_layers = kwargs['layers']
            #print_duration = kwargs['print_duration']
            #print_volume = kwargs['print_volume']
            print_length = kwargs['print_length']
            file_path = kwargs['file_path']
            is_usb = kwargs['is_usb']
            title = file_name.replace('.gcode', '').replace('.gco', '')
            if len(title) > 10:
                title = title[:9] + '...'

            Logger.info('Function Call: generate_new_screen {}'.format(file_name))

            def delete_file(*args): #gets binded to CTA in header
                roboprinter.printer_instance._file_manager.remove_file(file_path, file_name)
                self.go_back_to_main('files_tab')

            if is_usb:
                c = PrintUSB(name='print_file', file_name=file_name,print_layer_height = print_layer_height, print_layers = print_layers, print_length=print_length, file_path=file_path)
            else:
                c = PrintFile(name='print_file', file_name=file_name,print_layer_height = print_layer_height, print_layers = print_layers, print_length=print_length, file_path=file_path)

            if not is_usb:
                self._generate_backbutton_screen(name=c.name, title=title, back_destination='main', content=c, cta=delete_file, icon='Icons/trash.png')
            else:
                self._generate_backbutton_screen(name=c.name, title=title, back_destination='main', content=c)

            return

        def generate_network_utilities_screen(self, **kwargs):
            #generates network option screen. Utilities > Network > Network Utilities > wifi list || start ap
            cw = WifiConfigureButton()
            ap = APButton()
            ip = IPAddressButton()
            qr = QR_Button()
            buttons = [cw, ap, ip, qr]

            sb = Scroll_Box_Even(buttons)

            self._generate_backbutton_screen(name=kwargs['name'], title=kwargs['title'], back_destination=kwargs['back_destination'], content=sb)

        def generate_ip_screen(self, **kwargs):
            # Misnomer -- Network Status
            def get_network_status():
                netcon = NetconnectdClient()
                try:
                    #Determine mode and IP
                    status = netcon._get_status()
                    wifi = status['connections']['wifi']
                    ap = status['connections']['ap']
                    wired = status['connections']['wired']

                    if wifi and wired:
                        ssid = status['wifi']['current_ssid']
                        ip = netcon.get_ip()
                        mode = 'Wifi  \"{}\"'.format(ssid)
                        mode += ' and Wired Ethernet'
                    elif wifi:
                        ssid = status['wifi']['current_ssid']
                        ip = netcon.get_ip()
                        mode = 'Wifi  \"{}\"'.format(ssid)
                    elif ap and wired:
                        mode = 'Hotspot mode and Wired Ethernet'
                        ip = '10.250.250.1' + ' , ' + netcon.get_ip()
                    elif ap:
                        mode = 'Hotspot mode'
                        ip = '10.250.250.1'
                    elif wired:
                        mode = 'Wired ethernet'
                        ip = netcon.get_ip()
                    else:
                        mode = 'Neither in hotspot mode or connected to wifi'
                        ip = ''
                    hostname = netcon.hostname()
                except Exception as e:
                    mode = 'Error -- could not determine'
                    ip = 'Error -- could not determine'
                    hostname = 'Error -- could not determine'
                    Logger.error('RoboScreenManager.generate_ip_screen: {}'.format(e))
                t = 'Connection status: \n    {}\n\n IP: \n    {}\n\n Hostname: \n    {}'.format(mode, ip, hostname)
                c.text = t
                return
            t = "Getting network status..."
            c = Label(text=t, font_size=30, background_color=[0,0,0,1])
            self._generate_backbutton_screen(name=kwargs['name'], title=kwargs['title'], back_destination=kwargs['back_destination'], content=c)
            thread.start_new_thread(get_network_status, ())

        def generate_start_apmode_screen(self, **kwargs):
            #generate screen with button prompting user to start ap mode
            AP_Mode(self, 'hotspot')

        def generate_wificonfig(self, *args, **kwargs):
            if kwargs['back_destination']:
                back_d = kwargs['back_destination']
            else:
                back_d = 'main'
            # pass control of wifi configuration sequences to WifiConfiguration
            WifiConfiguration(roboscreenmanager=self, back_destination=back_d)



        def _generate_backbutton_screen(self, name, title, back_destination, content, **kwargs):
            #helper function that instantiate the screen and presents it to the user
            # input are screen properties that get presented on the newly generated screen
            s = BackButtonScreen(name=name, title=title, back_destination=back_destination, content=content, **kwargs)
            s.populate_layout()
            self.add_widget(s)
            self.current = s.name

            return s

        def generate_wizards_screen(self, **kwargs):
            name = kwargs['name']
            title = kwargs['title']
            back_destination = kwargs['back_destination']

            z = Z_Offset_Wizard_Button()
            fl = Filament_Loading_Wizard_Button()
            fc = Filament_Change_Wizard_Button()
            buttons = [z,fl,fc]

            c = Scroll_Box_Even(buttons)

            self._generate_backbutton_screen(name=name, title=title, back_destination=back_destination, content=c)

        def generate_qr_screen(self, **kwargs):
            #generates the screen with a QR code image
            #
            c = QRCodeScreen()
            self._generate_backbutton_screen(name=kwargs['name'], title=kwargs['title'], back_destination=kwargs['back_destination'], content=c)
            return

        def go_back_to_main(self, tab=None):
            #Moves user to main screen and deletes all other screens
            #used by end of sequence confirmation buttons
            #optional tab parameter. If not None it will go back to that tab
            Logger.info('Function Call: go_back_to_main')
            self.current = 'main'

            if tab is not None:
                main = self.current_screen
                main.open_tab(tab)

            #remove all screens that are not main
            for s in self.screen_names:
                if s is not 'main':
                    d = self.get_screen(s)
                    self.remove_widget(d)
                else:
                    continue


            Logger.info('Screens: {}'.format(
                self.screen_names))  # not necessary; using this to show me that screen gets properly deleted

        def go_back_to_screen(self, current, destination):
            # Goes back to destination and deletes current screen
            ps = self.get_screen(current)
            self.current = destination
            self.remove_widget(ps)
            Logger.info('go_back_to_screen: current {}, dest {}'.format(current, destination))

            if current == 'wifi_config[1]':
                Window.release_all_keyboards()
            #used to delete keyboards after user hits backbutton from Wifi Config Screen. This is a brute force implementation.... TODO figure out a more elegant and efficient way to perform this call.

            return

        def generate_zaxis_wizard(self, **kwargs):
            """
            """
            ZoffsetWizard(robosm=self, back_destination=kwargs['back_destination'])

        def generate_manualcontrol_screen(self, **kwargs):
            name = kwargs['name']
            title = kwargs['title']
            back_destination = kwargs['back_destination']

            c = Motor_Control()

            buttons = [c]
            layout = Scroll_Box_Even(buttons)

            self._generate_backbutton_screen(name=name, title=title, back_destination=back_destination, content=layout)

        def generate_motor_controls(self, **kwargs):
            name = kwargs['name']
            title = kwargs['title']
            back_destination = kwargs['back_destination']

            c = MotorControl()

            self._generate_backbutton_screen(name=name, title=title, back_destination=back_destination, content=c)

        def generate_temperature_controls(self, **kwargs):
            name = kwargs['name']
            title = kwargs['title']
            back_destination = kwargs['back_destination']

            c = TemperatureControl()

            self._generate_backbutton_screen(name=name, title=title, back_destination=back_destination, content=c)

        def generate_robo_controls(self, **kwargs):
            _name = kwargs['name']

            extruder = Extruder_Controls()
            manual = Motor_Control()



            buttons = [extruder, manual]

            layout = Scroll_Box_Even(buttons)

            self._generate_backbutton_screen(name = _name, title = kwargs['title'], back_destination=kwargs['back_destination'], content=layout)
            return

        def generate_extrudercontrol_screen(self, **kwargs):
            _name = kwargs['name']

            t = Temperature_Control()
            preheat = Preheat_Button()
            cooldown = Cooldown_Button()

            buttons = [t, preheat,cooldown]

            layout = Scroll_Box_Even(buttons)

            self._generate_backbutton_screen(name = _name, title = kwargs['title'], back_destination=kwargs['back_destination'], content=layout)
            return


        def generate_preheat_wizard(self, **kwargs):
            _name = kwargs['name']
            # preheat wizard layout
            c = PreheatWizard(self, name=_name) #pass self so that Preheat can render secondary screens
            self._generate_backbutton_screen(name=_name, title=kwargs['title'], back_destination=kwargs['back_destination'], content=c)

            return
        def generate_Preheat_Screen(self, **kwargs):
            _name = kwargs['name']
            screen = Preheat_Screen()
            screen.schedule_update()
            self._generate_backbutton_screen(name = _name, title=kwargs['title'], back_destination=kwargs['back_destination'], content=screen)

        def generate_preheat_list(self, **kwargs):
            _name = kwargs['name']

            pla = PLA_Button()
            ab = ABS_Button()
            placeholder = Empty_Button()
            layout = GridLayout(cols=1, padding=0, spacing=[0,0], size_hint=(1, None),)
            layout.add_widget(pla)
            layout.add_widget(ab)
            layout.add_widget(placeholder)

            self._generate_backbutton_screen(name = _name, title = kwargs['title'], back_destination=kwargs['back_destination'], content=layout)
            pass
        def cooldown_button(self, value):
            roboprinter.printer_instance._printer.commands('M104 S0')
            roboprinter.printer_instance._printer.commands('M140 S0')
            self.go_back_to_main('printer_status_tab')
            return

        def generate_cooldown(self, **kwargs):
            _name = kwargs['name']
            layout = GridLayout(cols = 3, rows = 3, orientation = 'vertical')
            layout.add_widget(Label(size_hint_x = None))
            layout.add_widget(Label(size_hint_x = None))
            layout.add_widget(Label(size_hint_x = None))
            layout.add_widget(Label(size_hint_x = None))
            cb = Button(text = 'Cooldown', font_size = 30, background_normal = 'Icons/button_start_blank.png', halign = 'center', valign = 'middle', width = 300, height = 100)
            layout.add_widget(cb)
            layout.add_widget(Label(size_hint_x = None))
            layout.add_widget(Label(size_hint_x = None))
            layout.add_widget(Label(size_hint_x = None))
            layout.add_widget(Label(size_hint_x = None))
            cb.bind(on_press = self.cooldown_button)
            self._generate_backbutton_screen(name=_name, title=kwargs['title'], back_destination=kwargs['back_destination'], content=layout)

            return


        def generate_filament_wizard(self, **kwargs):
            # Instantiates the FilamentWizard and gives it a screen. Passes management of filament wizard related screens to FilamentWizard instance.
            FilamentWizard('LOAD',self, name=kwargs['name'],title=kwargs['title'], back_destination=kwargs['back_destination']) #pass self so that FilamentWizard can render itself
            return

        def genetate_filament_change_wizard(self, **kwargs):
            FilamentWizard('CHANGE',self, name=kwargs['name'],title=kwargs['title'], back_destination=kwargs['back_destination']) #pass self so that FilamentWizard can render itself
            return


    class RoboLcdApp(App):

        def build(self):
            # Root widget is RoboScreenManager
            dir_path = os.path.dirname(os.path.realpath(__file__))
            resource_add_path(dir_path) #kivy will look for images and .kv files in this directory path/to/RoboLCD/lcd/
            printer_info = roboprinter.printer_instance._printer.get_current_connection()

            # Determine what kivy rules to implement based on screen size desired. Will use printerprofile to determine screen size
            printer_type = roboprinter.printer_instance._settings.global_get(['printerProfiles', 'default'])
            if printer_type == "r2":
                sm = Builder.load_file('lcd_large.kv')
                Logger.info('Screen Type: {}'.format('r2'))
            else:
                sm = Builder.load_file('lcd_mini.kv')
                Logger.info('Screen Type: {}'.format('c2'))


            screen_manager.set_sm(sm)
            return sm

    RoboLcdApp().run()
