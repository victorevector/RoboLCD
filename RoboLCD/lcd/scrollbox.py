from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.logger import Logger

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


class Scroll_Box_Even(GridLayout):
    """docstring for Scroll_Box_Even"""
    position = 0
    max_pos = 0
    buttons = []
    def __init__(self, button_array):
        super(Scroll_Box_Even, self).__init__()
        self.grid = self.ids.content
        self.max_pos = len(button_array) - 4
        self.buttons = button_array
        if len(button_array) <= 4:
            self.scroll.clear_widgets()
            self.scroll.size_hint_x = None
            self.scroll.width = 1
        self.populate_buttons()

    def up_button(self):
        self.position -= 1
        if self.position < 0:
            self.position = 0
        self.populate_buttons()
        

    def down_button(self):
        self.position += 1
        if self.position > self.max_pos:
            self.position = self.max_pos
        self.populate_buttons()
        

    def populate_buttons(self):
        content = self.grid

        content.clear_widgets()

        if self.position + 0 < len(self.buttons):
            content.add_widget(self.buttons[self.position + 0])
        else:
            content.add_widget(Button(text='', background_color = [0,0,0,1]))

        if self.position + 1 < len(self.buttons):
            content.add_widget(self.buttons[self.position + 1])
        else:
            content.add_widget(Button(text='', background_color = [0,0,0,1]))

        if self.position + 2 < len(self.buttons):
            content.add_widget(self.buttons[self.position + 2])
        else:
            content.add_widget(Button(text='', background_color = [0,0,0,1]))

        if self.position + 3 < len(self.buttons):
            content.add_widget(self.buttons[self.position + 3])
        else:
            content.add_widget(Button(text='', background_color = [0,0,0,1]))

   



       
        