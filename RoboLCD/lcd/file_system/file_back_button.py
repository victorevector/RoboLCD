#Kivy
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.logger import Logger

#RoboLCD
from RoboLCD import roboprinter


class File_BB(Screen):
    back_function = ObjectProperty(None)
    title = StringProperty('')
    option_function = ObjectProperty(None)
    icon = StringProperty("Icons/settings.png")

    def __init__(self):
        super(File_BB, self).__init__()
        self.name="File_Explorer"
        self.title = ''
        self.back_function = None
        self.option_function = None
        self.content = None
        self.file_content = self.ids.content_layout
        
    def update_back_function(self, back_function):
        self.back_function = back_function

    def update_title(self, title):
        self.title = title

    def update_option_function(self, option_function, icon):
        self.option_function = option_function
        self.icon = icon

    def update_option_icon(self, option_icon):
        self.icon = option_icon

    def execute_back_function(self):
        if self.back_function != None:
            self.back_function()

    def execute_option_function(self):
        if self.option_function != None:
            self.option_function()

    def get_screen_data(self):
        screen_data = {
            'content': self.content,
            'title': self.title,
            'back_function': self.back_function,
            'option_function': self.option_function,
            'option_icon': self.icon
        }
        return screen_data

    def populate_old_screen(self, screen, ignore_update=False):
        self.set_screen_content(screen['content'],
                                screen['title'],
                                back_function=screen['back_function'],
                                option_function=screen['option_function'],
                                option_icon=screen['option_icon'])

        #check to see if the screen has an update function
        if hasattr(screen['content'], 'update') and callable(screen['content'].update) and not ignore_update:
            screen['content'].update()

    def set_screen_content(self, content, title, back_function='original', option_function='original', option_icon="Icons/settings.png"):
        self.file_content.clear_widgets()
        self.title = title
        self.content = content
        self.file_content.add_widget(content)
        self.icon = option_icon
        #if there is no previously set function and no newly set function then default to placeholder. else just keep the current config
        
        if back_function != 'original':
            self.back_function = back_function

        if option_function != 'original' and option_function != 'no_option':
            self.option_function = option_function

        if option_function == 'no_option':
            self.option_function = self.placeholder
            self.icon = "Icons/Printer Status/blank-warning.png" #blank



    def placeholder(self, *args, **kwargs):

        pass



