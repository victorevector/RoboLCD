# import threading
# from kivy.app import App
# from kivy.lang import Builder
# from kivy.resources import resource_add_path
# from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.floatlayout import FloatLayout
# from kivy.uix.button import Button
# from kivy.uix.togglebutton import ToggleButton
# from kivy.uix.gridlayout import GridLayout
# from kivy.uix.label import Label
# from kaapopup import KaaPopup, UpdateScreen
# from mainscreen import MainScreen, MainScreenTabbedPanel
# from files import FilesTab, FilesContent, PrintFile, PrintUSB
# from utilities import UtilitiesTab, UtilitiesContent, QRCodeScreen
# from printerstatus import PrinterStatusTab, PrinterStatusContent
# from wifi import WifiButton, WifiPasswordInput, WifiConfirmation, WifiConfigureButton, APButton, StartAPButton, APConfirmation, IPAddressButton, SuccessButton, WifiUnencrypted
# from wizard import WizardButton, PreheatWizard
# from netconnectd import NetconnectdClient
# from .. import roboprinter
# from backbuttonscreen import BackButtonScreen
# from noheaderscreen import NoHeaderScreen
# from kivy.config import Config
# from kivy.logger import Logger
# import thread
# from kivy.core.window import Window
# from scrollbox import ScrollBox
# from manualcontrol import ManualControl, TemperatureControl
# from kivy.clock import Clock
# from kivy.uix.popup import Popup
# from pconsole import pconsole
#
#
# #screen manager class
# class RoboScreenManager(ScreenManager):
#         """
#         Root widget
#         Encapsulates methods that are both neeeded globally and needed by descendant widgets to execute screen related functions. For example, self.generate_file_screen(**) is stored in this class but gets used by its descendant, the FileButton widget.
#         """
#         connection_popup = None
#
#         def __init__(self, **kwargs):
#             super(RoboScreenManager, self).__init__(transition=NoTransition())
#             kaa_thread = threading.Thread(target=self.receive_message)
#             kaa_thread.start()
#             Logger.info("Starting kaa_thread...")
#             Clock.schedule_interval(self.check_connection_status, .5)
#             pconsole.initialize_eeprom()
#             pconsole.generate_eeprom()
#
#
#         def check_connection_status(self, dt):
#             """Is aware of printer-sbc connection """
#             is_closed_or_error = roboprinter.printer_instance._printer.is_closed_or_error()
#
#             if roboprinter.printer_instance._printer.get_current_connection()[0] == 'Closed':
#                 is_closed = True
#             else:
#                 is_closed = False
#
#             is_error = roboprinter.printer_instance._printer.is_error()
#
#             if is_closed and self.connection_popup is None:
#                 Logger.info('Popup: Init')
#                 self.connection_popup = self.generate_connection_popup(title='Connection Closed', text='Printer not detected\n\n\nCheck connection')
#
#             if is_error and self.connection_popup is None:
#                 self.connection_popup = self.generate_connection_popup(title='Error State', text='Printer is Error State')
#
#             if not is_closed_or_error and self.connection_popup is not None:
#                 Logger.info('Popup: Dismissed')
#                 self.connection_popup.dismiss()
#                 self.connection_popup = None
#
#         def generate_connection_popup(self, title, text, dismiss=False, close_button=False, *args, **kwargs):
#             # TODO change name to generate_popup because it can be used for more than just connection closed or error states
#             l = Label(
#                 text=text,
#                 font_size=30
#                 )
#             bl = FloatLayout()
#             bl.add_widget(l)
#             if close_button:
#                 b = Button(
#                     text="Close",
#                     font_size=30,
#                     )
#                 bl.add_widget(b)
#             p = Popup(
#                 title=title,
#                 content=bl,
#                 size_hint=(None,None),
#                 size=(500,400),
#                 auto_dismiss=dismiss,
#                 title_size=30
#                 )
#
#             l.pos_hint= {'center_x': .5, 'top': 1.25}
#
#             if close_button:
#                 b.fbind('on_press', p.dismiss)
#                 b.size_hint = .5,.3
#                 b.pos_hint= {'center_x': .5, 'y': 0}
#
#             p.open()
#             return p
#
#
#
#         def generate_popup(self, **kwargs):
#             pass
#
#         def receive_message(*args):
#             """
#             Receive Message from C SDK on Raspberry pi.
#             :return:
#             """
#             Logger.info("Received message started:")
#             if mq is None:  # if no mq exists
#                 pass
#
#             else:  # if mq exists
#                 while True:
#                     Logger.info('starting Received message')
#                     (message, priority) = mq.receive()
#                     Logger.info('Received message: {}'.format(message))
#
#                     if message:
#                         msg = message.decode("utf-8")
#                         Logger.info(msg)
#                         p = KaaPopup(message=msg)
#                         p.open()
#                     else:
#                         continue
#         def generate_file_screen(self, **kwargs):
#             # Accesible to FilesButton
#             # Instantiates BackButtonScreen and passes values for dynamic properties:
#             # backbutton label text, print information, and print button.
#             file_name = kwargs['filename']
#             print_duration = kwargs['print_duration']
#             print_volume = kwargs['print_volume']
#             print_length = kwargs['print_length']
#             file_path = kwargs['file_path']
#             is_usb = kwargs['is_usb']
#             title = file_name.replace('.gcode', '').replace('.gco', '')
#             if len(title) > 10:
#                 title = title[:9] + '...'
#
#             Logger.info('Function Call: generate_new_screen {}'.format(file_name))
#
#             def delete_file(*args): #gets binded to CTA in header
#                 roboprinter.printer_instance._file_manager.remove_file(file_path, file_name)
#                 self.go_back_to_main('files_tab')
#
#             if is_usb:
#                 c = PrintUSB(name='print_file', file_name=file_name, print_duration=print_duration, print_volume=print_volume, print_length=print_length, file_path=file_path)
#             else:
#                 c = PrintFile(name='print_file', file_name=file_name, print_duration=print_duration, print_volume=print_volume, print_length=print_length, file_path=file_path)
#
#             if not is_usb:
#                 self._generate_backbutton_screen(name=c.name, title=title, back_destination='main', content=c, cta=delete_file, icon='Icons/trash.png')
#             else:
#                 self._generate_backbutton_screen(name=c.name, title=title, back_destination='main', content=c)
#
#             return
#
#         def generate_network_utilities_screen(self, **kwargs):
#             #generates network option screen. Utilities > Network > Network Utilities > wifi list || start ap
#             cw = WifiConfigureButton()
#             ap = APButton()
#             ip = IPAddressButton()
#             layout = GridLayout(cols=1, padding=0, spacing=[0,0], size_hint=(1, None))
#
#             layout.bind(minimum_height=layout.setter('height'))
#             layout.add_widget(cw)
#             layout.add_widget(ap)
#             layout.add_widget(ip)
#
#             self._generate_backbutton_screen(name=kwargs['name'], title=kwargs['title'], back_destination=kwargs['back_destination'], content=layout)
#
#         def generate_ip_screen(self, **kwargs):
#             # Misnomer -- Network Status
#             def get_network_status():
#                 netcon = NetconnectdClient()
#                 try:
#                     #Determine mode and IP
#                     status = netcon._get_status()
#                     wifi = status['connections']['wifi']
#                     ap = status['connections']['ap']
#                     wired = status['connections']['wired']
#
#                     if wifi and wired:
#                         ssid = status['wifi']['current_ssid']
#                         ip = netcon.get_ip()
#                         mode = 'Wifi  \"{}\"'.format(ssid)
#                         mode += ' and Wired Ethernet'
#                     elif wifi:
#                         ssid = status['wifi']['current_ssid']
#                         ip = netcon.get_ip()
#                         mode = 'Wifi  \"{}\"'.format(ssid)
#                     elif ap and wired:
#                         mode = 'Hotspot mode and Wired Ethernet'
#                         ip = '10.250.250.1' + ' , ' + netcon.get_ip()
#                     elif ap:
#                         mode = 'Hotspot mode'
#                         ip = '10.250.250.1'
#                     elif wired:
#                         mode = 'Wired ethernet'
#                         ip = netcon.get_ip()
#                     else:
#                         mode = 'Neither in hotspot mode or connected to wifi'
#                         ip = ''
#                     hostname = netcon.hostname()
#                 except Exception as e:
#                     mode = 'Error -- could not determine'
#                     ip = 'Error -- could not determine'
#                     hostname = 'Error -- could not determine'
#                     Logger.error('RoboScreenManager.generate_ip_screen: {}'.format(e))
#                 t = 'Connection status: \n    {}\n\n IP: \n    {}\n\n Hostname: \n    {}'.format(mode, ip, hostname)
#                 c.text = t
#                 return
#             t = "Getting network status..."
#             c = Label(text=t, font_size=30, background_color=[0,0,0,1])
#             self._generate_backbutton_screen(name=kwargs['name'], title=kwargs['title'], back_destination=kwargs['back_destination'], content=c)
#             thread.start_new_thread(get_network_status, ())
#
#         def generate_wifi_list_screen(self, **kwargs):
#             # generates content for the wifi screen and passes it along to self._generate_backbutton_screen(*)
#
#             wifi_list = GridLayout(cols=1, padding=0, spacing=0, size_hint=(1, None))
#             placeholder = Label(text='Connecting...', font_size=30)
#
#             wifi_list.bind(minimum_height=wifi_list.setter('height'))
#             wifi_list.add_widget(placeholder)
#
#             c = ScrollBox(content=wifi_list)
#
#             def append_wifi_list():
#                 wl = NetconnectdClient().command('list_wifi', None)
#                 wifi_list.remove_widget(placeholder)
#                 for w in wl:
#                     ssid = w['ssid']
#                     encrypted = w['encrypted']
#                     quality = w['quality']
#                     text = '{}                                               {}  {}'.format(ssid, encrypted, quality)
#                     b = WifiButton(ssid=ssid, encrypted=encrypted, quality=quality)
#                     wifi_list.add_widget(b)
#
#             def refresh_wifi_list(*args):
#                 wifi_list.clear_widgets()
#                 wifi_list.add_widget(placeholder)
#                 thread.start_new_thread(append_wifi_list, ())
#
#             self._generate_backbutton_screen(name=kwargs['name'], title=kwargs['title'], back_destination=kwargs['back_destination'], content=c, cta=refresh_wifi_list, icon='Icons/trash.png')
#
#             thread.start_new_thread(append_wifi_list, ())
#             return
#
#         def generate_wifi_config_screen(self, **kwargs):
#             # generates the wifi configuration screen
#             if kwargs['encrypted']:
#                 c = WifiPasswordInput(ssid=kwargs['ssid'])
#             else:
#                 c = WifiUnencrypted(ssid=kwargs['ssid'])
#
#             self._generate_backbutton_screen(name=kwargs['name'], title=kwargs['title'], back_destination=kwargs['back_destination'], content=c)
#
#             return
#
#         def generate_wifi_confirmation_screen(self, **kwargs):
#             # generates the wifi confirmation screen. This screen tells the user whether the wifi connected correctly or not.
#             Window.release_all_keyboards() #Removes keyboard that was requested in wifi config screen.
#             ssid = kwargs['ssid']
#             data = {'ssid': ssid, 'psk': kwargs['psk'], 'force': True}
#             current_screen = kwargs['name']
#             Logger.info('Wifi Credentials: {} -- {}'.format(ssid, kwargs['psk']))
#             c = BoxLayout(orientation='vertical')
#             feedback = WifiConfirmation()
#             c.add_widget(feedback)
#             s = self._generate_backbutton_screen(name=current_screen, title=kwargs['title'], back_destination=kwargs['back_destination'], content=c)
#
#             # unbind on_press callback that is defined in <BackButtonScreen>
#             def unbind_onpress_fs():
#                 # unbind on_press callback that is defined in <BackButtonScreen>
#
#                 old_fs = s.ids.back_button.get_property_observers('on_press', True)
#                 for f in old_fs:
#                     s.ids.back_button.unbind_uid('on_press', f[4]) #uid is the 5th in tuple
#
#                 old_fs = s.ids.back_button.get_property_observers('on_press', True)
#
#             # rebind the backbuttonscreen's back_button function so that user cannot go back to screen while waiting for netconnectd to respond. Rebind it to go_back_to_screen after netconnectd responds in connect()
#             def disable_back_button(*args, **kwargs):
#                 self.generate_connection_popup(title='Back Button Disabled', text='Please wait until process completes.', dismiss=True, close_button=True)
#
#             unbind_onpress_fs()
#             s.ids.back_button.fbind('on_press', disable_back_button)
#
#             def connect():
#                 try:
#                     NetconnectdClient().command('configure_wifi', data)
#                     t = 'Successfully connected to {}'.format(ssid)
#                     success_button = SuccessButton(current_screen=current_screen)
#                     c.add_widget(success_button)
#                 except Exception as e:
#                     Logger.error('Wifi: {}'.format(e))
#                     t = "Could not connect to {}".format(ssid)
#                 feedback.text = t
#
#                 # unbind the pop up window function
#                 unbind_onpress_fs()
#
#                 # Rebind backbutton to gobacktoscreen after netconnectd responds
#                 def renable_back_button(*args, **kwargs):
#                     self.go_back_to_screen(current=s.name, destination=s.back_destination)
#                 s.ids.back_button.fbind('on_press', renable_back_button)
#
#             thread.start_new_thread(connect, ()) #this allows the confirmation screen to render before receiving result from netconnectd
#
#         def generate_start_apmode_screen(self, **kwargs):
#             #generate screen with button prompting user to start ap mode
#             ap = StartAPButton()
#             c = FloatLayout()
#             c.add_widget(ap)
#             self._generate_backbutton_screen(name=kwargs['name'], title=kwargs['title'], back_destination=kwargs['back_destination'], content=c)
#
#         def generate_ap_confirmation_screen(self, **kwargs):
#             #generate screen with confirmation message about start_ap mode command
#             c = BoxLayout(orientation='vertical')
#             feedback = APConfirmation()
#             current_screen = kwargs['name']
#
#             c.add_widget(feedback)
#             s = self._generate_backbutton_screen(name=current_screen, title=kwargs['title'], back_destination=kwargs['back_destination'], content=c)
#
#             # unbind on_press callback that is defined in <BackButtonScreen>
#             def unbind_onpress_fs():
#                 # unbind on_press callback that is defined in <BackButtonScreen>
#
#                 old_fs = s.ids.back_button.get_property_observers('on_press', True)
#                 for f in old_fs:
#                     s.ids.back_button.unbind_uid('on_press', f[4]) #uid is the 5th in tuple
#
#                 old_fs = s.ids.back_button.get_property_observers('on_press', True)
#
#             # rebind the backbuttonscreen's back_button function so that user cannot go back to screen while waiting for netconnectd to respond. Rebind it to go_back_to_screen after netconnectd responds in connect()
#             def disable_back_button(*args, **kwargs):
#                 self.generate_connection_popup(title='Back Button Disabled', text='Please wait until process completes.', dismiss=True, close_button=True)
#
#             unbind_onpress_fs()
#             s.ids.back_button.fbind('on_press', disable_back_button)
#
#             def connect():
#                 try:
#                     netcon = NetconnectdClient()
#                     netcon.command('forget_wifi', None)
#                     netcon.command('start_ap', None)
#                     t = 'Successfully started AP Mode!'
#                     b = SuccessButton(current_screen=current_screen)
#                     c.add_widget(b)
#                 except Exception as e:
#                     Logger.error('Start AP: {}'.format(e))
#                     t = "Could not start AP Mode."
#                 feedback.text = t
#
#                 # unbind the pop up window function
#                 unbind_onpress_fs()
#
#                 # Rebind backbutton to gobacktoscreen after netconnectd responds
#                 def renable_back_button(*args, **kwargs):
#                     self.go_back_to_screen(current=s.name, destination=s.back_destination)
#                 s.ids.back_button.fbind('on_press', renable_back_button)
#
#             thread.start_new_thread(connect, ())
#             return
#
#         def _generate_backbutton_screen(self, name, title, back_destination, content, **kwargs):
#             #helper function that instantiate the screen and presents it to the user
#             # input are screen properties that get presented on the newly generated screen
#             s = BackButtonScreen(name=name, title=title, back_destination=back_destination, content=content, **kwargs)
#             s.populate_layout()
#             self.add_widget(s)
#             self.current = s.name
#
#             return s
#
#         def generate_wizards_screen(self, **kwargs):
#             name = kwargs['name']
#             title = kwargs['title']
#             back_destination = kwargs['back_destination']
#
#             c = GridLayout(cols=1, padding=0, spacing=0, size_hint=(1, None))
#             text_field = '[size=30]{:<55}[/size]>'
#             ztext = text_field.format('Z Offset Wizard')
#             ftext = '[size=30]{:<47}[/size]>'.format('Filament Loading Wizard') #does not use text_field because Kivy renders button text differently regardless if all text length is uniform. In this case, len(ftext) == len(ztext) == len(ptext) if all strings get formatted according to text_field YET ftext will be rendered offset by kivy...
#             ptext = text_field.format('Preheat Wizard')
#             z = WizardButton(text=ztext)
#             f = WizardButton(text=ftext)
#             p = WizardButton(text=ptext)
#
#             def zwrapper(*args):
#                 #makes self.generate_zaxis_wizard accesible to button's bind method
#                 self.generate_zaxis_wizard(
#                     name='zoffset',
#                     title='Z Offset Wizard',
#                     back_destination=name
#                 )
#             def fwrapper(*args):
#                 pass
#
#             def pwrapper(*args):
#                 self.generate_preheat_wizard(
#                     name='preheat_wizard',
#                     title='Preheat Wizard',
#                     back_destination=name
#                 )
#
#             z.bind(on_press= zwrapper)
#             f.bind(on_press=fwrapper)
#             p.bind(on_press=pwrapper)
#
#             c.add_widget(z)
#             c.add_widget(f)
#             c.add_widget(p)
#
#             self._generate_backbutton_screen(name=name, title=title, back_destination=back_destination, content=c)
#
#         def generate_qr_screen(self, **kwargs):
#             #generates the screen with a QR code image
#             #
#             c = QRCodeScreen()
#             self._generate_backbutton_screen(name=kwargs['name'], title=kwargs['title'], back_destination=kwargs['back_destination'], content=c)
#             return
#
#         def go_back_to_main(self, tab=None):
#             #Moves user to main screen and deletes all other screens
#             #used by end of sequence confirmation buttons
#             #optional tab parameter. If not None it will go back to that tab
#             Logger.info('Function Call: go_back_to_main')
#             self.current = 'main'
#
#             if tab is not None:
#                 main = self.current_screen
#                 main.open_tab(tab)
#
#             #remove all screens that are not main
#             for s in self.screen_names:
#                 if s is not 'main':
#                     d = self.get_screen(s)
#                     self.remove_widget(d)
#                 else:
#                     continue
#
#
#             Logger.info('Screens: {}'.format(
#                 self.screen_names))  # not necessary; using this to show me that screen gets properly deleted
#
#         def go_back_to_screen(self, current, destination):
#             # Goes back to destination and deletes current screen
#             ps = self.get_screen(current)
#             self.current = destination
#             self.remove_widget(ps)
#             Logger.info('go_back_to_screen: current {}, dest {}'.format(current, destination))
#
#             if current == 'wifi_config_screen':
#                 Window.release_all_keyboards()
#             #used to delete keyboards after user hits backbutton from Wifi Config Screen. This is a brute force implementation.... TODO figure out a more elegant and efficient way to perform this call.
#
#             return
#
#         def generate_zaxis_wizard(self, **kwargs):
#             screen_0 = kwargs['name']
#             title = kwargs['title']
#             back_destination = kwargs['back_destination']
#             global ZOFFSET
#             ZOFFSET = 0
#
#             ###completion screen###
#             def completion_screen(*args):
#                 global ZOFFSET
#                 write_zoffset = 'M851 Z{}'.format(ZOFFSET)
#                 save_to_eeprom = 'M500'
#                 roboprinter.printer_instance._printer.commands([write_zoffset, save_to_eeprom])
#
#                 screen_3 = screen_0 + '[3]'
#                 title = 'Z Offset'
#                 back_destination = screen_0 + '[2]'
#                 layout = BoxLayout(orientation='vertical')
#                 feedback = Label(text='Successfully saved z-offset value: {}'.format(ZOFFSET), font_size=30)
#                 ok = SuccessButton()
#                 ok.unbind(on_press=self.go_back_to_main)
#
#                 def move_bed_AND_go_back_to_main(*args):
#                     roboprinter.printer_instance._printer.commands('G1 Z160')
#                     self.go_back_to_main()
#
#                 ok.bind(on_press=move_bed_AND_go_back_to_main)
#
#                 layout.add_widget(feedback)
#                 layout.add_widget(ok)
#
#                 self._generate_backbutton_screen(
#                     name=screen_3,
#                     title=title,
#                     back_destination=back_destination,
#                     content = layout
#                     )
#
#             ###zoffset screen###
#             def zoffset_screen(*args):
#                 global ZOFFSET
#
#                 screen_2 = screen_0 + '[2]'
#                 title = 'Z Offset'
#                 back_destination = screen_0 + '[1]'
#                 layout = BoxLayout(orientation='horizontal')
#                 left_side = BoxLayout(orientation='vertical')
#                 up = Button(text="Up", id='up')
#                 down = Button(text="Down", id='down')
#                 right_side = BoxLayout(orientation='vertical')
#                 increments = BoxLayout(orientation='horizontal')
#                 mm2 = ToggleButton(text="0.2mm", group='mm', id='mm2')
#                 mm1 = ToggleButton(text="0.1mm", group='mm', state='down', id='mm1')
#                 finished = Button(text='Finished')
#
#                 def increment(b):
#                     global ZOFFSET
#                     if b is up and mm2.state == 'down':
#                         roboprinter.printer_instance._printer.jog('z', -0.2) #.commands(G1 Z0, G1 Z0) ; .home(axis)  ; .jog()
#                         ZOFFSET -= 0.2
#                     elif b is up and mm1.state == 'down':
#                         roboprinter.printer_instance._printer.jog('z', -0.1)
#                         ZOFFSET -= 0.1
#                     elif b is down and mm2.state == 'down':
#                         roboprinter.printer_instance._printer.jog('z', +0.2)
#                         ZOFFSET += 0.2
#                     elif b is down and mm1.state == 'down':
#                         roboprinter.printer_instance._printer.jog('z', +0.1)
#                         ZOFFSET += 0.1
#                     else:
#                         Logger.info('Increment: Button pushed but no increment')
#
#                 finished.bind(on_press=completion_screen)
#                 up.bind(on_press=increment)
#                 down.bind(on_press=increment)
#
#                 increments.add_widget(mm2)
#                 increments.add_widget(mm1)
#
#                 left_side.add_widget(up)
#                 left_side.add_widget(down)
#
#                 right_side.add_widget(increments)
#                 right_side.add_widget(finished)
#
#                 layout.add_widget(left_side)
#                 layout.add_widget(right_side)
#
#                 self._generate_backbutton_screen(
#                     name=screen_2,
#                     title=title,
#                     back_destination=back_destination,
#                     content=layout
#                 )
#
#             ###zmin screen####
#             def zmin_screen(*args):
#                 global ZOFFSET
#                 ZOFFSET = 0
#                 screen_1 = screen_0 + '[1]'
#                 title = 'Z Offset'
#                 back_destination = screen_0
#                 layout = BoxLayout(orientation='vertical')
#                 instructions = Label(
#                     text='Moving z-axis to min position...',
#                     font_size=30
#                     )
#                 layout.add_widget(instructions)
#
#                 self._generate_backbutton_screen(name=screen_1, title=title, back_destination=back_destination, content=layout)
#
#                 def add_instructions():
#                     import time
#                     roboprinter.printer_instance._printer.commands(['G28', 'G91', 'G1 X5 Y30', 'G90' ])
#                     roboprinter.printer_instance._printer.commands(['M851 Z-10', 'M500'])
#                     time.sleep(5) #Brute force implementation because currently not sure how to make this function aware when printer has finished moving z axis
#                     instructions.text = "Instructions: \nMove the z-axis up to extruder until \n a piece of paper can just barely pass through." #TODO clearer instructions
#                     start = Button(text='Begin', size_hint=(.5, .5))
#                     start.bind(on_press=zoffset_screen)
#                     layout.add_widget(start)
#
#                 thread.start_new_thread(add_instructions, ())
#
#
#             ###First screen content###
#             layout = FloatLayout()
#             start = Button(
#                 text='Start',
#                 font_size=40,
#                 pos_hint={'center_x': .5, 'center_y': .5},
#                 size_hint=(.5, .5), border=(40,40,40,40), background_normal="Icons/rounded.png"
#                 )
#             start.bind(on_press=zmin_screen)
#             layout.add_widget(start)
#
#             self._generate_backbutton_screen(name=screen_0, title=title, back_destination=back_destination, content=layout)
#
#         def generate_manualcontrol_screen(self, **kwargs):
#             name = kwargs['name']
#             title = kwargs['title']
#             back_destination = kwargs['back_destination']
#
#             c = ManualControl()
#             t = TemperatureControl()
#
#             def toggle_controls(*args):
#                 # toggles between manual control and temperature control
#                 s = self.get_screen(name)
#                 if s.ids.cta.background_normal == 'Icons/head_1.png':
#                     s.ids.cta.background_normal = 'Icons/printer.png'
#                     s.ids.content_layout.clear_widgets()
#                     s.ids.content_layout.add_widget(t)
#                     s.ids.title.text = 'Temperature Control'
#                 else:
#                     s.ids.cta.background_normal = 'Icons/head_1.png'
#                     s.ids.content_layout.clear_widgets()
#                     s.ids.content_layout.add_widget(c)
#                     s.ids.title.text = 'Motor Control'
#
#             self._generate_backbutton_screen(name=name, title=title, back_destination=back_destination, content=c, cta=toggle_controls, icon='Icons/head_1.png')
#
#         def generate_preheat_wizard(self, **kwargs):
#             _name = kwargs['name']
#             # preheat wizard layout
#             c = PreheatWizard(self, name=_name) #pass self so that Preheat can render secondary screens
#             self._generate_backbutton_screen(name=_name, title=kwargs['title'], back_destination=kwargs['back_destination'], content=c)
#
#             return
