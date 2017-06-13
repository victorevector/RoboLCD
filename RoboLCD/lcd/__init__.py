def start():
    import os
    os.environ["KIVY_NO_ARGS"] = "1"
    os.environ["KIVY_NO_CONSOLELOG"] = "1"

    import sys
    sys.dont_write_bytecode = True
    import logging
    import re
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
    Config.set('graphics', 'borderless', 1)
    # Config.set('input', '%(name)s', 'probesysfs,provider=hidinput,param=invert_x=1') #This now gets set in the builder

    from kivy.app import App
    from kivy.lang import Builder
    from kivy.resources import resource_add_path
    from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.button import Button
    from kivy.uix.togglebutton import ToggleButton
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label
    from functools import partial
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
    from scrollbox import ScrollBox, Scroll_Box_Even, Scroll_Box_Icons, Robo_Icons, Robo_Icons_Anchor, Scroll_Box_Icons_Anchor
    from netconnectd import NetconnectdClient
    from .. import roboprinter
    from kivy.logger import Logger
    import thread
    from kivy.core.window import Window
    from kivy.clock import Clock
    from kivy.uix.popup import Popup
    from pconsole import pconsole
    from robo_sm import screen_manager
    from connection_popup import Connection_Popup, Updating_Popup, Error_Popup, Warning_Popup
    import subprocess
    from Print_Tuning import Tuning_Overseer
    from Versioning import Versioning

    from updater import UpdateScreen

    from EEPROM import EEPROM
    from Modal_Popup import Modal_Popup
    from Firmware_Wizard import Firmware_Wizard
    from slicer_wizard import Slicer_Wizard
    from session_saver import session_saver
    from file_explorer import FileOptions
    from fine_tune_zoffset import Fine_Tune_ZOffset

    from bed_calibration_wizard import Bed_Calibration
    from errors_and_warnings import Refresh_Screen
    from webcam import Camera


    Logger.info('Start')
    class RoboScreenManager(ScreenManager):
        """
        Root widget
        Encapsulates methods that are both neeeded globally and needed by descendant widgets to execute screen related functions. For example, self.generate_file_screen(**) is stored in this class but gets used by its descendant, the FileButton widget.
        """
        connection_popup = None
        wait_temp = None
        wifi_grid = []
        wifi_list = []

        def __init__(self, **kwargs):
            super(RoboScreenManager, self).__init__(transition=NoTransition())
            pconsole.initialize_eeprom()
            pconsole.query_eeprom()
            roboprinter.robo_screen = self.get_current_screen

            roboprinter.back_screen = self._generate_backbutton_screen
            roboprinter.robosm = self

            # dictionary of screens
            self.acceptable_screens = {
                #Utilities Screen
                'PRINT_TUNING': {'name':'print_tuning','title':'Print Tuning','back_destination':'main', 'function': self.generate_tuning_screen },
                'FAN_CONTROL': {'name':'print_tuning','title':'Fan Control','back_destination':'main', 'function': self.generate_tuning_screen },
                'ROBO_CONTROLS': {'name':'robo_controls','title':'Robo Controls','back_destination':'main', 'function': self.generate_robo_controls },
                'WIZARDS' : {'name':'wizards_screen', 'title':'Wizards', 'back_destination':'main', 'function': self.generate_wizards_screen},
                'NETWORK' : {'name':'network_utilities_screen', 'title':'Network Utilities', 'back_destination':'main', 'function': self.generate_network_utilities_screen},

                'UPDATES' : {'name':'UpdateScreen', 'title':'Update', 'back_destination':'main', 'function': self.generate_update_screen},
                'SYSTEM'   : {'name': 'system', 'title': 'System', 'back_destination':'main', 'function': self.generate_system},
                'OPTIONS': {'name':'options', 'title': 'Options', 'back_destination':'main', 'function': self.generate_options},

                #Robo Controls sub screen
                'EXTRUDER_CONTROLS': {'name':'extruder_control_screen', 'title':'Temperature Control', 'back_destination':'main', 'function':self.generate_toolhead_select_screen},
                'MOTOR_CONTROLS':{'name':'motor_control_screen','title':'Motor Control','back_destination':'main', 'function': self.generate_motor_controls},

                #Extruder controls sub screen
                'TEMPERATURE_CONTROLS': {'name':'temperature_button','title':'Temperature Control','back_destination':'extruder_control_screen', 'function': self.generate_temperature_controls},
                'PREHEAT':{'name':'preheat_wizard','title':'Preheat','back_destination':'extruder_control_screen', 'function': self.generate_preheat_list},
                'COOLDOWN' : {'name':'cooldown_button','title':'Cooldown','back_destination':'extruder_control_screen', 'function':self.cooldown_button},

                #Wizards sub screen
                'ZOFFSET': {'name':'zoffset', 'title':'Z Offset Wizard', 'back_destination':'wizards_screen', 'function': self.generate_zaxis_wizard},
                'FIL_LOAD': {'name':'filamentwizard','title':"Filament",'back_destination':'wizards_screen', 'function': self.generate_filament_wizard},
                'FIL_CHANGE': {'name':'filamentwizard','title':"Filament",'back_destination':'wizards_screen', 'function': self.genetate_filament_change_wizard},
                'SLICER' : {'name': 'slicing_wizard', 'title': 'Slicer', 'back_destination': 'wizards_screen', 'function': self.slicer_wizard},
                'FINE_TUNE':{'name': 'fine_tune_wizard', 'title': 'Fine Tune Wizard', 'back_destination': 'wizards_screen', 'function': self.fine_tune_wizard},
                'BED_CALIBRATION':{'name': 'bed_calibration', 'title': 'Bed Calibration', 'back_destination': 'wizards_screen', 'function': self.bed_calibration},

                #Network sub screen
                'CONFIGURE_WIFI': {'name':'', 'title':'', 'back_destination':'network_utilities_screen', 'function':self.generate_wificonfig},
                'START_HOTSPOT': {'name':'start_apmode_screen', 'title':'Start Wifi Hotspot', 'back_destination':'network_utilities_screen', 'function':self.generate_start_apmode_screen},
                'NETWORK_STATUS': {'name':'ip_screen', 'title':'Network Status', 'back_destination':'network_utilities_screen', 'function':self.generate_ip_screen},
                'QR_CODE': {'name':'qrcode_screen', 'title':'QR Code', 'back_destination':'network_utilities_screen', 'function':self.generate_qr_screen},

                #Options sub screen
                'EEPROM': {'name': 'eeprom_viewer', 'title': 'EEPROM', 'back_destination': 'options', 'function': self.generate_eeprom},
                'UNMOUNT_USB': {'name': 'umount', 'title':'', 'back_destination': '', 'function':self.system_handler},
                'FIRMWARE' : {'name': 'firmware_updater','title':'Firmware', 'back_destination': 'main', 'function': self.update_firmware},
                'MOTORS_OFF':{'name': 'Motors_Off', 'title':'', 'back_destination':'options', 'function':self.motors_off},
                'MAINBOARD': {'name': 'mainboard_status', 'title': 'Connection Status', 'back_destination': 'options', 'function': self.mainboard_status },
                'WEBCAM' : {'name': 'webcam_status', 'title': "Webcam Status", 'back_destination': 'options', 'function': self.webcam_status},

                #System Sub Screen
                'SHUTDOWN': {'name': 'Shutdown', 'title':'', 'back_destination': '', 'function':self.system_handler},
                'REBOOT': {'name': 'Reboot', 'title':'', 'back_destination': '', 'function':self.system_handler},
                
                
                
                #extruder Control sub screens

                'TOOL1' :{'name': 'TOOL1', 'title': 'Extruder 1', 'back_destination':'extruder_control_screen', 'function': self.generate_temperature_controls },
                'TOOL2' :{'name': 'TOOL2', 'title': 'Extruder 2', 'back_destination':'extruder_control_screen', 'function': self.generate_temperature_controls },
                'BED' :{'name': 'BED', 'title': 'Bed', 'back_destination':'extruder_control_screen', 'function': self.generate_temperature_controls },


            }

        def get_current_screen(self):
            return self.current

        
        def generate_update_screen(self, **kwargs):

            Logger.info('starting update screen')
            update_screen = UpdateScreen()
            Logger.info('ending update screen')
            self._generate_backbutton_screen(name=kwargs['name'], title=kwargs['title'], back_destination=kwargs['back_destination'], content=update_screen)

            return

        def generate_file_screen(self, **kwargs):
            # Accesible to FilesButton
            # Instantiates BackButtonScreen and passes values for dynamic properties:
            # backbutton label text, print information, and print button.
            file_name = kwargs['filename']
            file_path = kwargs['file_path']
            is_usb = kwargs['is_usb']
            title = file_name.replace('.gcode', '').replace('.gco', '')

            Logger.info('Function Call: generate_new_screen {}'.format(file_name))

            def delete_file(*args): #gets binded to CTA in header
                roboprinter.printer_instance._file_manager.remove_file('local', file_path)
                self.go_back_to_main('files_tab')

            if is_usb:
                c = PrintUSB(name='print_file',
                                   file_name=file_name,
                                   file_path=file_path)
            else:
                c = PrintFile(name='print_file',
                              file_name=file_name,
                              file_path=file_path)
            def file_options():
                FileOptions(file_name, file_path)

            if not is_usb:
                self._generate_backbutton_screen(name=c.name, title=title, back_destination=self.current, content=c, cta=file_options, icon='Icons/settings.png')
            else:
                self._generate_backbutton_screen(name=c.name, title=title, back_destination=self.current, content=c, cta=file_options, icon='Icons/settings.png')

            return

        def generate_network_utilities_screen(self, **kwargs):
            #generates network option screen. Utilities > Network > Network Utilities > wifi list || start ap

            cw = Robo_Icons('Icons/Icon_Buttons/Configure Wifi.png', 'Configure Wifi', 'CONFIGURE_WIFI')
            ap = Robo_Icons('Icons/Icon_Buttons/Start Wifi.png', 'Start Wifi Hotspot', 'START_HOTSPOT')
            ip = Robo_Icons('Icons/Icon_Buttons/Network status.png', 'Network Status', 'NETWORK_STATUS')
            qr = Robo_Icons('Icons/Icon_Buttons/QR Code.png', 'API QR Code', 'QR_CODE')

            buttons = [cw,ap,ip,qr]

            sb = Scroll_Box_Icons(buttons)

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
            for s in self.screen_names:
                if s is name:
                    d= self.get_screen(s)
                    self.remove_widget(d)
                    Logger.info("Removed: " + s)

            s = BackButtonScreen(name=name, title=title, back_destination=back_destination, content=content, **kwargs)
            s.populate_layout()
            self.add_widget(s)
            self.current = s.name

            return s

        def generate_wizards_screen(self, **kwargs):
            name = kwargs['name']
            title = kwargs['title']
            back_destination = kwargs['back_destination']

            model = roboprinter.printer_instance._settings.get(['Model'])

            z = Robo_Icons('Icons/Zoffset illustration/Z-offset.png', 'Z Offset Wizard', 'ZOFFSET')
            fl = Robo_Icons('Icons/Icon_Buttons/Load Filament.png', 'Filament Loading', 'FIL_LOAD')
            fc = Robo_Icons('Icons/Icon_Buttons/Change Filament.png', 'Filament Change', 'FIL_CHANGE')

            slicer = Robo_Icons('Icons/Slicer wizard icons/slicer-wizard.png', 'Slicing Wizard', 'SLICER')
            fine_tune = Robo_Icons('Icons/Zoffset illustration/Fine tune.png', 'Fine Tune Offset', 'FINE_TUNE')

            #If it's not an R2 we dont need the bed calibration wizard
            if model == "Robo R2":
                bed_calib = Robo_Icons('Icons/Bed_Calibration/Bed placement.png', 'Bed Calibration', 'BED_CALIBRATION')
                buttons = [fc, fl, z, slicer, bed_calib, fine_tune]
            else:
                buttons = [fc, fl, z, slicer, fine_tune]


            c = Scroll_Box_Icons(buttons)

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
            #ps = self.get_screen(current)
            try:
                for s in self.screen_names:
                    if s is current:
                        d= self.get_screen(s)
                        self.remove_widget(d)
                self.current = destination
                #self.remove_widget(ps)
                Logger.info('go_back_to_screen: current {}, dest {}'.format(current, destination))
    
                if current == 'wifi_config[1]':
                    Window.release_all_keyboards()
                #used to delete keyboards after user hits backbutton from Wifi Config Screen. This is a brute force implementation.... TODO figure out a more elegant and efficient way to perform this call.
                return
            except Exception as e:
                self.go_back_to_main()
                return
                
            

        def generate_zaxis_wizard(self, **kwargs):
            """
            """
            temp_pop = Error_Popup("Bed Not Connected", "Please Reconnect the bed and try again")
            ZoffsetWizard(robosm=self, back_destination=kwargs['back_destination'], temp_pop = temp_pop)

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

            self._generate_backbutton_screen(name=name,
                                             title=title,
                                             back_destination=back_destination,
                                             content=c, cta=c.raise_buildplate,
                                             icon='Icons/Manual_Control/Z+_icon.png' )

        def generate_temperature_controls(self, **kwargs):
            name = kwargs['name']
            title = kwargs['title']
            back_destination = kwargs['back_destination']

            selected_tool = name

            c = TemperatureControl(selected_tool = selected_tool)

            self._generate_backbutton_screen(name=name, title=title, back_destination=back_destination, content=c)

        def generate_robo_controls(self, **kwargs):
            _name = kwargs['name']

            #new Icon Way
            extruder = Robo_Icons('Icons/Icon_Buttons/Temperature.png', 'Temperature\nControls', 'EXTRUDER_CONTROLS')
            manual = Robo_Icons('Icons/Icon_Buttons/Motor_Controls.png', 'Motor\nControls', 'MOTOR_CONTROLS')

            buttons = [extruder, manual]

            layout = Scroll_Box_Icons(buttons)

            self._generate_backbutton_screen(name = _name, title = kwargs['title'], back_destination=kwargs['back_destination'], content=layout)
            return

        def generate_toolhead_select_screen(self, **kwargs):
            _name = kwargs['name']

            self.tool_0 = False
            self.tool_1 = False
            self.bed_0 = False

            temps = roboprinter.printer_instance._printer.get_current_temperatures()
            Logger.info(temps)

            if 'tool0' in temps.keys():
                self.tool_0 = True
                t0 = Robo_Icons('Icons/System_Icons/Extruder1.png', 'Extruder 1', 'TOOL1')

            if 'bed' in temps.keys():
                self.bed_0 = True
                bed = Robo_Icons('Icons/System_Icons/Bed temp.png', 'Bed', 'BED')

            if 'tool1' in temps.keys():
                self.tool_1 = True
                t1 = Robo_Icons('Icons/System_Icons/Extruder2.png', 'Extruder 2', 'TOOL2')

            preheat = Robo_Icons('Icons/Icon_Buttons/Preheat.png', 'Preheat', 'PREHEAT')
            cooldown = Robo_Icons('Icons/Icon_Buttons/CoolDown.png', 'Cooldown', 'COOLDOWN')

            buttons = []
            if self.tool_0 :
                buttons.append(t0)
            if self.tool_1:
                buttons.append(t1)
            if self.bed_0:
                buttons.append(bed)

            buttons.append(preheat)
            buttons.append(cooldown)

            layout = Scroll_Box_Icons(buttons)

            self._generate_backbutton_screen(name = _name, title = kwargs['title'], back_destination=kwargs['back_destination'], content=layout)
            return

        def generate_extrudercontrol_screen(self, **kwargs):
            _name = kwargs['name']

            self.selected_tool = _name




            t = Robo_Icons('Icons/Icon_Buttons/Temperature.png', 'Temperature Controls', 'TEMPERATURE_CONTROLS')
            preheat = Robo_Icons('Icons/Icon_Buttons/Preheat.png', 'Preheat', 'PREHEAT')
            cooldown = Robo_Icons('Icons/Icon_Buttons/CoolDown.png', 'Cooldown', 'COOLDOWN')

            buttons = [preheat, t, cooldown]

            layout = Scroll_Box_Icons(buttons)

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

            setup = {"tool0": self.tool_0,
                     "tool1": self.tool_1,
                     "bed": self.bed_0}

            pla = PLA_Button(setup, name=_name)
            ab = ABS_Button(setup, name=_name)
            placeholder = Empty_Button()
            layout = BoxLayout(orientation="vertical")
            layout.add_widget(pla)
            layout.add_widget(ab)
            layout.add_widget(placeholder)

            self._generate_backbutton_screen(name = _name, title = kwargs['title'], back_destination=kwargs['back_destination'], content=layout)
            return

        def cooldown_button(self, **kwargs):
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

        def coming_soon(self, **kwargs):
            _name = kwargs['name']
            layout = GridLayout(cols = 3, rows = 3, orientation = 'vertical')
            layout.add_widget(Label(size_hint_x = None))
            layout.add_widget(Label(size_hint_x = None))
            layout.add_widget(Label(size_hint_x = None))
            layout.add_widget(Label(size_hint_x = None))
            cb = Label(text = 'Coming Soon', font_size = 30,halign = 'center', valign = 'middle', width = 300, height = 100)
            layout.add_widget(cb)
            layout.add_widget(Label(size_hint_x = None))
            layout.add_widget(Label(size_hint_x = None))
            layout.add_widget(Label(size_hint_x = None))
            layout.add_widget(Label(size_hint_x = None))
            self._generate_backbutton_screen(name=_name, title=kwargs['title'], back_destination=kwargs['back_destination'], content=layout)

            return


        def generate_filament_wizard(self, **kwargs):
            # Instantiates the FilamentWizard and gives it a screen. Passes management of filament wizard related screens to FilamentWizard instance.
            FilamentWizard('LOAD',self, name=kwargs['name'],title=kwargs['title'], back_destination=kwargs['back_destination']) #pass self so that FilamentWizard can render itself
            return

        def genetate_filament_change_wizard(self, **kwargs):
            FilamentWizard('CHANGE',self, name=kwargs['name'],title=kwargs['title'], back_destination=kwargs['back_destination']) #pass self so that FilamentWizard can render itself
            return
        def generate_tuning_screen(self, **kwargs):
            _name = kwargs['name']

            layout = Tuning_Overseer().tuning_object()

            self._generate_backbutton_screen(name=_name, title=kwargs['title'], back_destination=kwargs['back_destination'], content=layout)

        def generate_versioning(self, **kwargs):
            _name = kwargs['name']
            layout = Versioning()
            self._generate_backbutton_screen(name=_name, title=kwargs['title'], back_destination=kwargs['back_destination'], content=layout)

        def generate_eeprom(self, **kwargs):
            _name = kwargs['name']
            eeprom = EEPROM(self)
            layout = Scroll_Box_Even(eeprom.buttons)

            self._generate_backbutton_screen(name=_name, title=kwargs['title'], back_destination=kwargs['back_destination'], content=layout)

        def generate_options(self, **kwargs):
            _name = kwargs['name']

            opt = Robo_Icons('Icons/System_Icons/EEPROM Reader.png', 'EEPROM', 'EEPROM')
            usb = Robo_Icons('Icons/System_Icons/USB.png', 'Unmount USB', 'UNMOUNT_USB')
            firm = Robo_Icons('Icons/System_Icons/Firmware update wizard.png', 'Firmware Update', 'FIRMWARE')
            motors = Robo_Icons('Icons/Tuning/New Tuning/motors off.png', 'Motors Off', 'MOTORS_OFF')
            main_status = Robo_Icons('Icons/Printer Status/Connection.png', 'Connection', 'MAINBOARD')
            cam = Robo_Icons('Icons/System_Icons/Webcam.png', 'Webcam', 'WEBCAM')

            model = roboprinter.printer_instance._settings.get(['Model'])
            if model == "Robo R2":
              buttons = [opt,usb, firm, motors, main_status, cam]
            else:
              buttons = [opt,usb, firm, motors, main_status]
            layout = Scroll_Box_Icons(buttons)

            self._generate_backbutton_screen(name = _name, title = kwargs['title'], back_destination=kwargs['back_destination'], content=layout)

        def webcam_status(self, **kwargs):
          layout = Camera()

          self._generate_backbutton_screen(name = kwargs['name'], title = kwargs['title'], back_destination=kwargs['back_destination'], content=layout)



        def generate_system(self, **kwargs):
            _name = kwargs['name']

            power = Robo_Icons('Icons/System_Icons/Shutdown.png', 'Shutdown', 'SHUTDOWN')
            reboot = Robo_Icons('Icons/System_Icons/Reboot.png', 'Reboot', 'REBOOT')
            
            

            buttons = [power, reboot]

            layout = Scroll_Box_Icons(buttons)

            self._generate_backbutton_screen(name = _name, title = kwargs['title'], back_destination=kwargs['back_destination'], content=layout)

        #this is a function for simple system commands
        def system_handler(self, **kwargs):
            option = kwargs['name']

            acceptable_options = {
                'Shutdown': {'command': 'sudo shutdown -h now', 'popup': "WARNING",
                             'error': "Shuting Down",
                             'body_text':"After the screen turns white\nyou may turn off the printer",
                             'delay': 5
                             },

                'Reboot' : {'command': 'sudo reboot', 'popup': "WARNING",
                            'error': "Rebooting",
                            'body_text':"Currently Rebooting\nPlease wait",
                            'delay': 5
                            },

                'umount': {'command':'sudo umount /dev/sda1' if not 'usb_location' in session_saver.saved else 'sudo umount ' + session_saver.saved['usb_location'] , 'popup': "ERROR",
                           'error': 'USB UnMounted',
                           'body_text':'Please Remove USB Stick',
                           'delay': 0.1
                           },
            }

            if option in acceptable_options:
                popup = acceptable_options[option]['popup']
                if popup == "WARNING":
                    Logger.info("Showing Warning")
                    wp = Warning_Popup(acceptable_options[option]['error'], acceptable_options[option]['body_text'])
                    wp.show()

                elif popup == "ERROR":
                    Logger.info("Showing Error")
                    ep = Error_Popup(acceptable_options[option]['error'], acceptable_options[option]['body_text'])
                    ep.show()

                Logger.info("Executing: " + acceptable_options[option]['command'])
                self.shell_command = acceptable_options[option]['command']
                Clock.schedule_once(self.execute_function, acceptable_options[option]['delay'])



            else:
                Logger.info('Not an acceptable system option' + str(option))

        def execute_function(self, dt):
            subprocess.call(self.shell_command, shell=True)
            #update files
            if 'file_callback' in session_saver.saved:
                session_saver.saved['file_callback']()

        def motors_off(self, **kwargs):
            
            roboprinter.printer_instance._printer.commands('M18')
            ep = Error_Popup('Motors Disengaged', 'To re-engage motors, home the printer')
            ep.show()

        def mainboard_status(self, **kwargs):
            title = 'Reset Connection'
            body_text = 'Reset the connection to the printer controls'
            button_text = 'Reset'
            layout = Refresh_Screen(title, body_text, button_text)
            self._generate_backbutton_screen(name = kwargs['name'], title = kwargs['title'], back_destination=kwargs['back_destination'], content=layout)

           


        def update_firmware(self, **kwargs):
            Firmware_Wizard(self, kwargs['back_destination'])

        def slicer_wizard(self, **kwargs):
            Slicer_Wizard(self, kwargs['back_destination'])

        def fine_tune_wizard(self, **kwargs):
            Fine_Tune_ZOffset()


        def bed_calibration(self, **kwargs):
            Bed_Calibration()




        def generate_screens(self, screen):

            if screen in self.acceptable_screens:
                Logger.info("Changing screen to " + screen)
                self.acceptable_screens[screen]['function'](name=self.acceptable_screens[screen]['name'],
                                                     title = self.acceptable_screens[screen]['title'],
                                                     back_destination = self.acceptable_screens[screen]['back_destination'])
            else:
                Logger.info(screen + " Is Not an acceptable screen")
                return False


    class RoboLcdApp(App):

        def build(self):
            # Root widget is RoboScreenManager
            dir_path = os.path.dirname(os.path.realpath(__file__))
            resource_add_path(dir_path) #kivy will look for images and .kv files in this directory path/to/RoboLCD/lcd/
            printer_info = roboprinter.printer_instance._printer.get_current_connection()
            sm = None
            # Determine what kivy rules to implement based on screen size desired. Will use printerprofile to determine screen size

            model = roboprinter.printer_instance._settings.get(['Model'])

            if model == None:
                #detirmine model
                printer_type = roboprinter.printer_instance._settings.global_get(['printerProfiles', 'defaultProfile'])

                if 'model' in printer_type:
                    if printer_type['model'] != 'Robo C2' and printer_type['model'] != 'Robo R2':
                        model = 'Robo C2'
                    else:
                        model = printer_type['model']
                    
                else:
                    model = "Robo C2"

                roboprinter.printer_instance._settings.set(['Model'], model)
                roboprinter.printer_instance._settings.save()


                if model == "Robo R2":
                    sm = self.load_R2()

                elif model == "Robo C2":
                    sm = self.load_C2()

            elif model == "Robo R2":
                sm = self.load_R2()

            elif model == "Robo C2":
                sm = self.load_C2()

            screen_manager.set_sm(sm)
            return sm

        def concat_2_files(self, file1, file2):
            temp_path = '/tmp/kv/combined.kv'

            dir_path = os.path.dirname(os.path.realpath(__file__))
            file_list = [dir_path + '/'+ file1, dir_path + '/'+ file2]
            #make a temporary file

            if not os.path.isdir('/tmp/kv'):
                os.makedirs('/tmp/kv')


            with open(temp_path, 'w') as combined:
                for path in file_list:
                    with open(path, 'r') as file:
                        for line in file:
                            combined.write(line)

            return temp_path

        def load_C2(self):
            #load C2
            Config.set('input', '%(name)s', 'probesysfs,provider=hidinput,param=rotation=270,param=invert_y=1')
            path = self.concat_2_files('C2.kv', 'lcd_mini.kv')
            sm = Builder.load_file(path)
            Logger.info('Screen Type: {}'.format('c2'))

            return sm

        def load_R2(self):
            #load R2
            Config.set('input', '%(name)s', 'probesysfs,provider=hidinput,param=invert_x=1')
            path = self.concat_2_files('R2.kv', 'lcd_mini.kv')
            sm = Builder.load_file(path)
            Logger.info('Screen Type: {}'.format('R2'))
            return sm


    RoboLcdApp().run()
