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
from session_saver import session_saver

class Print_Tuning(BoxLayout):

    tuning_number = StringProperty('[size=30]999')
    title_label_text = StringProperty('[size=40][color=#69B3E7]Flow Rate[/color][/size]')
    up_icon = StringProperty("Icons/Tuning/Up +1.png")
    down_icon = StringProperty("Icons/Tuning/Down +1.png")

    flow_rate_number = NumericProperty(100)
    feed_rate_number = NumericProperty(100)
    fan_speed_number = NumericProperty(100)
    button_size = [200,200]


    change_amount_value = [1,10]
    change_icon_up = ["Icons/Tuning/Up +1.png", "Icons/Tuning/Up +10.png"]
    change_icon_down = ["Icons/Tuning/Down +1.png", "Icons/Tuning/Down +10.png"]
    change_value = 0

    def __init__(self, **kwargs):
        super(Print_Tuning, self).__init__(**kwargs)
        self.flow_active = True
        self.feed_active = False
        self.fan_active = False
        self.tune_rates = {'FLOW': self.flow_rate_number, 
                           'FEED': self.feed_rate_number, 
                           'FAN': self.fan_speed_number}
        self.load_tuning_info()
        self.current_tuner = 'FLOW'
        self.set_active(self.current_tuner)

        self.max_rates = {'FLOW': 125,
                          'FEED': 200,
                          'FAN': 255}

        self.min_rates = {'FLOW': 75,
                          'FEED': 50,
                          'FAN': 0}

    
    def add_button(self, amount):
        self.tune_rates[self.current_tuner] += amount
        if self.tune_rates[self.current_tuner] in range(self.min_rates[self.current_tuner], self.max_rates[self.current_tuner]):
            self.tuning_number = str(self.tune_rates[self.current_tuner])

        elif self.tune_rates[self.current_tuner] > self.max_rates[self.current_tuner]:
            self.tune_rates[self.current_tuner] = self.max_rates[self.current_tuner]
            self.tuning_number = str(self.tune_rates[self.current_tuner])

        elif self.tune_rates[self.current_tuner] < self.min_rates[self.current_tuner]:
            self.tune_rates[self.current_tuner] = self.min_rates[self.current_tuner]
            self.tuning_number = str(self.tune_rates[self.current_tuner])

        self.apply_tunings()
        self.save_tuning_info()

    def flow_button(self):
        self.set_active('FLOW')
        self.title_label_text = "[size=40][color=#69B3E7]Flow Rate[/size][/color]"
        self.save_tuning_info()

    def feed_button(self):
        self.set_active('FEED')
        self.title_label_text = "[size=40][color=#69B3E7]Feed Rate[/size][/color]"
        self.save_tuning_info()

    def fan_button(self):
        self.set_active('FAN')
        self.title_label_text = "[size=40][color=#69B3E7]Fan Speed[/size][/color]"
        self.save_tuning_info()

    def set_active(self, tuner):
        acceptable_actives = {'FLOW': self.flow_active,
                              'FEED': self.feed_active,
                              'FAN': self.fan_active}

        if tuner in acceptable_actives:
            for t in acceptable_actives:
                acceptable_actives[t] = False
            acceptable_actives[tuner] = True
            self.current_tuner = tuner

            self.tuning_number = str(self.tune_rates[self.current_tuner])

    def save_tuning_info(self):
        session_saver.save_variable('FLOW', self.tune_rates['FLOW'])
        session_saver.save_variable('FEED', self.tune_rates['FEED'])
        session_saver.save_variable('FAN', self.tune_rates['FAN'])
        #Logger.info(str(session_saver.saved))

    def load_tuning_info(self):
        tuning_exists = False
        try:
            session_saver.saved['FLOW']
            tuning_exists = True
            Logger.info("Settings exist")
            Logger.info(str(session_saver.saved['FLOW']))
            Logger.info(str(session_saver.saved['FEED']))
            Logger.info(str(session_saver.saved['FAN']))

        except Exception as e:
            Logger.info("Settings do not exist")
            self.tune_rates['FLOW'] = 100
            self.tune_rates['FEED'] = 100
            self.tune_rates['FAN'] = 100
            
        if tuning_exists == True:
            self.tune_rates['FLOW'] =  session_saver.saved['FLOW']
            self.tune_rates['FEED'] =  session_saver.saved['FEED']
            self.tune_rates['FAN'] =  session_saver.saved['FAN']

    def apply_tunings(self):
        if self.current_tuner == 'FLOW':
            roboprinter.printer_instance._printer.flow_rate(self.tune_rates['FLOW'])
        elif self.current_tuner == 'FEED':
            roboprinter.printer_instance._printer.feed_rate(self.tune_rates['FEED'])
        elif self.current_tuner == 'FAN':
            roboprinter.printer_instance._printer.commands('M106 S'+ str(self.tune_rates['FAN']))

    def reset_tunings(self):
        self.tune_rates = {'FLOW': self.flow_rate_number, 
                           'FEED': self.feed_rate_number, 
                           'FAN': self.fan_speed_number}

        self.save_tuning_info()

    def change_amount(self):
        self.change_value += 1

        if self.change_value > 1:
            self.change_value = 0

        self.ids.change_text.text = "[size=60]{}[/size]".format(self.change_amount_value[self.change_value]) 
        self.ids.up_image.source = self.change_icon_up[self.change_value]
        self.ids.down_image.source = self.change_icon_down[self.change_value] 



