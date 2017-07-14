# -*- coding: utf-8 -*-
from kivy.uix.button import Button
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
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
from printer_jog import printer_jog
from scrollbox import Scroll_Box_Even
from Language import lang
from common_screens import Modal_Question_No_Title, KeyboardInput, Keypad
from session_saver import session_saver
from connection_popup import Info_Popup, Error_Popup

#This class oversees all of the preheat screens. All callbacks eventually lead back here.
class Preheat_Overseer(object):

    def __init__(self, end_point=None,**kwargs):
        self.model = roboprinter.printer_instance._settings.get(['Model'])
        self.settings = roboprinter.printer_instance._settings
        self._name = kwargs['name']
        self.title = kwargs['title']
        self.back_destination = kwargs['back_destination']
        self.end_point = end_point
        self.show_preheat_selection_screen(**kwargs)

    #This will create the preheat selection screen. 
    def show_preheat_selection_screen(self,*args, **kwargs):
        acceptable_selections = self.settings.get(['Temp_Preset'])
        #populate with some default values if acceptable_selections == 0
        Logger.info("selection count = " + str(len(acceptable_selections)))
        if len(acceptable_selections) == 0:
            Logger.info("Returning to Defaults")
            self.add_defaults()
            
        

        self.c = Preheat(self.switch_to_preheat)

        roboprinter.robosm._generate_backbutton_screen(name=self._name, 
                                                       title=self.title , 
                                                       back_destination=self.back_destination, 
                                                       content=self.c, 
                                                       cta=self.create_preset, 
                                                       icon='Icons/Preheat/add_preset.png',
                                                       )

    def add_defaults(self):
        default_selections = {
                                'Robo PLA': 
                                {
                                    'Extruder1': 190,
                                    'Bed': 60
                                },
                                'Robo ABS':
                                {
                                    'Extruder1': 230,
                                    'Bed': 100
                                }
        }

        #save default selection
        self.settings.set(['Temp_Preset'], default_selections)
        self.settings.save()

    #This is a callback for the preheat selection screen. This gets called when a user clicks on a preheat option
    def switch_to_preheat(self, option):
        #get all temperature presets
        acceptable_selections = self.settings.get(['Temp_Preset'])

        #make sure the selection is a valid selection from the dictionary
        if option in acceptable_selections:
            #make the options parameters
            title = option
            temp_ext1 = acceptable_selections[option]['Extruder1']
            temp_bed = acceptable_selections[option]['Bed']
            body_text = '[size=40][color=#69B3E7][font=fonts/S-Core - CoreSansD55Bold.otf][b]' + title + "[/color][/b][/font]\n[size=30]" + lang.pack['Preheat']['Extruder'] + str(temp_ext1) + lang.pack['Preheat']['Celsius_Alone'] + "\n" + lang.pack['Preheat']['Bed'] + str(temp_bed) + lang.pack['Preheat']['Celsius_Alone']
            
            #alter the view for the model:
            if self.model == "Robo C2":
                body_text = '[size=40][color=#69B3E7][font=fonts/S-Core - CoreSansD55Bold.otf][b]' + title + "[/color][/b][/font]\n[size=30]" + lang.pack['Preheat']['Extruder'] + str(temp_ext1) + lang.pack['Preheat']['Celsius_Alone']


            #these options lead to callbacks that will either set the temperature or edit the option
            option1 = partial(self.set_temp, extruder = temp_ext1, bed = temp_bed)
            option2 = partial(self.edit, option = title)
    
            option1_text = lang.pack['Preheat']['Preheat']
            if self.end_point != None:
               option1_text = lang.pack['Preheat']['Select']
            #body_text, option1_text, option2_text, option1_function, option2_function
            modal_screen = Modal_Question_No_Title(body_text, option1_text, lang.pack['Preheat']['Edit'], option1, option2)
    
            #make screen
            roboprinter.robosm._generate_backbutton_screen(name='view_preheat', 
                                                           title = lang.pack['Preheat']['Edit_Preset']['Select_Preset'] , 
                                                           back_destination=self._name, 
                                                           content=modal_screen,
                                                           backbutton_callback=self.c.update)
    #This will either set the temp or execute the callback to a custon end point
    def set_temp(self, extruder, bed):
        #Go back to the printer status tab, or call a custom callback to go to a new screen
        if self.end_point == None:
            roboprinter.printer_instance._printer.set_temperature('tool0', float(extruder))
            roboprinter.printer_instance._printer.set_temperature('bed', float(bed))
            Logger.info("Set temperature to extruder: " + str(extruder) + " set temp to bed: " + str(bed))
            session_saver.saved['Move_Tools']('TEMP')
            roboprinter.robosm.go_back_to_main('printer_status_tab')
        else:
            self.end_point(extruder, bed)


    #This sets up the screen for editing an option
    def edit(self, option):
        Logger.info("option: " + str(option))
        content = Option_View(option=option,callback = self.switch_to_preheat, delete_callback = self.show_preheat_selection_screen, back_destination = roboprinter.robosm.current)
        roboprinter.robosm._generate_backbutton_screen(name='edit_preheat', title = lang.pack['Preheat']['Edit_Preset']['Title'] , back_destination=roboprinter.robosm.current, content=content)

    #This sets up the screen to create a custom preset
    def create_preset(self):
        Logger.info("Create new preset")
        content = Option_View(callback = self.show_preheat_selection_screen)
        roboprinter.robosm._generate_backbutton_screen(name='edit_preheat', title = lang.pack['Preheat']['Edit_Preset']['Add_Material'] , back_destination=roboprinter.robosm.current, content=content)


#This class shows all Preheat options
class Preheat(Scroll_Box_Even):
    def __init__(self,callback):
        self.model = roboprinter.printer_instance._settings.get(['Model'])
        self.settings = roboprinter.printer_instance._settings
        self.callback = callback
        self.make_buttons()
        super(Preheat, self).__init__(self.buttons)

    #This will create the button list for the SBE 
    def make_buttons(self):
        self.buttons = []
        preheat_settings = self.settings.get(['Temp_Preset'])

        #Order the preset list
        ordered_presets = []
        for temp_preset in preheat_settings:
            ordered_presets.append(temp_preset)
        ordered_presets = sorted(ordered_presets, key=str.lower)

        for temp_preset in ordered_presets:
            title = str(temp_preset)
            body_text = lang.pack['Preheat']['Preheat_Head'] + str(preheat_settings[temp_preset]['Extruder1']) + lang.pack['Preheat']['And_Bed'] + str(preheat_settings[temp_preset]['Bed']) + lang.pack['Preheat']['Celsius_Alone']
            
            #alter the view for the model:
            if self.model == "Robo C2":
                body_text = lang.pack['Preheat']['Preheat_Head'] + str(preheat_settings[temp_preset]['Extruder1']) 


            temp_button = Preheat_Button(title, body_text, self.callback)
            self.buttons.append(temp_button)
    #This is called to update the screen with the most current preheat list
    def update(self):
        self.make_buttons()
        #populate buttons is a function in SBE
        self.populate_buttons()


#This class is the view for the preheat options
class Option_View(BoxLayout):
    button_padding = ObjectProperty([0,0,0,0])
    button_spacing = ObjectProperty(50)

    def __init__(self, option=None,callback = None, delete_callback = None, back_destination = None, **kwargs):
        super(Option_View, self).__init__()
        self.model = roboprinter.printer_instance._settings.get(['Model'])
        self.settings = roboprinter.printer_instance._settings
        self.back_destination = back_destination
        self.callback = callback
        self.delete_callback=delete_callback
        self.confirm_overwrite = False

        if option != None:
            #populate fields and make buttons
            #add save and delete button
            self.populate_option(option)
            self.original_option = option
        else:
            #populate fields with default values
            #add only a save button
            self.populate_default()
            self.original_option = None

    #This populates a known option with preset variables
    def populate_option(self, option):
        #get presets
        preset_options = self.settings.get(['Temp_Preset'])

        self.selected_option = {option: preset_options[option]}
        Logger.info("Selected Preset is: " + str(self.selected_option))

        #make options
        name = next(iter(self.selected_option))
        name_title = lang.pack['Preheat']['Edit_Preset']['Name'] + name
        name_body = lang.pack['Preheat']['Edit_Preset']['Set_Name']

        ext1 = self.selected_option[name]['Extruder1']
        ext1_title = lang.pack['Preheat']['Edit_Preset']['Ext'] + str(ext1) + lang.pack['Preheat']['Celsius_Alone']
        ext1_body = lang.pack['Preheat']['Edit_Preset']['Ext_Body']

        bed = self.selected_option[name]['Bed']
        bed_title = lang.pack['Preheat']['Edit_Preset']['Bed'] + str(bed) + lang.pack['Preheat']['Celsius_Alone']
        bed_body = lang.pack['Preheat']['Edit_Preset']['Bed_Body']

        #make buttons with the options
        self.name_button = Preheat_Button(name_title, name_body, self.show_keyboard)
        self.ext1_button = Preheat_Button(ext1_title, ext1_body, self.show_keypad)

        #if we are a C2 add a label
        if self.model == "Robo R2":
            self.bed_button =  Preheat_Button(bed_title, bed_body, self.show_keypad)
        else:
            self.bed_button = Preheat_Button('','',self.placeholder)

        #make save and delete buttons

        save = Simple_Button(lang.pack['Preheat']['Edit_Preset']['Save'], "Icons/blue_button_style.png", self.save_preset)
        delete = Simple_Button(lang.pack['Preheat']['Edit_Preset']['Delete'], "Icons/red_button_style.png", self.delete_preset)

        #push buttons to the grid
        button_list = [self.name_button, self.ext1_button, self.bed_button]

        for button in button_list:
            self.ids.button_box.add_widget(button)

        #push save and delete to grid
        button_list = [save, delete]

        for button in button_list:
            self.ids.modal_box.add_widget(button)

        #adjust button padding for two buttons
        self.button_padding = [50,15,50,15]
        self.button_spacing = 50

    #This populates a default option so we can save it later
    def populate_default(self):
        #make options
        self.selected_option = {lang.pack['Preheat']['Edit_Preset']['Name_Default'] : {

                                    'Extruder1': 0,
                                    'Bed': 0
                                    }
                                }
        name_title = lang.pack['Preheat']['Edit_Preset']['Name'] + lang.pack['Preheat']['Edit_Preset']['Name_Default']
        name_body = lang.pack['Preheat']['Edit_Preset']['Set_Name']

        ext1 = 0
        ext1_title = lang.pack['Preheat']['Edit_Preset']['Ext'] + str(ext1) + lang.pack['Preheat']['Celsius_Alone']
        ext1_body = lang.pack['Preheat']['Edit_Preset']['Ext_Body']

        bed = 0
        bed_title = lang.pack['Preheat']['Edit_Preset']['Bed'] + str(bed) + lang.pack['Preheat']['Celsius_Alone']
        bed_body = lang.pack['Preheat']['Edit_Preset']['Bed_Body']

         #make buttons with the options
        self.name_button = Preheat_Button(name_title, name_body, self.show_keyboard)
        self.ext1_button = Preheat_Button(ext1_title, ext1_body, self.show_keypad)

        #if we are a C2 add a label
        if self.model == "Robo R2":
            self.bed_button =  Preheat_Button(bed_title, bed_body, self.show_keypad)
        else:
            self.bed_button = Preheat_Button('','',self.placeholder)
        

        #make save button
        save = Simple_Button(lang.pack['Preheat']['Edit_Preset']['Save'], "Icons/blue_button_style.png", self.save_preset)
        #push buttons to the grid
        button_list = [self.name_button, self.ext1_button, self.bed_button]

        for button in button_list:
            self.ids.button_box.add_widget(button)

        self.ids.modal_box.add_widget(save)

        #adjust button padding for one buttons
        self.button_padding = [200,15,200,15]
        self.button_spacing = 0


    def placeholder(self, *args, **kwargs):
        Logger.info("Button Works")

    def show_keyboard(self, name):
        #keyboard_callback = None, default_text = '', name = 'keyboard_screen', title=lang.pack['Keyboard']['Default_Title']
        KeyboardInput(keyboard_callback=self.get_keyboard_results, default_text=name.replace('Name: ',''),back_destination='edit_preheat', title=lang.pack['Preheat']['Keyboard']['Title'])

    def get_keyboard_results(self, result):
        def overwrite():
            Logger.info("Result is: " + str(result))
            name = next(iter(self.selected_option))
    
            temp_option = {result:
                            {
                                'Extruder1': self.selected_option[name]['Extruder1'],
                                'Bed': self.selected_option[name]['Bed']
                            }  
                          }
    
            Logger.info(str(temp_option))
    
            self.selected_option = temp_option
            self.name_button.title = lang.pack['Preheat']['Edit_Preset']['Name'] + result

            roboprinter.robosm.current = 'edit_preheat'
            self.confirm_overwrite = True
        def cancel():
            name = next(iter(self.selected_option))
            self.show_keyboard(name)

        #check if the result will overwrite an existing preset
        preheat_settings = self.settings.get(['Temp_Preset'])
        if result in preheat_settings or result == lang.pack['Preheat']['Edit_Preset']['Name_Default']:
            #make the modal screen
            body_text = lang.pack['Preheat']['Duplicate']['Body_Text'] + str(result) + lang.pack['Preheat']['Duplicate']['Body_Text1']
            modal_screen = Modal_Question_No_Title(body_text, lang.pack['Preheat']['Duplicate']['option1'] , lang.pack['Preheat']['Duplicate']['option2'] , overwrite, cancel)

            #make screen
            roboprinter.robosm._generate_backbutton_screen(name='duplicate_error', title = lang.pack['Preheat']['Duplicate']['Title'], back_destination='edit_preheat', content=modal_screen)
        else:
            overwrite()



    def show_keypad(self, value):
        if value.find("Extruder:") != -1:
            #callback, number_length=3,name='keyboard_screen', title=lang.pack['Files']['Keyboard']['Default_Title']
            Keypad(self.collect_ext1_key, name='ext1_keyboard', title=lang.pack['Preheat']['Keypad']['Title_ext1'])
        else:
            Keypad(self.collect_bed_key, name='bed_keyboard', title=lang.pack['Preheat']['Keypad']['Title_bed'])

    def collect_ext1_key(self, value):
        Logger.info("Ext1 Result is: " + str(value))
        if int(value) > 290:
            ep = Info_Popup(lang.pack['Preheat']['Errors']['Ext1_Error'], lang.pack['Preheat']['Errors']['Ext1_Body'])
            value = 290
            ep.show()
        name = next(iter(self.selected_option))


        self.selected_option[name]['Extruder1'] = int(value) 
        self.ext1_button.title = lang.pack['Preheat']['Edit_Preset']['Ext'] + str(self.selected_option[name]['Extruder1']) + lang.pack['Preheat']['Celsius_Alone']

    def collect_bed_key(self, value):
        Logger.info("Bed Result is: " + str(value))
        if int(value) > 100:
            ep = Info_Popup(lang.pack['Preheat']['Errors']['Bed_Error'], lang.pack['Preheat']['Errors']['Bed_Body'])
            value = 100
            ep.show()
        name = next(iter(self.selected_option))

        self.selected_option[name]['Bed'] = int(value) if int(value) <= 100 else 100
        self.bed_button.title = lang.pack['Preheat']['Edit_Preset']['Bed'] + str(self.selected_option[name]['Bed']) + lang.pack['Preheat']['Celsius_Alone']

    def save_preset(self):
        #get all the options
        presets = self.settings.get(['Temp_Preset'])
        current_screen = roboprinter.robosm.current
        name = next(iter(self.selected_option))
       

        def save_new_entry():
             #delete old entry
            if self.original_option != None:
                del presets[self.original_option]
            #save new entry
            
            presets[name] = self.selected_option[name]
    
            #save
            self.settings.set(['Temp_Preset'], presets)
            self.settings.save()
    
            #update screen
            self.callback(name)
        def cancel():
            #go back to previous screen 
            roboprinter.robosm.current = current_screen

        #check for duplicate names
        
        
        if name in presets and name != self.original_option and not self.confirm_overwrite:

            #make the modal screen
            body_text = lang.pack['Preheat']['Duplicate']['Body_Text'] + str(name) + lang.pack['Preheat']['Duplicate']['Body_Text1']
            modal_screen = Modal_Question_No_Title(body_text, 
                                                   lang.pack['Preheat']['Duplicate']['option1'] , 
                                                   lang.pack['Preheat']['Duplicate']['option2'] , 
                                                   save_new_entry, 
                                                   cancel)

            #make screen
            roboprinter.robosm._generate_backbutton_screen(name='duplicate_error', 
                                                           title = lang.pack['Preheat']['Duplicate']['Title'], 
                                                           back_destination=current_screen, 
                                                           content=modal_screen)
        
        else:
            save_new_entry()


    def delete_preset(self):
        screen = roboprinter.robosm.current
        def delete():
            #get all the options
            presets = self.settings.get(['Temp_Preset'])
    
            #delete entry
            name = next(iter(self.selected_option))
            del presets[name]
    
            #save
            self.settings.set(['Temp_Preset'], presets)
            self.settings.save()

            #Info Popup saying that we deleted the preset
            title = lang.pack['Preheat']['Delete']['Deleted']
            ep = Error_Popup(name, title, callback=self.delete_callback)
            ep.show()
        def cancel():
            roboprinter.robosm.current = screen

        #make the modal screen
        name = next(iter(self.selected_option))
        body_text = lang.pack['Preheat']['Delete']['Body'] + str(name) + lang.pack['Preheat']['Delete']['Q_Mark'] 
        modal_screen = Modal_Question_No_Title(body_text, lang.pack['Preheat']['Delete']['positive'] , lang.pack['Preheat']['Delete']['negative'] , delete, cancel)

        #make screen
        roboprinter.robosm._generate_backbutton_screen(name='delete_preset', title = lang.pack['Preheat']['Delete']['Title'] , back_destination=screen, content=modal_screen)

#This is just a simple button for the different options. It has a large title and a small body text
class Preheat_Button(Button):
    title = StringProperty('')
    body_text = StringProperty('')
    picture_source = StringProperty('')
    callback = ObjectProperty(None)
    def __init__(self, title, body_text, callback):
        super(Preheat_Button, self).__init__()
        self.title = title
        self.body_text = body_text
        self.callback = callback

#this is a simple button that can be added anywhere
class Simple_Button(Button):
    button_text = StringProperty('')
    background_normal = StringProperty('')
    callback = ObjectProperty(None)

    def __init__(self, button_text, background_normal, callback):
        self.button_text = button_text
        self.background_normal = background_normal
        self.callback = callback
        super(Simple_Button, self).__init__()


        


