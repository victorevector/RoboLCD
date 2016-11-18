from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty
from .. import roboprinter
from kivy.logger import Logger


class BackButtonScreen(Screen):
    """
    The BackButtonScreen consists of 4 properties: name, title, back_destination, and content.
    It provides a template for all aestheticaly related screens. It is the job of the caller to populate this class with the correct properties thatyou want to display on the screen. Content is an object property which can be populated with whatever hierarchy of widgets you want. They will be added to a ScrollView.
    """

    name = StringProperty('--')
    content = ObjectProperty(None)
    title = StringProperty('--')
    back_destination = StringProperty('--')
    cta = None
    icon = StringProperty('')

    def __init__(self, name, title, back_destination, content, **kwargs):
        super(BackButtonScreen, self).__init__()
        self.name = name
        self.title = title
        self.back_destination = back_destination
        self.content = content

        if kwargs.has_key('cta'):
            self.cta = kwargs['cta']
            self.icon = kwargs['icon']

    def populate_layout(self):
        # adds the self.content widget to the layout that is defined in the .kv
        self.ids.content_layout.add_widget(self.content)
        if self.cta:
            self.ids.cta.bind(on_press=self.cta)
            self.ids.cta_image.source = self.icon

    # def rebind(self, f, *args, **kwargs):
    #     # rebinds the back_button with f and
    #     self.ids.back_button.bind(on_press=f)
    #
    # def rebind_to_goback(self):
    #     self.ids.back_button.bind()
