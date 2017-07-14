# coding=utf-8
from session_saver import session_saver
from scrollbox import Scroll_Box_Even_Button, Scroll_Box_Even
from pconsole import pconsole
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from .. import roboprinter
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from connection_popup import Status_Popup
from common_screens import Modal_Question_No_Title, Button_Screen


class EEPROM():
    def __init__(self, robosm):
        self.sm = robosm
        self.buttons = []
        self.eeprom_dictionary = {
            roboprinter.lang.pack['EEPROM']['Home_Offset'] : 'HOME_OFFSETS',
            roboprinter.lang.pack['EEPROM']['Probe_Offset'] : 'Z_OFFSET_EEPROM',
            roboprinter.lang.pack['EEPROM']['Filament_Settings'] : 'FILAMENT_SETTINGS',
            roboprinter.lang.pack['EEPROM']['Feed_Rates']: 'FEED_RATES',
            roboprinter.lang.pack['EEPROM']['PID_Settings'] : 'PID',
            roboprinter.lang.pack['EEPROM']['Bed_PID']: 'BPID',
            roboprinter.lang.pack['EEPROM']['Steps_Unit'] : 'STEPS_PER_UNIT',
            roboprinter.lang.pack['EEPROM']['Accelerations'] : 'ACCELERATIONS',
            roboprinter.lang.pack['EEPROM']['Max_Accelerations'] : 'MAX_ACCELERATIONS',
            roboprinter.lang.pack['EEPROM']['Advanced']: 'ADVANCED_VARIABLES',

        }
        model = roboprinter.printer_instance._settings.get(['Model'])

        if model == "Robo R2":
            #add bed PID for the R2
            self.button_order = [
                                 roboprinter.lang.pack['EEPROM']['Home_Offset'],
                                 roboprinter.lang.pack['EEPROM']['Probe_Offset'] , 
                                 roboprinter.lang.pack['EEPROM']['Steps_Unit'], 
                                 roboprinter.lang.pack['EEPROM']['Accelerations'], 
                                 roboprinter.lang.pack['EEPROM']['Max_Accelerations'],  
                                 roboprinter.lang.pack['EEPROM']['Filament_Settings'], 
                                 roboprinter.lang.pack['EEPROM']['Feed_Rates'], 
                                 roboprinter.lang.pack['EEPROM']['PID_Settings'],
                                 roboprinter.lang.pack['EEPROM']['Bed_PID'], 
                                 roboprinter.lang.pack['EEPROM']['Advanced']
                                 ]
        else:
            self.button_order = [
                                 roboprinter.lang.pack['EEPROM']['Home_Offset'],
                                 roboprinter.lang.pack['EEPROM']['Probe_Offset'] , 
                                 roboprinter.lang.pack['EEPROM']['Steps_Unit'], 
                                 roboprinter.lang.pack['EEPROM']['Accelerations'], 
                                 roboprinter.lang.pack['EEPROM']['Max_Accelerations'],  
                                 roboprinter.lang.pack['EEPROM']['Filament_Settings'], 
                                 roboprinter.lang.pack['EEPROM']['Feed_Rates'], 
                                 roboprinter.lang.pack['EEPROM']['PID_Settings'],
                                 roboprinter.lang.pack['EEPROM']['Advanced']
                                 ]
        self.load_eeprom()

        

    def load_eeprom(self):
        pconsole.query_eeprom()
        for cat in self.button_order:
            Logger.info(cat)
            temp = Scroll_Box_Even_Button(cat, self.load_values, [self.eeprom_dictionary[cat], cat])
            self.buttons.append(temp)
        temp = Scroll_Box_Even_Button(roboprinter.lang.pack['EEPROM']['Reset'], self.reset_defaults, "placeholder")
        self.buttons.append(temp)





    def reset_defaults(self, placeholder):

        #get the current screen
        back_screen = roboprinter.robosm.current

        def reset():
            roboprinter.printer_instance._printer.commands("M502")
            roboprinter.printer_instance._printer.commands("M500")
            roboprinter.printer_instance._printer.commands("M501")

            #make screen to say that the variables have been reset

            #body_text, button_function, button_text = roboprinter.lang.pack['Button_Screen']['Default_Button']
            content = Button_Screen(roboprinter.lang.pack['EEPROM']['Acknowledge_Reset']['Body_Text'],
                                    self.sm.go_back_to_main,
                                    button_text = roboprinter.lang.pack['EEPROM']['Acknowledge_Reset']['Button'])

            #make screen
            roboprinter.robosm._generate_backbutton_screen(name='ack_reset_eeprom', 
                                                           title = roboprinter.lang.pack['EEPROM']['Acknowledge_Reset']['Title'] , 
                                                           back_destination=back_screen, 
                                                           content=content)

        def cancel():
            roboprinter.robosm.current = back_screen

        #make the confirmation screen
        #body_text, option1_text, option2_text, option1_function, option2_function
        content = Modal_Question_No_Title(roboprinter.lang.pack['EEPROM']['Reset_Confirmation']['Body_Text'],
                                          roboprinter.lang.pack['EEPROM']['Reset_Confirmation']['positive'],
                                          roboprinter.lang.pack['EEPROM']['Reset_Confirmation']['negative'],
                                          reset,
                                          cancel) 

        #make screen
        roboprinter.robosm._generate_backbutton_screen(name='reset_eeprom', 
                                                       title = roboprinter.lang.pack['EEPROM']['Reset_Confirmation']['Title'] , 
                                                       back_destination=back_screen, 
                                                       content=content)       
        

    def load_values(self, catagory):
        back_destination = self.sm.current
        acceptable_catagories = {'HOME_OFFSETS': 'home offset',
                                 'Z_OFFSET_EEPROM': 'z offset',
                                 'FILAMENT_SETTINGS': 'filament settings',
                                 'FEED_RATES' : 'max feed rate',
                                 'PID': 'PID',
                                 'BPID': "BPID",
                                 'STEPS_PER_UNIT': 'steps per unit',
                                 'ACCELERATIONS': 'accelerations',
                                 'MAX_ACCELERATIONS':'max acceleration',
                                 'ADVANCED_VARIABLES': 'advanced variables'}

        buttons = []
        if catagory[0] in acceptable_catagories:
            for value in pconsole.eeprom[acceptable_catagories[catagory[0]]]:
                button_value = value + ": " + str(pconsole.eeprom[acceptable_catagories[catagory[0]]][value])
                temp = Scroll_Box_Even_Button(button_value, self.change_value, [catagory[0], value])
                buttons.append(temp)

        layout = Scroll_Box_Even(buttons)

        self.sm._generate_backbutton_screen(name=catagory[0], title=catagory[1], back_destination=back_destination, content=layout)


    def change_value(self, item):
        # item[0] = catagory to change
        # item[1] = value to change
        back_destination = self.sm.current
        acceptable_catagories = {'HOME_OFFSETS': 'M206',
                                 'Z_OFFSET_EEPROM': 'M851',
                                 'FILAMENT_SETTINGS': 'M200',
                                 'FEED_RATES' : 'M203',
                                 'PID': 'M301',
                                 'BPID': 'M304',
                                 'STEPS_PER_UNIT': 'M92',
                                 'ACCELERATIONS': 'M204',
                                 'MAX_ACCELERATIONS': 'M201',
                                 'ADVANCED_VARIABLES': 'M205'}
        values = {'HOME_OFFSETS': pconsole.eeprom['home offset'],
                                 'Z_OFFSET_EEPROM': pconsole.eeprom['z offset'],
                                 'FILAMENT_SETTINGS': pconsole.eeprom['filament settings'],
                                 'FEED_RATES' : pconsole.eeprom['max feed rate'],
                                 'PID': pconsole.eeprom['PID'],
                                 'BPID': pconsole.eeprom['BPID'],
                                 'STEPS_PER_UNIT': pconsole.eeprom['steps per unit'],
                                 'ACCELERATIONS': pconsole.eeprom['accelerations'],
                                 'MAX_ACCELERATIONS': pconsole.eeprom['max acceleration'],
                                 'ADVANCED_VARIABLES': pconsole.eeprom['advanced variables']}


        value = values[item[0]][item[1]]
        self.command = acceptable_catagories[item[0]] + " " + item[1]
        layout = Change_Value(self.command, value, str(item[1]))
        
        self.sm._generate_backbutton_screen(name = str(item[1]), title = str(item[1]), back_destination = 'eeprom_viewer', content= layout)


    # def apply_callback(self, dt):
    #     if self.screen != self.sm.current:
    #         Logger.info(self.command + str(self.layout.value))
    #         roboprinter.printer_instance._printer.commands(self.command + str(self.layout.value))
    #         roboprinter.printer_instance._printer.commands("M500")
    #         pconsole.query_eeprom()
    #         return False


class Change_Value(BoxLayout):
    name = StringProperty("ERROR")
    number = StringProperty("999")
    value = NumericProperty(999)

    change_amount_value = [0.01, 0.1, 1, 10, 100]
    change_value = 2
    button_size = [200,200]

    def __init__(self, command, value, name):
        super(Change_Value, self).__init__()
        self.command = command
        self.value = value
        self.name = name
        self.number = str(value)

    def change_amount(self):
        self.change_value += 1

        if self.change_value > 4:
            self.change_value = 0

        self.ids.change_text.text = "[size=60]{}".format(self.change_amount_value[self.change_value]) 

    def add_button(self, value):
        self.value += value

        self.number = str(self.value)

    def go_back(self):
        roboprinter.printer_instance._printer.commands(self.command + str(self.value))
        roboprinter.printer_instance._printer.commands("M500")
        pconsole.query_eeprom()
        ep = Status_Popup(roboprinter.lang.pack['EEPROM']['Error_Title'], roboprinter.lang.pack['EEPROM']['Error_Body'])
        ep.show()





