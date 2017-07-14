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
from common_screens import Picture_Button_Screen, Wait_Screen, Override_Layout,Picture_Button_Screen_Body, Button_Screen
from Language import lang

class ZoffsetWizard(object):
    def __init__(self, robosm, back_destination, **kwargs):
        super(ZoffsetWizard, self).__init__()
        self.sm = robosm
        self.name = 'zoffset' #name of initial screen
        self.z_pos_init = 20.00
        self.z_pos_end = 0.0
        self.first_screen(back_destination=back_destination)

        #position callback variables
        self.old_xpos = 0
        self.old_ypos = 0
        self.old_zpos = 0
        

    def first_screen(self, **kwargs):

        model = roboprinter.printer_instance._settings.get(['Model'])
        #body_text,image_source, button_function, button_text = roboprinter.lang.pack['Button_Screen']['Default_Button']
        c = Button_Screen(lang.pack['ZOffset_Wizard']['Wizard_Description'],
                          self.second_screen,
                          button_text=lang.pack['ZOffset_Wizard']['Start'])

        self.sm._generate_backbutton_screen(name=self.name, title=roboprinter.lang.pack['ZOffset_Wizard']['Welcome'] , back_destination=kwargs['back_destination'], content=c)

    def second_screen(self, *args):
        """Loading Screen
            Displays to user that Z Axis is moving """
        self._prepare_printer()

        title = lang.pack['ZOffset_Wizard']['Z_14']
        back_destination = roboprinter.robo_screen()
        name = self.name + "[1]"

        layout = Wait_Screen(self.check_temp_and_change_screen, '',lang.pack['ZOffset_Wizard']['Auto_Next'])

        self.sm._generate_backbutton_screen(name=name, title=title, back_destination=back_destination, content=layout)
        Logger.info("2nd Screen: RENDERED")

    def check_temp_and_change_screen(self):
        temps = roboprinter.printer_instance._printer.get_current_temperatures()

        #find the temperature
        if 'tool0' in temps:
            extruder_one_temp = temps['tool0']['actual']

        if extruder_one_temp < 100:
            self.third_screen()
        else:
            self.temperature_wait_screen()

    def temperature_wait_screen(self, *args):
        title = roboprinter.lang.pack['ZOffset_Wizard']['Wait']
        name = self.name + "temperature"
        back_destination = roboprinter.robo_screen()

        layout = Z_Offset_Temperature_Wait_Screen(self.third_screen)

        self.sm._generate_backbutton_screen(name = name,
                                            title = title,
                                            back_destination = back_destination,
                                            content = layout)
        Logger.info("Temperature Wait Screen Activated")



    def third_screen(self, *args):

        #turn off fan
        roboprinter.printer_instance._printer.commands('M106 S0')
        """
        Instructions screen
        """
        title = roboprinter.lang.pack['ZOffset_Wizard']['Z_24']
        name = self.name + "[2]"
        back_destination = roboprinter.robo_screen()

        Logger.info("Updated Zoffset is: " + str(self.z_pos_init))

        layout = Z_Offset_Adjuster()
        layout.ids.done.fbind('on_press', self.fifth_screen)

        self.sm._generate_backbutton_screen(title=title, name=name, back_destination=back_destination, content=layout)


    #This is where the ZOffset Wizard finishes
    #this is also where we should make the mod for testing the new Zoffset
    def fifth_screen(self, *args):

        self.z_pos_end = float(self._capture_zpos()) #schema: (x_pos, y_pos, z_pos)
        self.z_pos_end = float(self._capture_zpos()) #runs twice because the first call returns the old position
        Logger.info("ZCapture: z_pos_end {}".format(self.z_pos_end))
        self.zoffset = (self.z_pos_end) * -1.00


        title = roboprinter.lang.pack['ZOffset_Wizard']['Z_44']
        name = self.name + "[3]"
        back_destination = roboprinter.robo_screen()

        #title_text, body_text,image_source, button_function, button_text = roboprinter.lang.pack['Button_Screen']['Default_Button']
        layout = Picture_Button_Screen('[size=40][color=#69B3E7]' + lang.pack['ZOffset_Wizard']['Finish_Title'] + '[/color][/size]',
                                       '[size=30]' + lang.pack['ZOffset_Wizard']['Finish_Body1'] + ' {} '.format(self.zoffset) + lang.pack['ZOffset_Wizard']['Finish_Body2'],
                                       'Icons/Manual_Control/check_icon.png',
                                       self._end_wizard,
                                       button_text="[size=30]" + lang.pack['ZOffset_Wizard']['Save']
                                        )

        
        

        self.sm._generate_backbutton_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )

    
    def wait_for_update(self, dt):
        pconsole.query_eeprom()
        if pconsole.home_offset['Z'] != 0:
            roboprinter.printer_instance._printer.commands('G28')
            self.sm.go_back_to_main()
            return False

    #####Helper Functions#######
    def _prepare_printer(self):
        # Prepare printer for zoffset configuration
        #jog the Z Axis Down to prevent any bed interference
        jogger = {'z': 160}
        printer_jog.jog(desired=jogger, speed=1500, relative=True)
        #kill the extruder
        roboprinter.printer_instance._printer.commands('M104 S0')
        roboprinter.printer_instance._printer.commands('M140 S0')
        roboprinter.printer_instance._printer.commands('M106 S255')
        roboprinter.printer_instance._printer.commands('M502')
        roboprinter.printer_instance._printer.commands('M500')
        roboprinter.printer_instance._printer.commands('G28')

        bed_x = 0
        bed_y = 0

        roboprinter.printer_instance._printer.commands('G1 X' + str(bed_x) + ' Y' + str(bed_y) +' F10000')
        roboprinter.printer_instance._printer.commands('G1 Z20 F1500')

    def position_callback(self, dt):
        temps = roboprinter.printer_instance._printer.get_current_temperatures()
        pos = pconsole.get_position()
        if pos != False:
            xpos = int(float(pos[0]))
            ypos = int(float(pos[1]))
            zpos = int(float(pos[2]))
    
            extruder_one_temp = 105
    
            #find the temperature
            if 'tool0' in temps.keys():
                extruder_one_temp = temps['tool0']['actual']
    
            Logger.info("Counter is at: " + str(self.counter))
            #check the extruder physical position
            if self.counter > 25 and  xpos == self.old_xpos and ypos == self.old_ypos and zpos == self.old_zpos:
                if self.sm.current == 'zoffset[1]':
                    if extruder_one_temp < 100:
                        Logger.info('Succesfully found position')
                        self.third_screen()
                        return False
                    else:
                        self.temperature_wait_screen()
                        return False
                else:
                    Logger.info('User went to a different screen Unscheduling self.')
                    #turn off fan
                    roboprinter.printer_instance._printer.commands('M106 S0')
                    return False
    
            #if finding the position fails it will wait 30 seconds and continue
            self.counter += 1
            if self.counter > 60:
                if self.sm.current == 'zoffset[1]':
                    Logger.info('could not find position, but continuing anyway')
                    if extruder_one_temp < 100:
                        self.third_screen()
                        return False
                    else:
                        self.temperature_wait_screen()
                        return False
                else:
                    Logger.info('User went to a different screen Unscheduling self.')
                    #turn off fan
                    roboprinter.printer_instance._printer.commands('M106 S0')
                    return False
    
            #position tracking
            self.old_xpos = xpos
            self.old_ypos = ypos
            self.old_zpos = zpos


    def _capture_zpos(self):
        """gets position from pconsole. :returns: integer"""
        Logger.info("ZCapture: Init")
        p = pconsole.get_position()
        while p == False:
            p = pconsole.get_position()
        
        Logger.info("ZCapture: {}".format(p))
        return p[2]

    def _save_zoffset(self, *args):
        #turn off fan
        roboprinter.printer_instance._printer.commands('M106 S0')
        #write new home offset to printer
        write_zoffset = 'M206 Z' + str(self.zoffset)
        save_to_eeprom = 'M500'
        roboprinter.printer_instance._printer.commands([write_zoffset, save_to_eeprom])
        #pconsole.home_offset['Z'] = self.zoffset


    def _end_wizard(self, *args):
        #turn off fan
        self._save_zoffset()
        roboprinter.printer_instance._printer.commands('M106 S0')
        
        Clock.schedule_interval(self.wait_for_update, 0.5)

    

class Z_Offset_Adjuster(BoxLayout):
    i_toggle_mm = ['Icons/Manual_Control/increments_3_1.png', 'Icons/Manual_Control/increments_3_2.png', 'Icons/Manual_Control/increments_3_3.png']
    s_toggle_mm = [roboprinter.lang.pack['ZOffset_Wizard']['zero_five'],roboprinter.lang.pack['ZOffset_Wizard']['one_zero'], roboprinter.lang.pack['ZOffset_Wizard']['two_zero']]
    f_toggle_mm = [0.05, 0.1, 0.2]
    toggle_mm = 1
    def toggle_mm_z(self):
        self.toggle_mm += 1
        if self.toggle_mm > 2:
            self.toggle_mm = 0

        Logger.info(self.s_toggle_mm[self.toggle_mm])
        self.ids.toggle_label.text = self.s_toggle_mm[self.toggle_mm]
        self.ids.toggle_icon.source = self.i_toggle_mm[self.toggle_mm]
    def _jog(self, direction):
        # determine increment value
        increment = direction * self.f_toggle_mm[self.toggle_mm]
        jogger = {'z': increment}
        printer_jog.jog(desired=jogger, speed=1500, relative=True)

class Z_Offset_Temperature_Wait_Screen(FloatLayout):

    body_text = StringProperty(roboprinter.lang.pack['ZOffset_Wizard']['Cooldown'])
    temperature = StringProperty("999")
    bed_temp = StringProperty("999")


    def __init__(self, callback):
        super(Z_Offset_Temperature_Wait_Screen, self).__init__()
        #setup callback
        model = roboprinter.printer_instance._settings.get(['Model'])
        if model == "Robo R2": 
            self.body_text = roboprinter.lang.pack['ZOffset_Wizard']['Cooldown']
            Clock.schedule_interval(self.temp_callback_R2, 0.5)
        else:
            Clock.schedule_interval(self.temperature_callback, 0.5)

        self.callback = callback
        

    def temperature_callback(self,dt):
        temps = roboprinter.printer_instance._printer.get_current_temperatures()
        position_found_waiting_for_temp = False

        #get current temperature
        if 'tool0' in temps.keys():
            temp = temps['tool0']['actual']
            self.temperature = str(temp)

            if temp < 100:
                position_found_waiting_for_temp = True
                #go to the next screen
                self.callback()
                return False
        

    def temp_callback_R2(self, dt):
        temps = roboprinter.printer_instance._printer.get_current_temperatures()
        position_found_waiting_for_temp = False
        bed = 100
        #get current temperature
        if 'tool0' in temps.keys():
            temp = temps['tool0']['actual']
            self.temperature = str(temp)

        if 'bed' in temps.keys():
            bed = temps['bed']['actual']
            self.bed_temp = str(bed)

            if temp < 100 and bed < 60:
                position_found_waiting_for_temp = True
                #go to the next screen
                self.callback()
                return False



