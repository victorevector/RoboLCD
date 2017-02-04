from kivy.graphics import *
from .. import roboprinter
from kivy.clock import Clock
from kivy.uix.popup import Popup
from pconsole import pconsole
from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, BooleanProperty
from wizard import ZoffsetWizard
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.logger import Logger
from kivy.uix.label import Label


class Modal_Popup(ModalView):

    title_text = StringProperty("Error")
    body_text = StringProperty("error")
    dismiss_time = NumericProperty(5)
    dismiss_button = BooleanProperty(True)
    icon = StringProperty("Warning")
    callback_after_dismiss = ObjectProperty(None)
    yes_no = BooleanProperty(False)
    callback_yes = ObjectProperty(None)
    callback_no = ObjectProperty(None)

    rows = NumericProperty(1)
    cols = NumericProperty(1)
    root_rows = NumericProperty(3)

    def __init__(self, 
                title_text = "Error", 
                body_text = "Error",
                dismiss_time = 5, 
                dismiss_button= True, 

                icon = "WARNING", 
                callback_after_dismiss = None,
                yes_no = False,
                callback_yes = None,
                callback_no = None,
                **kwargs
                ):
        super(Modal_Popup, self).__init__()
        self.title_text = title_text
        self.body_text = body_text
        self.dismiss_time = dismiss_time
        self.dismiss_button = dismiss_button
        self.icon = icon
        self.callback_after_dismiss = callback_after_dismiss
        self.yes_no = yes_no
        self.callback_yes = callback_yes
        self.callback_no = callback_no

        self.create_popup()
        self.open()



    def create_popup(self):

        #buttons
        dis_button = Popup_Button(None, "","BLUE")
        yes = Popup_Button(None, "", "BLUE")
        no = Popup_Button(None, "", "BLUE")

        #detirmine layout of the popup
        if self.dismiss_time != -1:
            Clock.schedule_once(self.dismiss_popup, self.dismiss_time)

        if self.dismiss_button == True:
            dis_button = Popup_Button(self.dismiss_popup, "Dismiss", "BLUE")
            self.cols = 3
       

        if self.yes_no == True:
            if self.callback_yes != None and self.callback_no != None:
                yes = Popup_Button(self.callback_yes, "Yes", "BLUE")
                no = Popup_Button(self.callback_no, "No", "RED")
            else:
                #Raise and error if the callbacks are not set correctly
                raise Popup_Error("Yes and No Callbacks need to be defined")
        
        #add buttons to the button content
        if self.yes_no == True and self.dismiss_button == True:
            grid = Popup_Grid()
            grid.add_widget(yes)
            grid.add_widget(no)
            grid.add_widget(dis_button)

            self.ids.box_layout.add_widget(grid)
        elif self.yes_no == True and self.dismiss_button != True:
            grid = Popup_Grid()
            grid.add_widget(yes)
            grid.add_widget(no)

            self.ids.box_layout.add_widget(grid)
        elif self.yes_no != True and self.dismiss_button == True:
            grid = Popup_Grid()
            grid.add_widget(dis_button)

            self.ids.box_layout.add_widget(grid)
        elif self.yes_no == False and self.dismiss_button == False:
            image = self.ids.image
            label = self.ids.modal_question

            self.ids.box_layout.remove_widget(image)
            self.ids.box_layout.remove_widget(label)

            grid = Label(background_color = [0,0,0,1])
            self.ids.box_layout.add_widget(grid)

            self.ids.box_layout.add_widget(image)
            self.ids.box_layout.add_widget(label)




        

    def dismiss_popup(self):
        self.dismiss()

        if callback_after_dismiss != None:
            callback_after_dismiss()

class Popup_Button(Button):
    """docstring for Dismiss_Button"""
    function = ObjectProperty(None)
    button_text = StringProperty("Error")
    color = StringProperty('Icons/blue_button_style.png')

    def __init__(self, function, text, color):
        super(Popup_Button, self).__init__()
        self.function = function
        self.button_text = text

        if color == "BLUE":
            self.color = 'Icons/blue_button_style.png'
        else:
            self.color = 'Icons/red_button_style.png'
        pass

class Popup_Grid(GridLayout):
    """docstring for Popup_Grid"""
    def __init__(self):
        super(Popup_Grid, self).__init__()
        pass
        


class Popup_Error(Exception):
    def __init__(self, value):
         self.value = value
    def __str__(self):
        return repr(self.value)
        

    