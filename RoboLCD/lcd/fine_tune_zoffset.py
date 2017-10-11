from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty, ListProperty
from .. import roboprinter
from printer_jog import printer_jog
from kivy.clock import Clock
from pconsole import pconsole
from connection_popup import Error_Popup, Warning_Popup
import functools
from functools import partial
from common_screens import Button_Screen, Picture_Button_Screen
import time
from Preheat_Wizard import Preheat_Overseer

class Fine_Tune_ZOffset(object):
    """docstring for Fine_Tune_ZOffset"""
    def __init__(self):
        super(Fine_Tune_ZOffset, self).__init__()
        self.line_lock = False
        self.model = roboprinter.printer_instance._settings.get(['Model'])
        self.mode = "R2L" #Modes are L2R and R2L
        self.set_mode(self.mode)
        self.prepared_printer = False
        self.extruder_setting = 190
        self.bed_setting = 60
        pconsole.query_eeprom()
        self.welcome_screen()

        #variable that does not get a soft restart
        self.preparing_in_progress = False
        

    def set_mode(self, mode):
        self.mode = mode
        if mode == "L2R":
            if self.model == "Robo R2":
                self.start_pos_x = 5.00
                self.start_pos_y = 190.00
                self.travel_amount = 10.00
                self.max_x_travel = 195.00
                self.drop_amount = 100.00
            else:
                self.start_pos_x = 5.00
                self.start_pos_y = 120.00
                self.travel_amount = 10.00
                self.max_x_travel = 126.00
                self.drop_amount = 30.00

        elif mode == "R2L":
            if self.model == "Robo R2":
                self.start_pos_x = 190.00
                self.start_pos_y = 190.00
                self.travel_amount = 10.00
                self.max_x_travel = 5.00
                self.drop_amount = 100.00
            else:
                self.start_pos_x = 125.00
                self.start_pos_y = 120.00
                self.travel_amount = 10.00
                self.max_x_travel = 4.00
                self.drop_amount = 30.00

        self.x = self.start_pos_x

        

    def welcome_screen(self):
        layout = Button_Screen(roboprinter.lang.pack['FT_ZOffset_Wizard']['Welcome']['Body'], 
                               self.choose_preheat_settings)
        title = roboprinter.lang.pack['FT_ZOffset_Wizard']['Welcome']['Title']
        name = 'welcome_fine_tune'
        back_destination = roboprinter.robo_screen()

        roboprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )


    def welcome_screen_enter(self):
        Logger.info("Enter Function Entered!#################")
        #soft reset just incase the user hits the back button
        self.line_lock = False
        self.model = roboprinter.printer_instance._settings.get(['Model'])
        self.mode = "R2L" #Modes are L2R and R2L
        self.set_mode(self.mode)
        self.prepared_printer = False

    def choose_preheat_settings(self):
        Preheat_Overseer(end_point=self.collect_heat_settings,
                         name='preheat_wizard',
                         title=roboprinter.lang.pack['Utilities']['Preheat'],
                         back_destination='welcome_fine_tune')

    def collect_heat_settings(self, extruder, bed):
        self.extruder_setting = extruder
        self.bed_setting = bed
        self.user_set_mode()

    def user_set_mode(self):

        #do a soft reset if we have entered the preparing screen
        if self.preparing_in_progress:
            self.welcome_screen_enter()

        

        #set the mode
        from bed_calibration_wizard import Modal_Question, Wait_Screen
        def left_corner():
            self.set_mode("L2R")
            self.check_for_valid_start()
        def right_corner():
            self.set_mode("R2L")
            self.check_for_valid_start()

        layout = Modal_Question(roboprinter.lang.pack['FT_ZOffset_Wizard']['Set_Mode']['Sub_Title'] , 
                                roboprinter.lang.pack['FT_ZOffset_Wizard']['Set_Mode']['Body'],
                                roboprinter.lang.pack['FT_ZOffset_Wizard']['Set_Mode']['Option1'],
                                roboprinter.lang.pack['FT_ZOffset_Wizard']['Set_Mode']['Option2'],
                                left_corner,
                                right_corner
                                )

        title = roboprinter.lang.pack['FT_ZOffset_Wizard']['Set_Mode']['Title']
        name = self.name_generator()
        back_destination = 'welcome_fine_tune'
        if roboprinter.robosm.has_screen('welcome_fine_tune'):
            back_destination = 'welcome_fine_tune'
        elif roboprinter.robosm.has_screen('text_instructions'):
            back_destination = 'text_instructions'
        

        roboprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )
    def name_generator(self):
        if roboprinter.robosm.has_screen('pick_a_corner'):
            has_name = True
            name = 'pick_a_corner'
            updated_name = ''
            counter = 0
            while has_name:
                updated_name = name + '[' + str(counter) + ']'
                has_name = roboprinter.robosm.has_screen(updated_name)
                counter += 1
            Logger.info("Updated Name: " + updated_name)
            return updated_name
        else:
            return 'pick_a_corner'

    def check_for_valid_start(self):
        if self.prepared_printer:
            Logger.info("New Corner Picked########")
            roboprinter.printer_instance._printer.commands('M400')#Wait for all previous commands to finish (Clear the buffer)
            roboprinter.printer_instance._printer.commands('G1 X'+ str(self.start_pos_x) + ' Y'+ str(self.start_pos_y) + ' F5000') # go to first corner
            self.instruction1()
        else:

            start = self.check_offset()
    
            #if the ZOffset is not right don't allow the user to continue
            if start:
                self._prepare_for_lines()
            else:
                zoff = pconsole.home_offset['Z']
                ep = Error_Popup(roboprinter.lang.pack['FT_ZOffset_Wizard']['Z_Error']['Title'], roboprinter.lang.pack['FT_ZOffset_Wizard']['Z_Error']['Body'] + str(zoff) + roboprinter.lang.pack['FT_ZOffset_Wizard']['Z_Error']['Body1'],callback=partial(roboprinter.robosm.go_back_to_main, tab='printer_status_tab'))
                ep.open()


    
    #check the offset to see if it is in an acceptable range
    def check_offset(self):
        #if it's already in the preparing or if it has already been prepared there's no need to check
        if not self.preparing_in_progress and not self.prepared_printer:
            pconsole.query_eeprom()

            offset = float(pconsole.home_offset['Z'])
            #make sure the range is within -20 - 0
            if offset > -20.00 and not offset > 0.00 and offset != 0.00:
                return True
            else:
                return False
        else:
            return True


    def _prepare_for_lines(self):
        from bed_calibration_wizard import Modal_Question, Wait_Screen
        if not self.prepared_printer and not self.preparing_in_progress:
            self.preparing_in_progress = True
            roboprinter.printer_instance._printer.commands('M400')#Wait for all previous commands to finish (Clear the buffer)
            roboprinter.printer_instance._printer.commands('M104 S' + str(self.extruder_setting)) #Set Temperature
            roboprinter.printer_instance._printer.commands('M140 S' + str(self.bed_setting))
            roboprinter.printer_instance._printer.commands('G28') #Home Printer
            roboprinter.printer_instance._printer.commands('G29')
            roboprinter.printer_instance._printer.commands('G1 X'+ str(self.start_pos_x) + ' Y'+ str(self.start_pos_y) + ' F5000') # go to first corner
            roboprinter.printer_instance._printer.commands('G1 Z5')
            self.prepared_printer = True
            
            #wait for temperature set
            layout = Wait_Screen(self.instruction1, 
                                 roboprinter.lang.pack['FT_ZOffset_Wizard']['Prepare_Lines']['Sub_Title'] , 
                                 roboprinter.lang.pack['FT_ZOffset_Wizard']['Prepare_Lines']['Body'])
            title = roboprinter.lang.pack['FT_ZOffset_Wizard']['Prepare_Lines']['Title']
            name = 'temp_wait'
            back_destination = 'welcome_fine_tune'
    
            self.prepare_screen = roboprinter.back_screen(
                name=name,
                title=title,
                back_destination=back_destination,
                content=layout
            )
        elif self.preparing_in_progress:
            Logger.info("Re Adding Prepare Screen")
            roboprinter.robosm.add_widget(self.prepare_screen)
            roboprinter.robosm.current = 'temp_wait'
            #Just wait for the preparing screen to do it's thing

    def make_line(self):
        if not self.line_lock:
            
            #Lock the button down for a better user experience
            self.line_lock = True
            Logger.info("Locked!")
            Clock.schedule_once(self.unlock, 18.00)

            pos = pconsole.get_position()
            while not pos:
                pos = pconsole.get_position()
            
            Logger.info("self.x is at: " + str(self.x) + " position x is at: " + str(pos[0]))
            if self.mode == "L2R":
                if float(pos[0]) < self.max_x_travel:
                    self._line()
                else:
                    self.warn_and_restart()
            elif self.mode == "R2L":
                if float(pos[0]) > self.max_x_travel:
                    self._line()
                else:
                    self.warn_and_restart()

    def _line(self):
        roboprinter.printer_instance._printer.commands('M400')#Wait for all previous commands to finish (Clear the buffer)
        roboprinter.printer_instance._printer.commands('G1 Z0.3') #put nozzle on the bed
        roboprinter.printer_instance._printer.commands('G92 E0.00') #reset the E to zero so we can make a line
        roboprinter.printer_instance._printer.commands('G1 E6.00 F500') #extrude filament
        roboprinter.printer_instance._printer.commands('G1 Y' + str(self.travel_amount) + ' E15.00 F500') #make a line
        roboprinter.printer_instance._printer.commands('G1 Z5 E10.00 F500') #Retract filament and pull nozzle off bed          

        #add or subtract based on mode
        if self.mode == "L2R":
            self.x += 10
        elif self.mode == "R2L":
            self.x -= 10
        #Goto next point
        roboprinter.printer_instance._printer.commands('G1 X'+ str(self.x) + ' Y'+ str(self.start_pos_y) + ' F5000') #go to the next line start position

    
    def unlock(self, dt):
        Logger.info("Unlocked!")
        self.line_lock = False
        return False
        

    def warn_and_restart(self):
        pos = pconsole.get_position()
        while not pos:
            pos = pconsole.get_position()

        drop = self.drop_amount - float(pos[2]) 
        Logger.info("Dropping to: " + str(drop))
        roboprinter.printer_instance._printer.commands('M400')#Wait for all previous commands to finish (Clear the buffer)

        #################################################################################################################
                                    #Get off of the endstop so the Z axis works...
        #get bed dimensions
        bed_x = roboprinter.printer_instance._settings.global_get(['printerProfiles','defaultProfile', 'volume','width'])
        bed_y = roboprinter.printer_instance._settings.global_get(['printerProfiles','defaultProfile', 'volume','depth'])

        #calculate final positions
        bed_x = float(bed_x) / 2.0
        bed_y = float(bed_y) / 2.0

        roboprinter.printer_instance._printer.commands('G1 X' + str(bed_x) + ' Y' + str(bed_y) +' F10000')
        #################################################################################################################
        
        roboprinter.printer_instance._printer.commands('G1 Z'+ str(drop) + ' F5000')
        roboprinter.printer_instance._printer.commands('G1 X'+ str(self.start_pos_x) + ' Y'+ str(self.start_pos_y) + ' F5000') # go to first corner
        layout = Button_Screen(roboprinter.lang.pack['FT_ZOffset_Wizard']['Warn_Restart']['Body'] , self.restart)
        title = roboprinter.lang.pack['FT_ZOffset_Wizard']['Warn_Restart']['Title']
        name = 'line_restart'
        back_destination = roboprinter.robo_screen()

        roboprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )

    def restart(self):
        roboprinter.printer_instance._printer.commands('M400')#Wait for all previous commands to finish (Clear the buffer)
        roboprinter.printer_instance._printer.commands('G1 X'+ str(self.start_pos_x) + ' Y'+ str(self.start_pos_y) + ' F5000') # go to first corner
        roboprinter.printer_instance._printer.commands('G1 Z5')
        self.x = self.start_pos_x
        #update position
        pconsole.get_position()
        pconsole.get_position()
        self.user_set_mode()

    def instruction1(self):
        #go to the correct position to start from
        roboprinter.printer_instance._printer.commands('M400')#Wait for all previous commands to finish (Clear the buffer)
        roboprinter.printer_instance._printer.commands('G1 X'+ str(self.start_pos_x) + ' Y'+ str(self.start_pos_y) + ' F5000') # go to first corner
        roboprinter.printer_instance._printer.commands('G1 Z5')

        self.preparing_in_progress = False
        self.prepared_printer = True
        layout = Button_Screen(roboprinter.lang.pack['FT_ZOffset_Wizard']['Instruction']['Body'],
                               self.instruction2)
        title = roboprinter.lang.pack['FT_ZOffset_Wizard']['Instruction']['Title']
        name = 'text_instructions'
        back_destination = roboprinter.robo_screen()

        roboprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )


    def instruction2(self):
        layout = Picture_Instructions()
        title = roboprinter.lang.pack['FT_ZOffset_Wizard']['Instruction']['Title']
        name = 'picture_instructions'
        back_destination = roboprinter.robo_screen()

        roboprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout,
            cta = self.update_home_offset,
            icon = "Icons/Slicer wizard icons/next.png"
        )



    def update_home_offset(self):
        layout = Update_Offset(self.make_line)

        title = roboprinter.lang.pack['FT_ZOffset_Wizard']['Update_HO']['Title']
        name = 'home_adjust'
        back_destination = 'picture_instructions'

        roboprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout,
            cta = self.choose_to_finish,
            icon = "Icons/Slicer wizard icons/next.png"
        )

    def choose_to_finish(self):
        from bed_calibration_wizard import Modal_Question, Wait_Screen
        layout = Modal_Question(roboprinter.lang.pack['FT_ZOffset_Wizard']['Choose_Finish']['Sub_Title'], 
                                roboprinter.lang.pack['FT_ZOffset_Wizard']['Choose_Finish']['Body'], 
                                roboprinter.lang.pack['FT_ZOffset_Wizard']['Choose_Finish']['Option1'],
                                roboprinter.lang.pack['FT_ZOffset_Wizard']['Choose_Finish']['Option2'],
                                self.user_set_mode,
                                self.finish_wizard)

        title = roboprinter.lang.pack['FT_ZOffset_Wizard']['Choose_Finish']['Title']
        name = 'restart_or_quit'
        back_destination = 'home_adjust'

        roboprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )

    def finish_wizard(self):
        roboprinter.printer_instance._printer.commands('M500')
        offset = pconsole.home_offset['Z']
        layout = Picture_Button_Screen(roboprinter.lang.pack['FT_ZOffset_Wizard']['Finish']['Sub_Title'], 
                                      roboprinter.lang.pack['FT_ZOffset_Wizard']['Finish']['Body'] + str(offset),
                                      'Icons/Manual_Control/check_icon.png',
                                      self.goto_main)
        title = roboprinter.lang.pack['FT_ZOffset_Wizard']['Finish']['Title']
        name = 'finish_wizard'
        back_destination = roboprinter.robo_screen()

        roboprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )

    def goto_main(self):
        roboprinter.printer_instance._printer.commands('M104 S0')
        roboprinter.printer_instance._printer.commands('M140 S0')
        roboprinter.printer_instance._printer.commands('G28')
        roboprinter.robosm.go_back_to_main('utilities_tab')


#lines mod
class Update_Offset(BoxLayout):
    i_toggle_mm = ['Icons/Manual_Control/increments_2_1.png', 'Icons/Manual_Control/increments_2_2.png']
    s_toggle_mm = ['0.01mm', '0.05mm']
    f_toggle_mm = [0.01, 0.05]
    toggle_mm = 0
    actual_offset = StringProperty("")

    
    def __init__(self, offset_callback):
        super(Update_Offset, self).__init__()
        self.offset = 0.00
        self.callback = offset_callback
        self.actual_offset = str(pconsole.home_offset['Z'])


    def toggle_mm_z(self):
        self.toggle_mm += 1
        if self.toggle_mm > 1:
            self.toggle_mm = 0

        Logger.info(self.s_toggle_mm[self.toggle_mm])
        self.ids.toggle_label.text = self.s_toggle_mm[self.toggle_mm]
        self.ids.toggle_icon.source = self.i_toggle_mm[self.toggle_mm]

    def set_offset(self):
        current_offset = pconsole.home_offset['Z']
        updated_offset = current_offset + self.offset
        roboprinter.printer_instance._printer.commands('M206 Z' + str(updated_offset))
        pconsole.home_offset['Z'] = updated_offset
        self.actual_offset = str(updated_offset)
        self.offset = 0
        self.callback()

    def add_offset(self):
        self.offset += self.f_toggle_mm[self.toggle_mm]
        self.actual_offset = str(pconsole.home_offset['Z'] + self.offset)
        self.ids.offset_text.text = '[size=27]' + roboprinter.lang.pack['FT_ZOffset_Wizard']['Update_Offset']['Body'] + '\n[/size][size=40][color=#69B3E7]' + str(self.actual_offset) + '[/size]'

    def subtract_offset(self):
        self.offset -= self.f_toggle_mm[self.toggle_mm]
        self.actual_offset = str(pconsole.home_offset['Z'] + self.offset)
        self.ids.offset_text.text = '[size=27]' + roboprinter.lang.pack['FT_ZOffset_Wizard']['Update_Offset']['Body'] + '\n[/size][size=40][color=#69B3E7]' + str(self.actual_offset) + '[/size]'

class Picture_Instructions(BoxLayout):
    
    def __init__(self):
        super(Picture_Instructions, self).__init__()
        pass    

# class Button_Screen(BoxLayout):
#     body_text = StringProperty("Error")
#     button_function = ObjectProperty(None)
#     button_text = StringProperty("OK")
    


#     def __init__(self, body_text, button_function, button_text = "OK", **kwargs):
#         super(Button_Screen, self).__init__()
#         self.body_text = body_text
#         self.button_function = button_function
#         self.button_text = button_text

# class Picture_Button_Screen(BoxLayout):
#     title_text = StringProperty("Error")
#     body_text = StringProperty("Error")
#     image_source = StringProperty("Icons/Slicer wizard icons/button bkg active.png")
#     button_function = ObjectProperty(None)
#     button_text = StringProperty("OK")
    
#     def __init__(self, title_text, body_text,image_source, button_function, button_text = "OK", **kwargs):
#         super(Picture_Button_Screen, self).__init__()
#         self.title_text = title_text
#         self.body_text = body_text
#         self.image_source = image_source
#         self.button_function = button_function
#         self.button_text = button_text

# class Title_Button_Screen(BoxLayout):
#     title_text = StringProperty("Error")
#     body_text = StringProperty("Error")
#     button_function = ObjectProperty(None)
#     button_text = StringProperty("OK")
    
#     def __init__(self, title_text, body_text, button_function, button_text = "OK", **kwargs):
#         super(Title_Button_Screen, self).__init__()
#         self.title_text = title_text
#         self.body_text = body_text
#         self.button_function = button_function
#         self.button_text = button_text





# class Temperature_Wait_Screen(FloatLayout):
#     continue_function = ObjectProperty(None)
#     body_text = StringProperty("Please wait for the printer to finish preparing")
#     temperature = StringProperty("0")

#     def __init__(self, continue_function):
#         super(Temperature_Wait_Screen, self).__init__()
#         self.continue_function = continue_function
#         Clock.schedule_interval(self.wait_for_temp, 0.2)

#     def wait_for_temp(self, dt):
#         temps = roboprinter.printer_instance._printer.get_current_temperatures()
#         position_found_waiting_for_temp = False

#         #get current temperature
#         if 'tool0' in temps.keys():
#             temp = temps['tool0']['actual']
#             self.temperature = str(temp)

#             if temp >= 190:
#                 position_found_waiting_for_temp = True
#                 #go to the next screen
#                 self.continue_function()
#                 return False
        
