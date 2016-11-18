from kivy.uix.screenmanager import Screen
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.graphics import RoundedRectangle
from kivy.clock import Clock
from kivy.logger import Logger

DEFAULT_FONT = 'Roboto'


class MainScreen(Screen):
    """
    Represents the the main screen template with 3 tab buttons on the top bar: Files, Printer, and Settings

    Is in charge of orchestrating content update for all 3 tabs
    """

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, .1)

    def update(self, dt):
        self.ids.printer_status_content.update(dt)
        self.ids.files_content.update(dt)

    def open_tab(self, tab_id):
        t = self.ids[tab_id]
        Logger.info('Tab: {}'.format(t))
        self.ids.mstp.switch_to(t)


class MainScreenTabbedPanel(TabbedPanel):
    """
    Represents the tabbed panels. Handles toggling between FilesTab, PrinterStatusTab and SettingsTab
    """

    def __init__(self, **kwargs):
        super(MainScreenTabbedPanel, self).__init__(**kwargs)







