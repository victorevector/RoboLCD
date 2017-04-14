# coding=utf-8
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.tabbedpanel import TabbedPanelHeader
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.uix.modalview import ModalView
from .. import roboprinter
from connection_popup import Zoffset_Warning_Popup, Error_Popup, Update_Warning_Popup
import math
import subprocess
from multiprocessing import Process
from pconsole import pconsole
from updater import UpdateScreen


class PrinterStatusTab(TabbedPanelHeader):
    """
    Represents the Printer Status tab header and dynamic content
    """
    pass


class PrinterStatusContent(GridLayout):
    """
    """
    filename = StringProperty("")
    status = StringProperty("[ref=status][/ref]")
    extruder_one_temp = NumericProperty(0)
    extruder_one_max_temp = NumericProperty(200)
    extruder_two_max_temp = NumericProperty(200)
    extruder_two_temp = NumericProperty(0)
    bed_max_temp = NumericProperty(200)
    bed_temp = NumericProperty(0)
    progress = StringProperty('')
    startup = False 
    safety_counter = 0
    update_lock = False
    

    def __init__(self,**kwargs):
        super(PrinterStatusContent, self).__init__(**kwargs)
        
        
        self.splash_event = Clock.schedule_interval(self.turn_off_splash, .1)
        self.update_lock = False
        Clock.schedule_interval(self.safety, 1)


    def update(self, dt):

        
        # temps = roboprinter.printer_instance._printer.get_current_temperatures()
        current_data = roboprinter.printer_instance._printer.get_current_data()
        filename = current_data['job']['file']['name']
        is_operational = current_data['state']['flags']['operational']
        is_ready = current_data['state']['flags']['ready']
        is_printing = current_data['state']['flags']['printing']
        is_paused = current_data['state']['flags']['paused']
        progress = current_data['progress']['completion']
        status = current_data['state']['text']
        #TODO: REFACTOR because the following variable assignments WILL fail when we starting implementing lcd_large.kv since these widgets wont exists for that iteration

       
        left_of_extruder = self.ids.left_of_extruder_status
        right_of_extruder = self.ids.right_of_extruder_status
        e_children = left_of_extruder.children + right_of_extruder.children

        self.filename = filename.replace('.gcode','') if filename else 'No File Loaded'

        if is_printing or is_paused:
            p_transformed = int(progress)
            self.progress = '[size=50]{}%[/size]'.format(p_transformed)
        else:
            self.progress = ''

        if progress == 100:
            roboprinter.printer_instance._printer.unselect_file()

       

        temp1 = self.grab_target_and_actual('tool0')
        self.extruder_one_max_temp = temp1['target']
        self.extruder_one_temp = temp1['actual']

        temp2 = self.grab_target_and_actual('tool1')
        self.extruder_two_max_temp = temp2['target']
        self.extruder_two_temp = temp2['actual']

        bed = self.grab_target_and_actual('bed')
        self.bed_max_temp = bed['target']
        self.bed_temp = bed['actual']


        if (is_printing or is_paused) and len(e_children) == 0:
            left_of_extruder.add_widget(StartPauseButton())
            right_of_extruder.add_widget(CancelButton())
        elif len(e_children) > 0 and not is_printing and not is_paused:
            left_of_extruder.clear_widgets()
            right_of_extruder.clear_widgets()

    def grab_target_and_actual(self, tool):
        acceptable_tools = {'tool0': 'tool0',
                        'tool1': 'tool1',
                        'bed' : 'bed'
        }

        actual = 0
        target = 0

        if tool in acceptable_tools:
            temps = roboprinter.printer_instance._printer.get_current_temperatures()

            if tool in temps:
                if 'actual' in temps[tool] and 'target' in temps[tool]:
                    if temps[tool]['actual'] == None:
                        actual = 0
                        target = 0
                    else:
                        actual = temps[tool]['actual']
                        target = temps[tool]['target'] 
                else:
                    actual = 0
                    target = 0

        return {'actual':actual, 'target':target}

    def detirmine_layout(self):
        printer_type = roboprinter.printer_instance._settings.global_get(['printerProfiles', 'defaultProfile'])
        model = printer_type['model']

        tool0 = False
        tool1 = False
        bed = False


        if model == "Robo R2":
            if printer_type['extruder']['count'] == 1:
                tool0 = True
            elif printer_type['extruder']['count'] > 1:
                tool0 = True
                tool1 = True
            if printer_type['heatedBed']:
                bed = True
        elif model == "Robo C2":
            return

        if tool0 and tool1 and bed:
            tool_0 = Tool_Status("Extruder 1", "tool0")
            tool_1 = Tool_Status("Extruder 2", "tool1")
            bed = Tool_Status("Bed", "bed")

            self.ids.tools.add_widget(tool_0)
            self.ids.tools.add_widget(tool_1)
            self.ids.tools.add_widget(bed)

        elif tool0 and bed:
            tool_0 = Tool_Status("Extruder 1", "tool0")
            bed = Tool_Status("Bed", "bed")
            self.ids.tools.add_widget(tool_0)
            self.ids.tools.add_widget(bed)
            
        elif tool0:
            tool_0 = Tool_Status("Extruder 1", "tool0")
            self.ids.tools.add_widget(tool_0)
            
        else:
            Logger.info("##################### TOOL STATUS ERROR #######################")

    def start_print(self):
        roboprinter.printer_instance._printer.start_print()

    def turn_off_splash(self, dt):
        #turn off the splash screen
        if self.extruder_one_temp != 0 and self.startup == False:
            #Logger.info("Turning Off the Splash Screen!")
            self.detirmine_layout()

            #check for updates
            self.check_updates()
            #check for updates every hour
            Clock.schedule_interval(self.update_clock, 3600)
            subprocess.call(['sudo pkill omxplayer'], shell=True)
            self.startup = True
             
            
            return False

    def update_clock(self, dt):
        current_data = roboprinter.printer_instance._printer.get_current_data()
        is_printing = current_data['state']['flags']['printing']
        is_paused = current_data['state']['flags']['paused']

        if not is_printing and not is_paused:
            self.check_updates()

    def check_updates(self):
        self.updates = UpdateScreen(populate=False)
        self.updates.refresh_versions()
        installed = self.updates.get_installed_version()
        available = self.updates.get_avail_version()

        Logger.info("Available: " + str(available) + " Installed: " + str(installed) )

        if installed < available and available != "Connection Error!" and not self.update_lock:
            self.update_lock = True
            #updater popup
            update = Update_Warning_Popup(self.run_update, self.unlock_updater)
            update.open()

    def run_update(self):
        self.updates.run_updater()

    def unlock_updater(self):
        self.update_lock = False



    def safety(self,dt):
        self.safety_counter += 1
        safety_time = 60

        if self.safety_counter == safety_time and self.startup == False:
            #Logger.info("Safety Counter went off!")
            self.detirmine_layout()
            #check for updates
            self.check_updates()
            #check for updates every hour
            Clock.schedule_interval(self.update_clock, 3600)

            subprocess.call(['sudo pkill omxplayer'], shell=True)
            Clock.unschedule(self.splash_event)
            return False
        elif self.safety_counter == safety_time and self.startup == True:
            #Logger.info("Unscheduling safety event")
            return False

       

class StartPauseButton(Button):
    subtract_amount =  NumericProperty(40)
    def __init__(self, **kwargs):
        super(StartPauseButton, self).__init__(**kwargs)
        Clock.schedule_interval(self.sync_with_devices, .1)
        Clock.schedule_interval(self.colors, .1)
        self.auto_pause_pop = None

    def toggle_pause_print(self):
        roboprinter.printer_instance._printer.toggle_pause_print()


    def sync_with_devices(self, dt):
        '''makes sure that button's state syncs up with the commands that other devices push to the printer '''
        is_paused = roboprinter.printer_instance._printer.is_paused()
        if is_paused and self.ids.stopgo_label.text ==  '[size=30]Pause[/size]':
            self.ids.stopgo_label.text =  '[size=30]Resume[/size]'
            self.ids.stopgo_icon.source = 'Icons/Manual_Control/start_button_icon.png'
            self.subtract_amount = 50
            self.check_pause_status()
        elif not is_paused and self.ids.stopgo_label.text ==  '[size=30]Resume[/size]':
            self.ids.stopgo_label.text =  '[size=30]Pause[/size]'
            self.ids.stopgo_icon.source = 'Icons/Manual_Control/stop_button_icon.png'
            self.subtract_amount =  40
            self.auto_pause_pop = None

    def check_pause_status(self):
        if roboprinter.printer_instance.check_auto_pause != None:
            auto_pause = roboprinter.printer_instance.check_auto_pause()
            if auto_pause and self.auto_pause_pop == None:
                self.auto_pause_pop = Error_Popup("Filament Has Run out", "Please add more filament")
                self.auto_pause_pop.open()
        else:
            Logger.info("RoboLCD Does not have a helper function for auto pause")

    def colors(self, dt):
        '''updates the color  of the button based on Start or Pause state. Green for Start'''
        is_paused = roboprinter.printer_instance._printer.is_paused()
        if is_paused:
            self.background_normal = 'Icons/green_button_style.png'

        else:
            self.background_normal = 'Icons/blue_button_style.png'

class CancelButton(Button):
    def cancel_print(self, *args):
        Clock.schedule_once(self.cancel_callback, 0.5)

    def cancel_callback(self, dt):
        if self.is_printing() or roboprinter.printer_instance._printer.is_paused() == True:
            roboprinter.printer_instance._printer.cancel_print()
            Logger.info('Cancellation: Successful')
            Clock.schedule_once(self.unselect_callback, 30)
            self.mv.dismiss()
            

    def unselect_callback(self, dt):
        roboprinter.printer_instance._printer.unselect_file()
        Logger.info('Unselect: Successful')
    def no_button(self, instance):
        pass
    def modal_view(self):
        self.mv = ModalPopup()
        self.mv.ids.yes_button.bind(on_press = self.cancel_print)
        self.mv.ids.no_button.bind(on_press = self.no_button)
        self.mv.open()

    def is_printing(self):
        """ whether the printer is currently operational and ready for a new print job"""
        printing = roboprinter.printer_instance._printer.is_printing()
        if not printing:
            return False
        else:
            return True

class ModalPopup(ModalView):
    def cancellation_feedback(self):
        self.ids.modal_question.text = "Cancelling..."

    def dismiss_popup(self, *args):
        self.cancellation_feedback()

class Tool_Status(FloatLayout):
    name = StringProperty("Error")
    current_temperature = NumericProperty(0)
    max_temp = NumericProperty(0)
    tool = StringProperty('tool0')

    def __init__(self, name, tool, **kwargs):
        super(Tool_Status, self).__init__(**kwargs)
        self.name=name
        self.tool = tool
        Clock.schedule_interval(self.update_temp_and_progress, .1)

    def update_temp_and_progress(self, dt):
        self.temperature()


    def temperature(self):
        temps  = roboprinter.printer_instance._printer.get_current_temperatures()
        
        try:
            self.current_temperature = temps[self.tool]['actual']
            
            self.max_temp = temps[self.tool]['target']

            if self.tool == 'bed':
                if 'bed' in pconsole.temperature:
                    if float(pconsole.temperature['bed']) <= 0:
                        self.current_temperature = 0

            
            #Logger.info(str(self.current_temperature) + " "  + str(self.max_temp))
        except Exception as e:
            #Logger.info("Temperature Error")
            if self.tool == 'bed':
                if 'bed' in pconsole.temperature:
                    if float(pconsole.temperature['bed']) <= 0:
                        self.current_temperature = 0
          
        
        
