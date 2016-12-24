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

class Versioning(FloatLayout):
    version = StringProperty('[size=40][color=#69B3E7]Version: 1.0.4')