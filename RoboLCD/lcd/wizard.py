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
from z_offset_wizard import Z_Offset_Wizard_Finish, Z_Offset_Wizard_1_4, Z_Offset_Wizard_2_4, Z_Offset_Wizard_3_4, Z_Offset_Wizard_4_4, Z_Offset_Temperature_Wait_Screen
from printer_jog import printer_jog

class WizardButton(Button):
    pass

class PreheatWizard(BoxLayout):
    """
     #WARNING: ONLY HANDLES SINGLE EXTRUDER

    PreheatWizard orchestrates all that is necessary to guide the user to preheat the extruder for his or her 
    filament type, PLA or ABS.

    Trying a new implementation 9/20/16. This Wizard is implemented differently than the ZOffset Wizard. 
    This object will have access to the screen manager object.

    Why: Testing whether this implementation is easier to understand and more maintainable than Zoffset 
    Wizard implementation.

    What:
        The root object, RoboScreenManager, manages the ZOffset Wizard. This has led to a method, 
        .generate_zaxis_wizard(), that encapsulates all functionality necessary to render the wizard. 
        I find it hard to read and edit because it's a clump of functions defined within functions. 
        It is written in this way to accomodate the mult-screen nature of the wizard.

        I decided to implement it in this manner to keep in line with the idea that RoboScreenManager is 
        the screen manager. This means that RoboScreenManager holds all functionality as it pertains to 
        rendering new screens. The wizards need to access this functionality to render screens for each 
        step. I thought it might be more maintainable to keep that functionality defined within 
        RoboScreenManager.

        This is an experiment to see what happens when we pass RoboScreenManager into other objects. 
        As opposed to passing other objects into RoboScreenManager

    RoboScreenManager instantiates preheatwizard and then passes control over to it.
    """
    def __init__(self, roboscreenmanager, name, **kwargs):
        super(PreheatWizard, self).__init__(**kwargs)
        # first screen defined in .kv file
        self.sm = roboscreenmanager
        self.name = name #name of initial screen
        self.plastic_chosen = '' #title of second screen


    def second_screen(self, plastic_type):
        # Sets temperature
        # renders the second backbutton screen
        # Displays heating status and a button that sends you to mainscreen's printer status tab

        self.plastic_chosen = plastic_type.lower()
        if self.plastic_chosen == 'abs':
            self._preheat_abs()
        elif self.plastic_chosen == 'pla':
            self._preheat_pla()
        else:
            return

        c = self._second_screen_layout()

        self.sm._generate_backbutton_screen(name=self.name+'[1]', title=self.plastic_chosen.upper(), back_destination=self.name, content=c)

    def _second_screen_layout(self):
        layout = FloatLayout(size=(450,450))
        label = Label(
            font_size=40,
            pos_hint={'center_x': .5, 'top': 1.2}
            )
        if self.plastic_chosen == 'abs':
            t = u'Heating to 230°C'
        elif self.plastic_chosen == 'pla':
            t = u'Heating to 200°C'
        else:
            t = u'Error: plastic not registered'
        label.text = t
        b = Button(
            text='OK',
            pos_hint={'center_x': .5, 'y': 0},
            font_size=30,
            size_hint= [.5,.5],
            border=[40,40,40,40],
            background_normal="Icons/rounded_black.png"
        )
        b.bind(on_press=self._go_back_to_printer_status)

        layout.add_widget(label)
        layout.add_widget(b)
        return layout

    def _go_back_to_printer_status(self, *args, **kwargs):
        self.sm.go_back_to_main(tab='printer_status_tab')

    def _preheat_abs(self):
        # pre heat to 230 degrees celsius
        roboprinter.printer_instance._printer.set_temperature('tool0', 230.0)


    def _preheat_pla(self):
        # pre heat to 200 degrees celsius
        roboprinter.printer_instance._printer.set_temperature('tool0', 200.0)

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
        self.first_screen(**kwargs)
        self.poll_temp() #populates self.temp
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

    def first_screen(self, **kwargs):
        """
        First Screen:
            displays Start button that will open second_screen
        """
        layout = Filament_Wizard_1_5()
        layout.ids.start.fbind('on_press',self.second_screen)

        self.sm._generate_backbutton_screen(name=self.name, title=kwargs['title'], back_destination=kwargs['back_destination'], content=layout)

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
            _title = 'Filament Wizard 1/5'
        else:
            _title = 'Filament Wizard 1/4'

        self.layout2 = Filament_Wizard_2_5()
        back_destination = roboprinter.robo_screen()

        this_screen = self.sm._generate_backbutton_screen(name=self.name+'[1]', title=_title, back_destination=back_destination, content=self.layout2)
        #back_button will also stop the scheduled events: poll_temp and switch_to_third_screen
        this_screen.ids.back_button.bind(on_press=self.cancel_second_screen_events)

        # Heat up extruder
        if not self.is_printing and not self.is_paused:

            roboprinter.printer_instance._printer.set_temperature('tool0', 230.0)
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
        obj.text = str(self.temp) + "°C"

    def poll_temp(self, *args):
        # updates the temperature
        r = roboprinter.printer_instance._printer.get_current_temperatures()
        self.temp = r['tool0']['actual']
        if self.layout2 != None:
            self.layout2.update_temp(self.temp)

    def switch_to_third_screen(self, *args):
        # switches to third screen when temperature >= 229.0
        if self.temp >= 229.0:
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
        c = Filament_Wizard_3_5()
        c.ids.next_button.fbind('on_press',self.fourth_screen)
        back_destination = roboprinter.robo_screen()
        this_screen = self.sm._generate_backbutton_screen(name=self.name+'[2]', title='Filament Wizard 2/5', back_destination=back_destination, content=c)

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
            _title = 'Filament Wizard 3/5'
            back_dest = self.name+'[2]'
        else:
            _title = 'Filament Wizard 2/4'
            back_dest = self.name

        if self.extrude_event != None:
            self.end_extrude_event()
        c = Filament_Wizard_4_5()
        c.ids.next_button.fbind('on_press', self.fifth_screen)
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
            _title = 'Filament Wizard 4/5'
            back_dest = self.name+'[3]'
        else:
            _title = 'Filament Wizard 3/4'
            back_dest = self.name+'[3]'

        c = Filament_Wizard_5_5()
        c.ids.next_button.fbind('on_press', self.end_wizard)
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
            _title = 'Filament Wizard 5/5'

        else:
            _title = 'Filament Wizard 4/4'

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


class ZoffsetWizard(Widget):
    def __init__(self, robosm, back_destination, temp_pop, **kwargs):
        super(ZoffsetWizard, self).__init__()
        self.sm = robosm
        self.name = 'zoffset' #name of initial screen
        self.z_pos_init = 20.00
        self.z_pos_end = 0.0
        self.temp_pop = temp_pop
        self.first_screen(back_destination=back_destination)

        #position callback variables
        self.old_xpos = 0
        self.old_ypos = 0
        self.old_zpos = 0
        

    def first_screen(self, **kwargs):

        model = roboprinter.printer_instance._settings.get(['Model'])
        if model == "Robo R2":
            bed_temp = float(pconsole.temperature['bed'])
            Logger.info(str(bed_temp))
            if bed_temp <= 0:
                self.temp_pop.show()
                return
        c = Z_Offset_Wizard_1_4()
        c.ids.start.fbind('on_press', self.second_screen)

        self.sm._generate_backbutton_screen(name=self.name, title="Z Offset Wizard", back_destination=kwargs['back_destination'], content=c)

    def second_screen(self, *args):
        """Loading Screen
            Displays to user that Z Axis is moving """
        self._prepare_printer()

        title = "Z Offset 1/4"
        back_destination = roboprinter.robo_screen()
        name = self.name + "[1]"

        layout = Z_Offset_Wizard_2_4()
        self.counter = 0
        Clock.schedule_interval(self.position_callback, 1)

        self.sm._generate_backbutton_screen(name=name, title=title, back_destination=back_destination, content=layout)
        Logger.info("2nd Screen: RENDERED")
        # self.third_screen()

    def temperature_wait_screen(self, *args):
        title = "Waiting on Temperature"
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
        title = "Z Offset 2/4"
        name = self.name + "[2]"
        back_destination = roboprinter.robo_screen()

        Logger.info("Updated Zoffset is: " + str(self.z_pos_init))

        layout = Z_Offset_Wizard_3_4()
        layout.ids.done.fbind('on_press', self.fourth_screen)

        this_screen = self.sm._generate_backbutton_screen(title=title, name=name, back_destination=back_destination, content=layout)

        # # back_button deletes Second Screen, as back destination is first screen
        # second_screen = self.sm.get_screen(self.name)
        # delete_second = partial(self.sm.remove_widget, second_screen)
        # this_screen.ids.back_button.bind(on_press=delete_second)

    def fourth_screen(self, *args):
        """
        Z offset screen-- user interacts with the printer
        """
        title = "Z Offset 3/4"
        name = self.name + "[3]"
        back_destination = roboprinter.robo_screen()


        layout = Z_Offset_Wizard_4_4()

        self.sm._generate_backbutton_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )

        self.z_pos_end = float(self._capture_zpos()) #schema: (x_pos, y_pos, z_pos)
        self.z_pos_end = float(self._capture_zpos()) #runs twice because the first call returns the old position
        Logger.info("ZCapture: z_pos_end {}".format(self.z_pos_end))
        self.fifth_screen()


    #This is where the ZOffset Wizard finishes
    #this is also where we should make the mod for testing the new Zoffset
    def fifth_screen(self, *args):
        title = "Z Offset 4/4"
        name = self.name + "[4]"
        back_destination = roboprinter.robo_screen()

        layout = Z_Offset_Wizard_Finish()
        self.zoffset = (self.z_pos_end + 0.1) * -1
        layout.z_value = self.zoffset
        layout.ids.save.fbind('on_press', self._save_zoffset )
        layout.ids.save.fbind('on_press', self._end_wizard )

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

        #get bed dimensions
        bed_x = roboprinter.printer_instance._settings.global_get(['printerProfiles','defaultProfile', 'volume','width'])
        bed_y = roboprinter.printer_instance._settings.global_get(['printerProfiles','defaultProfile', 'volume','depth'])

        #calculate final positions
        bed_x = float(bed_x) / 2.0
        bed_y = float(bed_y) / 2.0

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

        # #get position
        # pos = pconsole.get_position()
        # zpos = int(float(pos[2]))
        #
        # #turn Zpos negative and add 0.1mm
        # zpos += 0.1
        # zpos *= -1

        #write new home offset to printer
        write_zoffset = 'M206 Z' + str(self.zoffset)
        save_to_eeprom = 'M500'
        roboprinter.printer_instance._printer.commands([write_zoffset, save_to_eeprom])
        #pconsole.home_offset['Z'] = self.zoffset


    def _end_wizard(self, *args):
        #turn off fan
        roboprinter.printer_instance._printer.commands('M106 S0')
        
        Clock.schedule_interval(self.wait_for_update, 0.5)




    ###############################



#Buttons

class Z_Offset_Wizard_Button(Button):
    pass
class Filament_Loading_Wizard_Button(Button):
    pass
class Filament_Change_Wizard_Button(Button):
    pass
