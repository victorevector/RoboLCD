from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.logger import Logger
from kivy.properties import NumericProperty, ObjectProperty, StringProperty,  BooleanProperty
from robo_controls import Temperature_Label
from kivy.clock import Clock


class ScrollBox(BoxLayout):
    """
    Custom widget -- ScrollBox. BoxLayout with 2 halves. Left half is a ScrollView and right half is 2 up and down buttons that scroll the ScrollView.
    """
    scroll = ObjectProperty(None)
    updown_layout = ObjectProperty(None)
    custom_content = ObjectProperty(None)

    def __init__(self, content, **kwargs):
        """
        Constructs the layout. Input requires populated Gridlayout (content) that gets injected into ScrollView (self.scroll). Up and down buttons will scroll through items in gridlayout.
        """
        super(ScrollBox, self).__init__(orientation='horizontal', **kwargs)
        self.scroll = self._create_scroll_view()
        self.updown_layout = self._create_up_down_button()
        self.custom_content = content

        self.scroll.add_widget(self.custom_content)
        self.add_widget(self.scroll)
        self.add_widget(self.updown_layout)


    def _create_scroll_view(self):
        scrollview = ScrollView(id='scrollview', do_scroll_x=False, do_scroll_y=False, size_hint_y=1, size_hint_x=0.8)
        return scrollview

    def _create_up_down_button(self):
        gridlayout = GridLayout(rows=2, size_hint_x=0.2, spacing=20, padding=(10,10,10,10))
        button_up = Button(
                           background_normal="Icons/Up-arrow-grey.png",
                           background_down="Icons/Up-arrow-blue.png",
                           )
        button_up.bind(on_press=self.up_action_file)
        button_down = Button(
                             background_normal="Icons/Down-arrow-grey.png",
                             background_down="Icons/Down-arrow-blue.png",
                             )
        button_down.bind(on_press=self.down_action_file)
        gridlayout.add_widget(button_up)
        gridlayout.add_widget(button_down)
        return gridlayout

    def up_action_file(self, *args):
        scroll_distance = 0.4
        #makes sure that user cannot scroll into the negative space
        if self.scroll.scroll_y + scroll_distance > 1:
            scroll_distance = 1 - self.scroll.scroll_y
        self.scroll.scroll_y += scroll_distance

    def down_action_file(self, *args):
        scroll_distance = 0.4
        #makes sure that user cannot scroll into the negative space
        if self.scroll.scroll_y - scroll_distance < 0:
            scroll_distance = self.scroll.scroll_y
        self.scroll.scroll_y -= scroll_distance


class Scroll_Box_Even(BoxLayout):
    """docstring for Scroll_Box_Even"""
    position = 0
    max_pos = 0
    buttons = []
    up_icons = ["Icons/Up-arrow-grey.png", "Icons/Up-arrow-blue.png"]
    down_icons = ["Icons/Down-arrow-grey.png", "Icons/Down-arrow-blue.png"]
    up_icon = ObjectProperty("Icons/Up-arrow-grey.png")
    down_icon = ObjectProperty("Icons/Down-arrow-grey.png")
    def __init__(self, button_array):
        super(Scroll_Box_Even, self).__init__()
        Logger.info("Initializing SBE")
        self.up_event = None
        self.down_event = None
        self.grid = self.ids.content
        self.max_pos = len(button_array) - 4
        self.buttons = button_array
        if len(button_array) <= 4:
            self.scroll.clear_widgets()
            self.scroll.size_hint_x = 0
            self.scroll.width = 0.1
        self.populate_buttons()

    def up_button(self):
        self.position -= 1
        if self.position < 0:
            self.position = 0
            self.up_event.cancel()
        self.populate_buttons()

    #every 0.2 seconds scroll up until the user releases the button
    def on_up_press(self):

        #change Color
        self.up_icon = self.up_icons[1]

        if self.up_event != None:
            self.up_event.cancel()
        if self.down_event != None:
            self.down_event.cancel()
        self.up_event = Clock.schedule_interval(self.on_up_clock, 0.2)


    def on_up_release(self):
        #change Color
        self.up_icon = self.up_icons[0]
        self.up_event.cancel()
        self.up_button()

    def on_up_clock(self,dt):
        self.up_button()
        

    def down_button(self):
        
        self.position += 1
        if self.position > self.max_pos:
            self.position = self.max_pos
            self.down_event.cancel()
        self.populate_buttons()

    #every 0.2 seconds scroll down until the user releases the button
    def on_down_press(self):
        #change Color
        self.down_icon = self.down_icons[1]
        if self.up_event != None:
            self.up_event.cancel()
        if self.down_event != None:
            self.down_event.cancel()
        self.down_event = Clock.schedule_interval(self.on_down_clock, 0.2)

    def on_down_release(self):
        #change Color
        self.down_icon = self.down_icons[0]
        self.down_event.cancel()
        self.down_button()

    def on_down_clock(self, dt):
        self.down_button()
        

    def populate_buttons(self):
        content = self.grid

        content.clear_widgets()

        for x in range(0,4):
            if self.position + x < len(self.buttons):
                content.add_widget(self.buttons[self.position + x])
            else:
                content.add_widget(Button(text='', background_color = [0,0,0,1]))

class Scroll_Box_Even_Button(Button):
    button_text = StringProperty("Error")
    generator= ObjectProperty("0")
    arg = ObjectProperty("ERROR")
    def __init__(self, text_button, generator_fuction, arg):
        super(Scroll_Box_Even_Button, self).__init__()
        self.button_text = text_button.encode('utf-8')
        self.generator = generator_fuction
        self.arg = arg



class Scroll_Box_Icons(GridLayout):
    """We should try to not have more than six icons on the screen"""
    cols = NumericProperty(2)
    rows = NumericProperty(3)
    buttons = []
    def __init__(self, button_array, robosm=None, **kwargs):
        super(Scroll_Box_Icons, self).__init__()

        
        #check to see if we need to resize the grid
        length = len(button_array)

        #format the buttons
        if length ==5 or length == 6:
            self.cols = 3
            self.rows = 2
        elif length == 4 or length == 3:
            self.cols = 2
            self.rows = 2
        elif length == 2:
            self.cols = 2
            self.rows = 1
        else:
            self.cols = 1
            self.rows = 1
        Logger.info("Cols: " + str(self.cols) + " Rows: " + str(self.rows))
        
        self.sm = robosm
        self.grid = self.ids.content
        self.buttons = button_array
        self.populate_buttons()   

    def populate_buttons(self):

        content = self.grid

        content.clear_widgets()
        for but in self.buttons:
            content.add_widget(but)

        length = len(self.buttons)
        if length == 5 or length == 3:
            if self.sm != None:
                tl = Temperature_Label(robosm=self.sm)
                content.add_widget(tl)
            else:
                content.add_widget(Button(text='', background_color = [0,0,0,1],size_hint = [0.0,0.0] ))

class Robo_Icons(Button):
    generator= StringProperty("ROBO_CONTROLS")
    img_source = StringProperty("Icons/Icon_Buttons/Robo_Controls.png")
    icon_name = StringProperty("Robo Controls")
    button_state = ObjectProperty(False)
    def __init__(self, _image_source, _icon_name, _generator_function):
        super(Robo_Icons, self).__init__()
        self. generator = _generator_function
        self.img_source = _image_source
        self.icon_name = _icon_name
        self.button_state = False

    




class Scroll_Box_Icons_Anchor(FloatLayout):
    """We should try to not have more than six icons on the screen"""
    buttons = []
    def __init__(self, button_array):
        super(Scroll_Box_Icons_Anchor, self).__init__()
        self.buttons = button_array
        self.populate_buttons()        

    def populate_buttons(self):

        left = self.ids.left
        left.add_widget(self.buttons[0])

        right = self.ids.right
        right.add_widget(self.buttons[1])

        center = self.ids.center
        center.add_widget(self.buttons[2])
        pass


        


class Robo_Icons_Anchor(Button):
    generator= StringProperty("ROBO_CONTROLS")
    img_source = StringProperty("Icons/Icon_Buttons/Robo_Controls.png")
    icon_name = StringProperty("Robo Controls")
    anchorx = StringProperty("left")
    anchory = StringProperty("center")
    def __init__(self, _image_source, _icon_name, _generator_function, position):
        super(Robo_Icons_Anchor, self).__init__()
        self. generator = _generator_function
        self.img_source = _image_source
        self.icon_name = _icon_name

        acceptable_positions = {'LEFT': {'anchor_x' : 'left', 'anchor_y': 'top'} ,
                                'RIGHT':{'anchor_x' : 'right', 'anchor_y': 'top'},
                                'CENTER':{'anchor_x' : 'center', 'anchor_y': 'bottom'},
                                }

        if position in acceptable_positions:
            self.anchorx = acceptable_positions[position]['anchor_x']
            self.anchory = acceptable_positions[position]['anchor_y']
            Logger.info(self.anchorx + " " + self.anchory)
        else:
            Logger.info(position + " Is not an acceptable position")







        
   



       
        