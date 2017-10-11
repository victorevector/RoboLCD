from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty, ListProperty
from .. import roboprinter
from printer_jog import printer_jog
from kivy.clock import Clock
from pconsole import pconsole
from connection_popup import Error_Popup, Warning_Popup
import functools
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.button import Button
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, BooleanProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
from kivy.core.window import Window
from kivy.uix.vkeyboard import VKeyboard
from Language import lang
from RoboLCD.lcd.session_saver import session_saver

#available common screens:

#Wait_Screen
#callback, title, body_text

#Point_Layout
#button_list, body_text

#Modal_Question
#title, body_text, option1_text, option2_text, option1_function, option2_function

#Modal_Question_No_Title
#body_text, option1_text, option2_text, option1_function, option2_function

#Quad_Icon_Layout
#bl1, bl2, body_text

#Button_Screen
#body_text, button_function, button_text = roboprinter.lang.pack['Button_Screen']['Default_Button']

#Picture_Button_Screen
#title_text, body_text,image_source, button_function, button_text = roboprinter.lang.pack['Button_Screen']['Default_Button']

#Picture_Button_Screen_Body
#body_text,image_source, button_function, button_text = roboprinter.lang.pack['Button_Screen']['Default_Button']

#Title_Button_Screen
#title_text, body_text, button_function, button_text = roboprinter.lang.pack['Button_Screen']['Default_Button']

#Temperature_Wait_Screen
#continue_function

#Override_Layout
#button_list, body_text

#OL_Button
#body_text, image_source, button_function, enabled = True, observer_group = None

#Button_Group_Observer
#No arguments

#KeyboardInput
#keyboard_callback = None, default_text = '', name = 'keyboard_screen', title=lang.pack['Files']['Keyboard']['Default_Title'], back_destination=None

#Keypad
#callback, number_length=3,name='keyboard_screen', title=lang.pack['Files']['Keyboard']['Default_Title']

#Auto_Image_Label_Button
#text='', image_icon='', background_normal='', callback=None






class Wait_Screen(BoxLayout):
    """Wait Here until the printer stops moving"""
    callback = ObjectProperty(None)
    title = StringProperty("ERROR")
    body_text = StringProperty("ERROR")
    def __init__(self, callback, title, body_text):
        super(Wait_Screen, self).__init__()
        self.callback = callback
        self.title = title
        self.body_text = body_text
        self.countz = 0
        self.last_countz = 999
        self.counter = 0
        #this waits 60 seconds before polling for a position. This command is waiting for the M28 command to finish
        Clock.schedule_once(self.start_check_pos, 50)
        

    def start_check_pos(self, dt):
        Clock.schedule_interval(self.check_position, 0.5)

    def check_position(self, dt):
        ready = pconsole.busy
        Logger.info(ready)
        if not ready:
            self.countz = pconsole.get_position()
            if self.countz:
                
                Logger.info("Count Z: " + str(self.countz[6]) + " last Count Z: " + str(self.last_countz))
        
                if int(self.countz[6]) == int(self.last_countz):
                    #go to the next screen
                    Logger.info("GO TO NEXT SCREEN! ###########")
                    self.callback()
                    return False
        
                self.last_countz = self.countz[6]
        else:
            Logger.info("Pconsole is not ready")

class Point_Layout(BoxLayout):
    body_text = StringProperty("Error")

    def __init__(self, button_list, body_text, **kwargs):
        super(Point_Layout, self).__init__()
        self.body_text =  body_text
        self.button_list = button_list
        self.alter_layout()

    def alter_layout(self):
        grid = self.ids.button_grid

        grid.clear_widgets()

        button_count = len(self.button_list)
       
        for button in self.button_list:
            grid.add_widget(button)


class Modal_Question(BoxLayout):
    title = StringProperty("Error")
    body_text = StringProperty("Error")
    option1_text = StringProperty("Error")
    option2_text = StringProperty("Error")
    option1_function = ObjectProperty(None)
    option2_function = ObjectProperty(None)

    def __init__(self, title, body_text, option1_text, option2_text, option1_function, option2_function):
        super(Modal_Question, self).__init__()
        self.title = title
        self.body_text = body_text
        self.option1_text = option1_text
        self.option2_text = option2_text
        self.option1_function = option1_function
        self.option2_function = option2_function

class Modal_Question_No_Title(BoxLayout):
    body_text = StringProperty("Error")
    option1_text = StringProperty("Error")
    option2_text = StringProperty("Error")
    option1_function = ObjectProperty(None)
    option2_function = ObjectProperty(None)

    def __init__(self, body_text, option1_text, option2_text, option1_function, option2_function):
        super(Modal_Question_No_Title, self).__init__()
        self.body_text = body_text
        self.option1_text = option1_text
        self.option2_text = option2_text
        self.option1_function = option1_function
        self.option2_function = option2_function

    
class Quad_Icon_Layout(BoxLayout):
    body_text = StringProperty("Error")

    def __init__(self, bl1, bl2, body_text, **kwargs):
        super(Quad_Icon_Layout, self).__init__()
        self.body_text =  body_text
        self.bl1 = bl1
        self.bl2 = bl2
        self.alter_layout()

    def alter_layout(self):
        grid = self.ids.button_grid

        grid.clear_widgets()
       
        
        #make a 2x2 grid
        for button in self.bl1:
            grid.add_widget(button)

        for button in self.bl2:
            grid.add_widget(button)

class Button_Screen(BoxLayout):
    body_text = StringProperty("Error")
    button_function = ObjectProperty(None)
    button_text = StringProperty("OK")

    def __init__(self, body_text, button_function, button_text = roboprinter.lang.pack['Button_Screen']['Default_Button'], **kwargs):
        super(Button_Screen, self).__init__()
        self.body_text = body_text
        self.button_function = button_function
        self.button_text = button_text


class Picture_Button_Screen(BoxLayout):
    title_text = StringProperty("Error")
    body_text = StringProperty("Error")
    image_source = StringProperty("Icons/Slicer wizard icons/button bkg active.png")
    button_function = ObjectProperty(None)
    button_text = StringProperty("OK")
    
    def __init__(self, title_text, body_text,image_source, button_function, button_text = roboprinter.lang.pack['Button_Screen']['Default_Button'], **kwargs):
        super(Picture_Button_Screen, self).__init__()
        self.title_text = title_text
        self.body_text = body_text
        self.image_source = image_source
        self.button_function = button_function
        self.button_text = button_text

class Picture_Button_Screen_Body(BoxLayout):
    body_text = StringProperty("Error")
    image_source = StringProperty("Icons/Slicer wizard icons/button bkg active.png")
    button_function = ObjectProperty(None)
    button_text = StringProperty("OK")
    
    def __init__(self, body_text,image_source, button_function, button_text = roboprinter.lang.pack['Button_Screen']['Default_Button'], **kwargs):
        super(Picture_Button_Screen_Body, self).__init__()
        self.body_text = body_text
        self.image_source = image_source
        self.button_function = button_function
        self.button_text = button_text

class Title_Button_Screen(BoxLayout):
    title_text = StringProperty("Error")
    body_text = StringProperty("Error")
    button_function = ObjectProperty(None)
    button_text = StringProperty("OK")
    
    def __init__(self, title_text, body_text, button_function, button_text = roboprinter.lang.pack['Button_Screen']['Default_Button'], **kwargs):
        super(Title_Button_Screen, self).__init__()
        self.title_text = title_text
        self.body_text = body_text
        self.button_function = button_function
        self.button_text = button_text


class Picture_Instructions(BoxLayout):
    
    def __init__(self):
        super(Picture_Instructions, self).__init__()
        pass    


class Temperature_Wait_Screen(FloatLayout):
    continue_function = ObjectProperty(None)
    body_text = StringProperty("Please wait for the printer to finish preparing")
    temperature = StringProperty("0")

    def __init__(self, continue_function):
        super(Temperature_Wait_Screen, self).__init__()
        self.continue_function = continue_function
        Clock.schedule_interval(self.wait_for_temp, 0.2)

    def wait_for_temp(self, dt):
        temps = roboprinter.printer_instance._printer.get_current_temperatures()
        position_found_waiting_for_temp = False

        #get current temperature
        if 'tool0' in temps.keys():
            temp = temps['tool0']['actual']
            self.temperature = str(temp)

            if temp >= 190:
                position_found_waiting_for_temp = True
                #go to the next screen
                self.continue_function()
                return False

class Override_Layout(BoxLayout):
    body_text = StringProperty("Error")
    button_padding = ObjectProperty([0,0,0,0])

    def __init__(self, button_list, body_text, **kwargs):
        super(Override_Layout, self).__init__()
        self.body_text =  body_text
        self.button_list = button_list
        self.alter_layout()

    def alter_layout(self):
        grid = self.ids.button_grid

        grid.clear_widgets()

        button_count = len(self.button_list)
        if button_count == 2:
            #make a 2 grid
            self.button_padding = [200,0,200,35]
            for button in self.button_list:
                grid.add_widget(button)

        elif button_count == 4:
            #make a 4 grid
            self.button_padding = [15,0,15,35]
            for button in self.button_list:
                grid.add_widget(button)

        elif button_count == 3:
            #make a 3 grid
            self.button_padding = [100,0,100,35]
            for button in self.button_list:
                grid.add_widget(button)
        else:
            #Throw an error because there's only supposed to be 2 and 4
            pass




class OL_Button(Button):
    button_text = StringProperty("Error")
    pic_source = StringProperty("Icons/Slicer wizard icons/low.png")
    button_background = ObjectProperty("Icons/Keyboard/keyboard_button.png")
    button_bg = ObjectProperty(["Icons/Slicer wizard icons/button bkg inactive.png", "Icons/Slicer wizard icons/button bkg active.png"])
    bg_count = NumericProperty(0)
    button_function = ObjectProperty(None)
    def __init__(self, body_text, image_source, button_function, enabled = True, observer_group = None, **kwargs):
        super(OL_Button, self).__init__()
        self.button_text = body_text
        self.pic_source = image_source
        self.button_function = button_function

        #add self to observer group
        self.observer_group = observer_group
        if self.observer_group != None:
            self.observer_group.register_callback(self.button_text, self.toggle_bg)
            if enabled:
                self.observer_group.change_button(self.button_text)
        else:
            if enabled:
                #show blue or grey for enabled or disables
                self.change_state(enabled)
                

    def change_bg(self):
        if self.observer_group != None:
            if self.observer_group.active_button != self.button_text:
                if self.bg_count == 1 :
                    self.bg_count = 0
                else:
                    self.bg_count += 1
        
                if self.bg_count == 1:
                    self.observer_group.change_button(self.button_text)

                #self.change_state(self.bg_count)
        else:
            if self.bg_count == 1:
                self.bg_count = 0
            else:
                self.bg_count += 1
            self.change_state(self.bg_count)

    def toggle_bg(self, name):
        if str(name) == str(self.button_text):
            self.button_function(True)
            self.bg_count = 1
        else:
            self.bg_count = 0
        self.button_background = self.button_bg[self.bg_count]

    def change_state(self, state):
        if state:
            self.bg_count = 1
            self.button_function(True)
        else:
            self.bg_count = 0
            self.button_function(False)
        self.button_background = self.button_bg[self.bg_count]

class Button_Group_Observer():
    def __init__(self):
        self._observers = {}
        self.active_button = 'none'

    def register_callback(self, name, callback):
        self._observers[name] = callback

    def change_button(self, name, value=None):
        self.active_button = name
        if name in self._observers:
            for observer in self._observers:
                if value != None:
                    self._observers[observer](name, value)
                else:
                    self._observers[observer](name)


class KeyboardInput(FloatLayout):
    kbContainer = ObjectProperty()
    keyboard_callback = ObjectProperty(None)
    default_text = StringProperty('')

    def __init__(self, keyboard_callback = None, default_text = '', name = 'keyboard_screen', title=lang.pack['Files']['Keyboard']['Default_Title'], back_destination=None,**kwargs):
        super(KeyboardInput, self).__init__(**kwargs)
        self.default_text = default_text
        self.back_destination = back_destination
        self.first_press = False
        if self.back_destination == None:
            self.back_destination = roboprinter.robo_screen()

        roboprinter.back_screen(name=name, 
                                title=title, 
                                back_destination=self.back_destination, 
                                content=self)
        self.current_screen = roboprinter.robo_screen()
        self._keyboard = None
        self._set_keyboard('keyboards/abc.json')
        if keyboard_callback != None:
            self.keyboard_callback = keyboard_callback

        self.keyboard_watch = Clock.schedule_interval(self.monitor_screen_change, 0.2)

    def close_screen(self):
        if self._keyboard:
            Window.release_all_keyboards()
        roboprinter.robosm.current = self.back_destination
        self.keyboard_watch.cancel()

    def monitor_screen_change(self,dt):

        if self.current_screen != roboprinter.robo_screen():
            if self._keyboard:
                Window.release_all_keyboards()

            return False

    def _set_keyboard(self, layout):
        #Dock the keyboard
        kb = Window.request_keyboard(self._keyboard_close, self)
        if kb.widget:
            self._keyboard = kb.widget
            self._keyboard.layout = layout
            self._style_keyboard()
        else:
            self._keyboard = kb
        self._keyboard.bind(on_key_down=self.key_down)
        Logger.info('Keyboard: Init {}'.format(layout))

    def _keyboard_close(self):
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self.key_down)
            self._keyboard = None

    def _style_keyboard(self):
        if self._keyboard:
            self._keyboard.margin_hint = 0,.02,0,0.02
            self._keyboard.height = 250
            self._keyboard.key_background_normal = 'Icons/Keyboard/keyboard_button.png'
            self.scale_min = .4
            self.scale_max = 1.6


    def key_down(self, keyboard, keycode, text, modifiers):
        """
        Callback function that catches keyboard events and writes them as password
        """
        # Writes to self.ids.password.text
        if self.ids.fname.text == self.default_text and not self.first_press: #clear stub text with first keyboard push
            self.ids.fname.text = ''
        if keycode == 'backspace':
            self.ids.fname.text = self.ids.fname.text[:-1]
        elif keycode == 'capslock' or keycode == 'normal' or keycode == 'special':
            pass
        elif keycode == 'toggle':
            self.toggle_keyboard()
        else:
            self.ids.fname.text += text

        #detect first press
        if not self.first_press:
            self.first_press = True

    def toggle_keyboard(self):
        if self._keyboard.layout == "keyboards/abc.json":
            self._keyboard.layout = "keyboards/123.json"
        else:
            self._keyboard.layout = "keyboards/abc.json"


class Keypad(BoxLayout):
    input_temp = StringProperty('0')
    desired_temp = 0

    def __init__(self, callback, number_length=3,name='keyboard_screen', title=lang.pack['Files']['Keyboard']['Default_Title'], **kwargs):
        super(Keypad, self).__init__()
        self.back_destination = roboprinter.robo_screen()
        self.callback = callback
        self.number_length = number_length
        roboprinter.back_screen(name=name, 
                                title=title, 
                                back_destination=self.back_destination, 
                                content=self)


    def add_number(self, number):
        Logger.info(str(number) + " Hit")

        text = str(self.desired_temp)

        if len(text) < self.number_length:
        
            self.desired_temp = self.desired_temp * 10 + number
            self.input_temp = str(self.desired_temp)

    def delete_number(self):
        self.desired_temp = int(self.desired_temp / 10)
        self.input_temp = str(self.desired_temp)

    def set_number(self):
        self.callback(self.input_temp)
        roboprinter.robosm.current = self.back_destination




class Auto_Image_Label_Button(Button):
    background_normal = StringProperty("Icons/blue_button_style.png")
    image_icon = StringProperty("Icons/Printer Status/pause_button_icon.png")
    button_text = StringProperty("Error")
    callback = ObjectProperty(None)

    def __init__(self, text='', image_icon='', background_normal='', callback=None, **kwargs):
        self.button_text = text
        self.image_icon = image_icon
        self.background_normal = background_normal
        self.callback = callback
        self.kwargs = kwargs
        super(Auto_Image_Label_Button, self).__init__()

    def button_press(self):
        if self.callback != None:
            self.callback(**self.kwargs)

