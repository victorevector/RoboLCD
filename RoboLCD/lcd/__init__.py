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
  from utilities import UtilitiesTab, UtilitiesContent, QRCodeScreen
  from printerstatus import PrinterStatusTab, PrinterStatusContent
  from wifi import WifiPasswordInput, WifiConfirmation, AP_Mode, APConfirmation, WifiUnencrypted, WifiConfiguration, WifiConnecting
  from backbuttonscreen import BackButtonScreen
  from noheaderscreen import NoHeaderScreen
  from manualcontrol import TemperatureControl, Temperature_Control
  from Motor_Control import Switchable_Motors
  from Preheat_Wizard import Preheat_Overseer
  from wizard import FilamentWizard
  from z_offset_wizard import ZoffsetWizard
  from scrollbox import Scroll_Box_Even, Scroll_Box_Icons, Robo_Icons
  from netconnectd import NetconnectdClient
  from RoboLCD import roboprinter
  from kivy.logger import Logger
  import thread
  from kivy.core.window import Window
  from kivy.clock import Clock
  from kivy.uix.popup import Popup
  from pconsole import pconsole
  from connection_popup import Updating_Popup, Error_Popup, Warning_Popup
  import subprocess
  from Print_Tuning import Tuning_Overseer
  from updater import UpdateScreen
  from EEPROM import EEPROM
  from session_saver import session_saver
  from RoboLCD.lcd.file_system.file_options import FileOptions
  from RoboLCD.lcd.file_system.files import FilesTab, FilesContent
  from fine_tune_zoffset import Fine_Tune_ZOffset

  from bed_calibration_wizard import Bed_Calibration
  from errors_and_warnings import Refresh_Screen
  import traceback
  from Select_Language import Change_Language
  from webcam import Camera
  from common_screens import Modal_Question_No_Title

  class RoboScreenManager(ScreenManager):
    """
    Root widget
    Encapsulates methods that are both neeeded globally and needed by descendant widgets to execute screen related functions. For example, self.generate_file_screen(**) is stored in this class but gets used by its descendant, the FileButton widget.
    """
    connection_popup = None
    wait_temp = None
    wifi_grid = []
    wifi_list = []     
    lang = roboprinter.lang   

    def __init__(self, **kwargs):
      super(RoboScreenManager, self).__init__(transition=NoTransition())
      #Load Language
      roboprinter.robosm = self
      roboprinter.robo_screen = self.get_current_screen
      roboprinter.back_screen = self._generate_backbutton_screen
      
      Logger.info("Language Loaded ###################################")
      passing = roboprinter.lang.pack['Load_Success']['pass']
      Logger.info("Loading Success? " + str(passing) + " ######################################")
      pconsole.initialize_eeprom()
      pconsole.query_eeprom()
      
      

      # dictionary of screens
      self.acceptable_screens = {
        #Utilities Screen
        'PRINT_TUNING': {'name':'print_tuning',
                 'title':roboprinter.lang.pack['Utilities']['Print_Tuning'],
                 'back_destination':'main', 
                 'function': self.generate_tuning_screen },

        'FAN_CONTROL': {'name':'print_tuning',
                'title':roboprinter.lang.pack['Utilities']['Fan_Control'],
                'back_destination':'main', 
                'function': self.generate_tuning_screen },

        'WIZARDS' : {'name':'wizards_screen', 
               'title':roboprinter.lang.pack['Utilities']['Wizards'], 
               'back_destination':'main', 
               'function': self.generate_wizards_screen},

        'NETWORK' : {'name':'network_utilities_screen', 
               'title':roboprinter.lang.pack['Utilities']['Network'], 
               'back_destination':'main', 
               'function': self.generate_network_utilities_screen},

        'UPDATES' : {'name':'UpdateScreen', 
               'title':roboprinter.lang.pack['Utilities']['Update'], 
               'back_destination':'main', 
               'function': self.generate_update_screen},

        'SYSTEM'   : {'name': 'system', 
               'title': roboprinter.lang.pack['Utilities']['System'], 
               'back_destination':'main', 
               'function': self.generate_system},

        'OPTIONS': {'name':'options', 
              'title': roboprinter.lang.pack['Utilities']['Options'], 
              'back_destination':'main', 
              'function': self.generate_options},

        #printer status screen
        'EXTRUDER_CONTROLS': {'name':'extruder_control_screen', 
                   'title':roboprinter.lang.pack['Utilities']['Temp_Control'], 
                   'back_destination':'main', 
                   'function':self.generate_toolhead_select_screen},

        'MOTOR_TEMP_CONTROLS': {'name':'motor_extruder_control_screen', 
                   'title':roboprinter.lang.pack['Utilities']['Temp_Control'], 
                   'back_destination':'motor_control_screen', 
                   'function':self.generate_toolhead_select_screen},

        'MOTOR_CONTROLS':{'name':'motor_control_screen',
                 'title':roboprinter.lang.pack['Utilities']['Motor_Control'],
                 'back_destination':'main', 
                 'function': self.generate_motor_controls},

        #Extruder controls sub screen
        'TEMPERATURE_CONTROLS': {'name':'temperature_button',
                     'title':roboprinter.lang.pack['Utilities']['Temp_Control'],
                     'back_destination':'extruder_control_screen', 
                     'function': self.generate_temperature_controls},

        'PREHEAT':{'name':'preheat_wizard',
              'title':roboprinter.lang.pack['Utilities']['Preheat'],
              'back_destination':'extruder_control_screen', 
              'function': self.generate_preheat_list},

        'COOLDOWN' : {'name':'cooldown_button',
               'title':roboprinter.lang.pack['Utilities']['Cooldown'],
               'back_destination':'extruder_control_screen', 
               'function':self.cooldown_button},

        #Wizards sub screen
        'ZOFFSET': {'name':'zoffset', 
              'title':roboprinter.lang.pack['Utilities']['ZOffset'], 
              'back_destination':'wizards_screen', 
              'function': self.generate_zaxis_wizard},

        'FIL_LOAD': {'name':'filamentwizard',
               'title':roboprinter.lang.pack['Utilities']['Filament'],
               'back_destination':'wizards_screen', 
               'function': self.generate_filament_wizard},

        'FIL_CHANGE': {'name':'filamentwizard',
                'title':roboprinter.lang.pack['Utilities']['Filament'],
                'back_destination':'wizards_screen', 
                'function': self.genetate_filament_change_wizard},

        'FINE_TUNE':{'name': 'fine_tune_wizard', 
               'title': roboprinter.lang.pack['Utilities']['FT_Wizard'], 
               'back_destination': 'wizards_screen', 
               'function': self.fine_tune_wizard},

        'BED_CALIBRATION':{'name': 'bed_calibration', 
                  'title': roboprinter.lang.pack['Utilities']['Bed_Cal'], 
                  'back_destination': 'wizards_screen', 
                  'function': self.bed_calibration},

        #Network sub screen
        'CONFIGURE_WIFI': {'name':'', 
                  'title':'', 
                  'back_destination':'network_utilities_screen', 
                  'function':self.generate_wificonfig},

        'START_HOTSPOT': {'name':'start_apmode_screen', 
                 'title': roboprinter.lang.pack['Utilities']['Start_Wifi'], 
                 'back_destination':'network_utilities_screen', 
                 'function':self.generate_start_apmode_screen},

        'NETWORK_STATUS': {'name':'ip_screen', 
                  'title':roboprinter.lang.pack['Utilities']['Network_Status'], 
                  'back_destination':'network_utilities_screen', 
                  'function':self.generate_ip_screen},

        'QR_CODE': {'name':'qrcode_screen', 
              'title':roboprinter.lang.pack['Utilities']['QR_Code'], 
              'back_destination':'network_utilities_screen', 
              'function':self.generate_qr_screen},

        #Options sub screen
        'EEPROM': {'name': 'eeprom_viewer', 
              'title': roboprinter.lang.pack['Utilities']['EEPROM'], 
              'back_destination': 'options', 
              'function': self.generate_eeprom},

        'UNMOUNT_USB': {'name': 'umount', 
                'title':'', 
                'back_destination': '', 
                'function':self.system_handler},

        'MOTORS_OFF':{'name': 'Motors_Off', 
               'title':'', 
               'back_destination':'options', 
               'function':self.motors_off},

        'LANGUAGE': {
               'name': 'language_select',
               'title': '',
               'back_destination': 'options',
               'function': self.generate_language
              },

        'MAINBOARD': {'name': 'mainboard_status', 
               'title': roboprinter.lang.pack['Utilities']['MainBoard'], 
               'back_destination': 'options', 
               'function': self.mainboard_status },
        'WEBCAM' : {'name': 'webcam_status', 
              'title': roboprinter.lang.pack['Utilities']['Webcam_Status'], 
              'back_destination': 'options', 
              'function': self.webcam_status},

        #System Sub Screen
        'SHUTDOWN': {'name': 'Shutdown', 
               'title':'', 
               'back_destination': '', 
               'function':self.system_handler},

        'REBOOT': {'name': 'Reboot', 
              'title':'', 
              'back_destination': '', 
              'function':self.system_handler},
        
        
        
        #extruder Control sub screens

        'TOOL1' :{'name': 'TOOL1', 
             'title': roboprinter.lang.pack['Utilities']['Tool1'], 
             'back_destination':'extruder_control_screen', 
             'function': self.generate_temperature_controls },

        'TOOL2' :{'name': 'TOOL2', 
             'title': roboprinter.lang.pack['Utilities']['Tool2'], 
             'back_destination':'extruder_control_screen', 
             'function': self.generate_temperature_controls },

        'BED' :{'name': 'BED', 
            'title': roboprinter.lang.pack['Utilities']['Bed'], 
            'back_destination':'extruder_control_screen', 
            'function': self.generate_temperature_controls },


      }

    def get_current_screen(self):
      return self.current

    def generate_language(self, **kwargs):
      Change_Language()

    
    def generate_update_screen(self, **kwargs):

      Logger.info('starting update screen')
      update_screen = UpdateScreen()
      Logger.info('ending update screen')
      self._generate_backbutton_screen(name=kwargs['name'], title=kwargs['title'], back_destination=kwargs['back_destination'], content=update_screen)

      return

    def generate_network_utilities_screen(self, **kwargs):
      #generates network option screen. Utilities > Network > Network Utilities > wifi list || start ap

      cw = Robo_Icons('Icons/Icon_Buttons/Configure Wifi.png', roboprinter.lang.pack['RoboIcons']['Configure_WiFi'], 'CONFIGURE_WIFI')
      ap = Robo_Icons('Icons/Icon_Buttons/Start Wifi.png', roboprinter.lang.pack['RoboIcons']['Start_WiFi'], 'START_HOTSPOT')
      ip = Robo_Icons('Icons/Icon_Buttons/Network status.png', roboprinter.lang.pack['RoboIcons']['Network_Status'], 'NETWORK_STATUS')
      qr = Robo_Icons('Icons/Icon_Buttons/QR Code.png', roboprinter.lang.pack['RoboIcons']['QR'], 'QR_CODE')

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
            mode = roboprinter.lang.pack['WiFi']['WiFi'] + '  \"{}\"'.format(ssid)
            mode += roboprinter.lang.pack['WiFi']['And_Wired']
          elif wifi:
            ssid = status['wifi']['current_ssid']
            ip = netcon.get_ip()
            mode = roboprinter.lang.pack['WiFi']['WiFi'] + '  \"{}\"'.format(ssid)
          elif ap and wired:
            mode = roboprinter.lang.pack['WiFi']['Hot_and_Wired']
            ip = roboprinter.lang.pack['WiFi']['Hot_IP'] + ' , ' + netcon.get_ip()
          elif ap:
            mode = roboprinter.lang.pack['WiFi']['Hot_ Mode']
            ip = roboprinter.lang.pack['WiFi']['Hot_IP']
          elif wired:
            mode = roboprinter.lang.pack['WiFi']['Wired']
            ip = netcon.get_ip()
          else:
            mode = roboprinter.lang.pack['WiFi']['No_Mode']
            ip = ''
          hostname = netcon.hostname()
        except Exception as e:
          mode = roboprinter.lang.pack['WiFi']['WiFi']
          ip = roboprinter.lang.pack['WiFi']['WiFi']
          hostname = roboprinter.lang.pack['WiFi']['WiFi']
          Logger.error('RoboScreenManager.generate_ip_screen: {}'.format(e))
        t = roboprinter.lang.pack['WiFi']['Connection_Status'] + ' \n    {}\n\n '.format(mode) + roboprinter.lang.pack['WiFi']['IP'] + ' \n    {}\n\n '.format(ip) + roboprinter.lang.pack['WiFi']['Hostname'] +' \n    {}'.format(hostname)
        c.text = t
        return
      t = roboprinter.lang.pack['WiFi']['Getting_Status']
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
     

    def go_back_to_main(self, tab=None, **kwargs):
      #Moves user to main screen and deletes all other screens
      #used by end of sequence confirmation buttons
      #optional tab parameter. If not None it will go back to that tab
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
       #Logger.info('go_back_to_screen: current {}, dest {}'.format(current, destination))
 
       if current == 'wifi_config[1]':
         Window.release_all_keyboards()
       #used to delete keyboards after user hits backbutton from Wifi Config Screen. This is a brute force implementation.... TODO figure out a more elegant and efficient way to perform this call.
       return
      except Exception as e:
       Logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! "+ str(e))
       traceback.print_exc()
       self.go_back_to_main('printer_status_tab')
             
      

    def generate_wizards_screen(self, **kwargs):
      name = kwargs['name']
      title = kwargs['title']
      back_destination = kwargs['back_destination']

      model = roboprinter.printer_instance._settings.get(['Model'])

      z = Robo_Icons('Icons/Zoffset illustration/Z-offset.png', roboprinter.lang.pack['RoboIcons']['Z_Offset'], 'ZOFFSET')
      fl = Robo_Icons('Icons/Icon_Buttons/Load Filament.png', roboprinter.lang.pack['RoboIcons']['Fil_Load'], 'FIL_LOAD')
      fc = Robo_Icons('Icons/Icon_Buttons/Change Filament.png', roboprinter.lang.pack['RoboIcons']['Fil_Change'], 'FIL_CHANGE')
      fine_tune = Robo_Icons('Icons/Zoffset illustration/Fine tune.png', roboprinter.lang.pack['RoboIcons']['FTZ_Offset'], 'FINE_TUNE')

      #If it's not an R2 we dont need the bed calibration wizard
      if model == "Robo R2":
        bed_calib = Robo_Icons('Icons/Bed_Calibration/Bed placement.png', roboprinter.lang.pack['RoboIcons']['Bed_Cal'], 'BED_CALIBRATION')
        buttons = [fc, fl, z, bed_calib, fine_tune]
      else:
        buttons = [fc, fl, z, fine_tune]


      c = Scroll_Box_Icons(buttons)

      self._generate_backbutton_screen(name=name, title=title, back_destination=back_destination, content=c)

    def generate_qr_screen(self, **kwargs):
      #generates the screen with a QR code image
      #
      c = QRCodeScreen()
      self._generate_backbutton_screen(name=kwargs['name'], title=kwargs['title'], back_destination=kwargs['back_destination'], content=c)
      return

    
      

    def generate_zaxis_wizard(self, **kwargs):
      ZoffsetWizard(robosm=self, back_destination=kwargs['back_destination'])

    def generate_motor_controls(self, **kwargs):
      name = kwargs['name']
      title = kwargs['title']
      back_destination = kwargs['back_destination']

      c = Switchable_Motors()

      self._generate_backbutton_screen(name=name,
                       title=title,
                       back_destination=back_destination, 
                       content=c,
                       cta=c.Switch_Layout,
                       icon='Icons/Manual_Control/switch 5.png'                                        
                      )

    def generate_temperature_controls(self, **kwargs):
      name = kwargs['name']
      title = kwargs['title']
      back_destination = kwargs['back_destination']

      selected_tool = name

      c = TemperatureControl(selected_tool = selected_tool)

      self._generate_backbutton_screen(name=name, title=title, back_destination=back_destination, content=c)

    def generate_toolhead_select_screen(self, **kwargs):
      _name = kwargs['name']

      self.tool_0 = False
      self.tool_1 = False
      self.bed_0 = False

      temps = roboprinter.printer_instance._printer.get_current_temperatures()
      Logger.info(temps)

      if 'tool0' in temps.keys():
        self.tool_0 = True
        t0 = Robo_Icons('Icons/System_Icons/Extruder1.png', roboprinter.lang.pack['RoboIcons']['Tool1'], 'TOOL1')

      if 'bed' in temps.keys():
        self.bed_0 = True
        bed = Robo_Icons('Icons/System_Icons/Bed temp.png', roboprinter.lang.pack['RoboIcons']['Bed'], 'BED')

      if 'tool1' in temps.keys():
        self.tool_1 = True
        t1 = Robo_Icons('Icons/System_Icons/Extruder2.png', roboprinter.lang.pack['RoboIcons']['Tool2'], 'TOOL2')

      preheat = Robo_Icons('Icons/Icon_Buttons/Preheat.png', roboprinter.lang.pack['RoboIcons']['Preheat'], 'PREHEAT')
      cooldown = Robo_Icons('Icons/Icon_Buttons/CoolDown.png', roboprinter.lang.pack['RoboIcons']['Cooldown'], 'COOLDOWN')

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

    def generate_preheat_list(self, **kwargs):
      
      c = Preheat_Overseer(**kwargs)

      

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

      opt = Robo_Icons('Icons/System_Icons/EEPROM Reader.png', roboprinter.lang.pack['RoboIcons']['EEPROM'] , 'EEPROM')
      usb = Robo_Icons('Icons/System_Icons/USB.png', roboprinter.lang.pack['RoboIcons']['USB'], 'UNMOUNT_USB')
      language = Robo_Icons('Icons/System_Icons/Language.png', roboprinter.lang.pack['RoboIcons']['Language'], 'LANGUAGE')
      main_status = Robo_Icons('Icons/Printer Status/Connection.png', roboprinter.lang.pack['RoboIcons']['Mainboard'], 'MAINBOARD')
      cam = Robo_Icons('Icons/System_Icons/Webcam.png', roboprinter.lang.pack['RoboIcons']['Webcam'], 'WEBCAM')

      model = roboprinter.printer_instance._settings.get(['Model'])
      if model == "Robo R2":
       #buttons = [opt,usb, firm, language, main_status, cam]
       buttons = [opt,usb, main_status, cam]
      else:
       #buttons = [opt,usb, firm, language, main_status]
       buttons = [opt,usb, main_status]

      layout = Scroll_Box_Icons(buttons)

      self._generate_backbutton_screen(name = _name, title = kwargs['title'], back_destination=kwargs['back_destination'], content=layout)

    def webcam_status(self, **kwargs):
     layout = Camera()

     self._generate_backbutton_screen(name = kwargs['name'], title = kwargs['title'], back_destination=kwargs['back_destination'], content=layout)



    def generate_system(self, **kwargs):
      _name = kwargs['name']

      power = Robo_Icons('Icons/System_Icons/Shutdown.png', roboprinter.lang.pack['RoboIcons']['Shutdown'], 'SHUTDOWN')
      reboot = Robo_Icons('Icons/System_Icons/Reboot.png', roboprinter.lang.pack['RoboIcons']['Reboot'], 'REBOOT')
      
      

      buttons = [power, reboot]

      layout = Scroll_Box_Icons(buttons)

      self._generate_backbutton_screen(name = _name, title = kwargs['title'], back_destination=kwargs['back_destination'], content=layout)

    #this is a function for simple system commands
    def system_handler(self, **kwargs):
      option = kwargs['name']

      acceptable_options = {
        'Shutdown': {'command': 'sudo shutdown -h now', 'popup': "WARNING",
               'error': roboprinter.lang.pack['System']['Shutdown_Title'] ,
               'body_text': roboprinter.lang.pack['System']['Shutdown_Body'] ,
               'delay': 5,
               'confirmation': True,
               'Title': roboprinter.lang.pack['System']['Shutdown_Confirmation']['Title'],
               'Body_Text': roboprinter.lang.pack['System']['Shutdown_Confirmation']['Body_Text']
               },

        'Reboot' : {'command': 'sudo reboot', 'popup': "WARNING",
              'error': roboprinter.lang.pack['System']['Reboot_Title'],
              'body_text': roboprinter.lang.pack['System']['Reboot_Body'] ,
              'delay': 5,
              'confirmation': True,
              'Title': roboprinter.lang.pack['System']['Reboot_Confirmation']['Title'],
              'Body_Text': roboprinter.lang.pack['System']['Reboot_Confirmation']['Body_Text']
              },

        'umount': {'command':'sudo umount /dev/sda1' if not 'usb_location' in session_saver.saved else 'sudo umount ' + session_saver.saved['usb_location'] , 'popup': "ERROR",
              'error': roboprinter.lang.pack['System']['USB_Title'] ,
              'body_text': roboprinter.lang.pack['System']['USB_Body'] ,
              'delay': 0.1,
              'confirmation': False
              },
      }

      if option in acceptable_options:
        def show_error():
          popup = acceptable_options[option]['popup']
          if popup == "WARNING":
            Logger.info("Showing Warning")
            wp = Warning_Popup(acceptable_options[option]['error'], acceptable_options[option]['body_text'])
            wp.show()
  
          elif popup == "ERROR":
            Logger.info("Showing Error")
            ep = Error_Popup(acceptable_options[option]['error'], acceptable_options[option]['body_text'],callback=partial(roboprinter.robosm.go_back_to_main, tab='printer_status_tab'))
            ep.show()
  
          Logger.info("Executing: " + acceptable_options[option]['command'])
          self.shell_command = acceptable_options[option]['command']
          Clock.schedule_once(self.execute_function, acceptable_options[option]['delay'])
        def go_back(back):
          self.current = back
  

        if acceptable_options[option]['confirmation']:

          #make a confirmation screen
          back_screen = self.current
          back_function = partial(go_back, back=back_screen)
          content = Modal_Question_No_Title(acceptable_options[option]['Body_Text'], 
                                            roboprinter.lang.pack['System']['positive'], 
                                            roboprinter.lang.pack['System']['negative'], 
                                            show_error, 
                                            back_function)

          #make screen
          roboprinter.robosm._generate_backbutton_screen(name='view_preheat', 
                                                       title = acceptable_options[option]['Title'] , 
                                                       back_destination=back_screen, 
                                                       content=content
                                                       )
        else:
          show_error()





      else:
        Logger.info('Not an acceptable system option' + str(option))

    def execute_function(self, dt):
      subprocess.call(self.shell_command, shell=True)
      #update files
      if 'file_callback' in session_saver.saved:
        session_saver.saved['file_callback']()

    def motors_off(self, **kwargs):
    
      
      roboprinter.printer_instance._printer.commands('M18')
      ep = Error_Popup(roboprinter.lang.pack['Popup']['Motors_Title'], roboprinter.lang.pack['Popup']['Motors_Body'],callback=partial(roboprinter.robosm.go_back_to_main, tab='printer_status_tab'))
      ep.show()

    def mainboard_status(self, **kwargs):
      back_screen = self.current
      def refresh_screen():
        title = roboprinter.lang.pack['Mainboard']['Connection_Title']
        body_text = roboprinter.lang.pack['Mainboard']['Connection_Body']
        button_text = roboprinter.lang.pack['Mainboard']['Connection_Button']
        layout = Refresh_Screen(title, body_text, button_text, start_refresh=True)
        self._generate_backbutton_screen(name = kwargs['name'], title = kwargs['title'], back_destination=kwargs['back_destination'], content=layout)

      def go_back():
        self.current = back_screen

      #make confirmation screen
      content = Modal_Question_No_Title(roboprinter.lang.pack['Error_Detection']['MAINBOARD']['Reset_Confirmation']['Body'], 
                                        roboprinter.lang.pack['Error_Detection']['MAINBOARD']['Reset_Confirmation']['positive'], 
                                        roboprinter.lang.pack['Error_Detection']['MAINBOARD']['Reset_Confirmation']['negative'], 
                                        refresh_screen, 
                                        go_back)

      #make screen
      roboprinter.robosm._generate_backbutton_screen(name='refresh_confirmation', 
                                                   title = roboprinter.lang.pack['Error_Detection']['MAINBOARD']['Reset_Confirmation']['Title'] , 
                                                   back_destination=back_screen, 
                                                   content=content
                                                   )

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
      import os
      if os.path.exists("/dev/fb1"):
        Logger.info("Frame Buffer C2")
        Config.set('input', '%(name)s', 'probesysfs,provider=hidinput,param=rotation=270,param=invert_y=1')
      else: 
        Logger.info("HDMI C2")
        Config.set('input', '%(name)s', 'probesysfs,provider=hidinput,param=rotation=180,param=invert_y=1,param=invert_x=1')
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

  RoboLCD = RoboLcdApp()
  RoboLCD.run()
  

  
