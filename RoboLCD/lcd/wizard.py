# -*- coding: utf-8 -*-
from kivy.uix.button import Button
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
from .. import roboprinter
from functools import partial
from kivy.logger import Logger
from kivy.clock import Clock
from pconsole import pconsole
import thread
from Filament_Wizard import Filament_Wizard_Finish, Filament_Wizard_1_5, Filament_Wizard_2_5, Filament_Wizard_3_5, Filament_Wizard_4_5, Filament_Wizard_5_5
from printer_jog import printer_jog
from Preheat_Wizard import Preheat_Overseer

class FilamentWizard(Widget):
    """ """
    temp = NumericProperty(0.0)
    layout2 = None
    extrude_event = None
    def __init__(self, loader_changer, robosm, name,  **kwargs):
        super(FilamentWizard, self).__init__(**kwargs)
        # first screen defined in .kv file
        self.sm = robosm
        self.name = name #name of initial screen
        self.load_or_change = loader_changer
        #check if the printer is printing
        current_data = roboprinter.printer_instance._printer.get_current_data()
        self.is_printing = current_data['state']['flags']['printing']
        self.is_paused = current_data['state']['flags']['paused']
        self.tmp_event = None
        self.s_event = None
        self.E_Position = None

        if self.is_printing or self.is_paused:

            #get the E Position
            pos = pconsole.get_position()
            while not pos:
                pos = pconsole.get_position()

            self.E_Position = pos[3]

        self.first_screen(**kwargs)
        self.poll_temp() #populates self.temp

    def first_screen(self, **kwargs):
        """
        First Screen:
            displays Start button that will open second_screen
        """
        
        if self.is_printing or self.is_paused:
            layout = Filament_Wizard_1_5(self.second_screen)
        else:
            layout = Filament_Wizard_1_5(self.choose_material)
           
        self.sm._generate_backbutton_screen(name=self.name, title=kwargs['title'], back_destination=kwargs['back_destination'], content=layout)

    def choose_material(self, *args):
        
        Preheat_Overseer(end_point=self.collect_heat_settings,
                         name='preheat_wizard',
                         title=roboprinter.lang.pack['Utilities']['Preheat'],
                         back_destination=self.name)

    def collect_heat_settings(self, extruder, bed):
        self.print_temperature = extruder
        self.print_bed_temperature = bed
        self.second_screen()

    def second_screen(self, *args):
        """
        the Heating Screen:
            Sets the temperature of the extruder to 230
            Display heating status to user
            Open third screen when temperature hits 230
        """
        #display heating status to user

        #end the event before starting it again
        if self.extrude_event != None:
            self.end_extrude_event()


        if self.load_or_change == 'CHANGE':
            _title = roboprinter.lang.pack['Filament_Wizard']['Title_15']
        else:
            _title = roboprinter.lang.pack['Filament_Wizard']['Title_14']

        # Heat up extruder
        if not self.is_printing and not self.is_paused:
            self.layout2 = Filament_Wizard_2_5(self.print_temperature)
            back_destination = 'preheat_wizard'
    
            this_screen = self.sm._generate_backbutton_screen(name=self.name+'[1]', title=_title, back_destination=back_destination, content=self.layout2)
            #back_button will also stop the scheduled events: poll_temp and switch_to_third_screen
            this_screen.ids.back_button.bind(on_press=self.cancel_second_screen_events)

            roboprinter.printer_instance._printer.set_temperature('tool0', self.print_temperature)
            self.tmp_event = Clock.schedule_interval(self.poll_temp, .5) #stored so we can stop them later
            self.s_event = Clock.schedule_interval(self.switch_to_third_screen, .75) #stored so we can stop them later
        else:
            if self.load_or_change == 'CHANGE':
                self.third_screen()
            
            elif self.load_or_change == 'LOAD':
                self.fourth_screen()
                
    ###Second screen helper functions ###
    def cancel_second_screen_events(self, *args):
        if self.tmp_event != None and self.s_event != None:
            self.tmp_event.cancel()
            self.s_event.cancel()

    def update_temp_label(self, obj, *args):
        # updates the temperature for the user's view
        obj.text = str(self.temp) + roboprinter.lang.pack['Filament_Wizard']['Celsius_Alone']

    def poll_temp(self, *args):
        # updates the temperature
        r = roboprinter.printer_instance._printer.get_current_temperatures()
        self.temp = r['tool0']['actual']
        if self.layout2 != None:
            self.layout2.update_temp(self.temp)

    def switch_to_third_screen(self, *args):
        # switches to third screen when temperature is set
        if self.temp >= self.print_temperature:
            if self.load_or_change == 'CHANGE':
                self.third_screen()
                # clock event no longer needed
                self.cancel_second_screen_events()
            elif self.load_or_change == 'LOAD':
                self.fourth_screen()
                # clock event no longer needed
                self.cancel_second_screen_events()
    #####################################

    def third_screen(self):
        """
        Pull filament Screen:
            Display instructions to user -- Pull out filament
            Display button that will open fourth screen
        """
        # roboprinter.printer_instance._printer.jog('e', -130.00)
        c = Filament_Wizard_3_5(self.fourth_screen)
        back_destination = roboprinter.robo_screen()
        this_screen = self.sm._generate_backbutton_screen(name=self.name+'[2]', title=roboprinter.lang.pack['Filament_Wizard']['Title_25'], back_destination=back_destination, content=c)

        #end the event before starting it again
        if self.extrude_event != None:
            self.end_extrude_event()
        self.extrude_event = Clock.schedule_interval(self.retract, 1)


        # back_button deletes Second Screen, as back destination is first screen
        # second_screen = self.sm.get_screen(self.name+'[1]')
        # delete_second = partial(self.sm.remove_widget, second_screen)
        # this_screen.ids.back_button.bind(on_press=delete_second)

    def fourth_screen(self, *args):
        """
        Load filament screen:
            Display instructions to user -- Load filament
            Display button that will open fifth screen
        """

        if self.load_or_change == 'CHANGE':
            _title = roboprinter.lang.pack['Filament_Wizard']['Title_35']
            back_dest = self.name+'[2]'
        else:
            _title = roboprinter.lang.pack['Filament_Wizard']['Title_24']
            back_dest = self.name

        if self.extrude_event != None:
            self.end_extrude_event()
        c = Filament_Wizard_4_5(self.fifth_screen)
        back_destination = roboprinter.robo_screen()
        self.sm._generate_backbutton_screen(name=self.name+'[3]', title=_title, back_destination=back_destination, content=c)

    def fifth_screen(self, *args):
        """
        Final screen / Confirm successful load:
            Extrude filament
            Display instruction to user -- Press okay when you see plastic extruding
            Display button that will move_to_main() AND stop extruding filament
        """
        if self.load_or_change == 'CHANGE':
            _title = roboprinter.lang.pack['Filament_Wizard']['Title_45']
            back_dest = self.name+'[3]'
        else:
            _title = roboprinter.lang.pack['Filament_Wizard']['Title_34']
            back_dest = self.name+'[3]'

        c = Filament_Wizard_5_5(self.end_wizard)
        back_destination = roboprinter.robo_screen()
        self.sm._generate_backbutton_screen(name=self.name+'[4]', title=_title, back_destination=back_destination, content=c)

        #end the event before starting it again
        if self.extrude_event != None:
            self.end_extrude_event()
        self.extrude_event = Clock.schedule_interval(self.extrude, 1)

    def extrude(self, *args):
        # wrapper that can accept the data pushed to it by Clock.schedule_interval when called
        if self.sm.current == 'filamentwizard[4]':
            roboprinter.printer_instance._printer.extrude(5.0)
        else:
            self.end_extrude_event()
            Logger.info("Canceling due to Screen change")
    def retract(self, *args):
        if self.sm.current == 'filamentwizard[2]':
            roboprinter.printer_instance._printer.extrude(-5.0)
        else:
            self.end_extrude_event()
            Logger.info("Canceling due to Screen change")

    def retract_after_session(self, *args):
        roboprinter.printer_instance._printer.extrude(-10.0)

    def end_extrude_event(self, *args):
        self.extrude_event.cancel()

    def end_wizard(self, *args):

        

        
        self.extrude_event.cancel()
        c = Filament_Wizard_Finish()

        if self.load_or_change == 'CHANGE':
            _title = roboprinter.lang.pack['Filament_Wizard']['Title_55']

        else:
            _title = roboprinter.lang.pack['Filament_Wizard']['Title_44']

        #set the E position back to it's original position
        if self.E_Position != None:
            roboprinter.printer_instance._printer.commands("G92 E" + str(self.E_Position))        

        #if it is printing or paused don't cool down
        if not self.is_printing and not self.is_paused:
            #retract 10mm
            self.retract_after_session()

            #cooldown
            roboprinter.printer_instance._printer.commands('M104 S0')
            roboprinter.printer_instance._printer.commands('M140 S0')

        back_destination = roboprinter.robo_screen()
        self.sm._generate_backbutton_screen(name=self.name+'[5]', title=_title, back_destination=back_destination, content=c)


    def _generate_layout(self, l_text, btn_text, f):
        """
        Layouts are similar in fashion: Text and Call to Action button
        creates layout with text and button and  binds f to button
        """
        layout = BoxLayout(orientation='vertical')
        btn = Button(text=btn_text, font_size=30)
        l = Label(text=l_text, font_size=30)
        btn.bind(on_press=f)
        layout.add_widget(l)
        layout.add_widget(btn)
        return layout
