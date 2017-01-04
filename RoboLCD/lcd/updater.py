from kivy.uix.floatlayout import FloatLayout
from kivy.logger import Logger
from kivy.properties import StringProperty
import yaml
import os


class UpdateScreen(FloatLayout):
    installed_version = StringProperty('1.0.3')
    avail_version = StringProperty('1.0.4')

    def __init__(self):
        super(UpdateScreen, self).__init__()
        self.installed_version, self.avail_version = self.get_versions()

    def get_versions(self):
        path = os.path.dirname(os.path.realpath(__file__)) + '/updates/version.yaml'
        with open(path, 'r') as f:
            config = yaml.load(f)
        return config['versions']['installed'], config['versions']['available']

    def disable_me(self, sm):
        self.ids.updatebtn.disabled = True
        sm.run_updatechecker()
