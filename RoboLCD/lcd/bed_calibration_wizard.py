from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty, ListProperty
from .. import roboprinter
from printer_jog import printer_jog
from kivy.clock import Clock
from pconsole import pconsole
from connection_popup import Error_Popup, Warning_Popup
import functools
from fine_tune_zoffset import Button_Screen, Picture_Button_Screen
from kivy.uix.boxlayout import BoxLayout
from slicer_wizard import Button_Group_Observer, OL_Button, Override_Layout

class Bed_Calibration(object):
    """Bed_Calibration Allows the user to move the head to three different points to manually level the bed through the 
       Screws on the bed"""
    def __init__(self):
        super(Bed_Calibration, self).__init__()
        pconsole.query_eeprom()
        self.model = roboprinter.printer_instance._settings.get(['Model'])
        self.welcome_screen()
        self.mode = "manual"

    def welcome_screen(self):
        layout = Button_Screen("Use this wizard to level the print bed by manually\n"
                               "adjusting the screws under the four corners of the bed.", 
                               self.tighten_all_screw_instructions,
                               button_text = "Start")
        title = "Bed Calibration Wizard"
        name = 'welcome_bed_calibration'
        back_destination = roboprinter.robo_screen()

        roboprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )
    def tighten_all_screw_instructions(self):
        layout = Button_Screen("Make sure that the bed is seated correctly and does\n"
                               "not tilt. [color=#69B3E7]Push down on each corner.[/color] If a corner tilts,\n"
                               "adjust the screw below until the tilting stops.", 
                               self.check_for_valid_start,
                               button_text = "Next")
        title = "Tilt Check"
        name = 'tilt1'
        back_destination = roboprinter.robo_screen()

        roboprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )

    def check_for_valid_start(self):
        start = self.check_offset()

        #if the ZOffset is not right don't allow the user to continue
        if start:
            self.ask_for_mode()
        else:
            zoff = pconsole.home_offset['Z']
            ep = Error_Popup("Z Offset not set", "The Z Offset is set to " + str(zoff) + " Please use the\nZ Offset Wizard before using this tool.")
            ep.open()

    def ask_for_mode(self):

        def manual():
            self.mode = "manual"
            self.prepare_printer()
        def guided():
            self.mode = "guided"
            self.prepare_printer()

        layout = Modal_Question("Choose Mode", 
                       "Choose guided mode for a complete step-by-step experience."
                       "\nChoose manual mode for a quicker, more advanced option.",
                       "Manual",
                       "Guided",
                       manual,
                       guided)

        title = "Mode Selection"
        name = 'guided_or_manual'
        back_destination = roboprinter.robo_screen()

        roboprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )



    
    #check the offset to see if it is in an acceptable range
    def check_offset(self):

        offset = float(pconsole.home_offset['Z'])
        #make sure the range is within -20 - 0
        if offset > -20.00 and not offset > 0.00 and offset != 0.00:
            return True
        else:
            return False

    def prepare_printer(self):
        #kill heaters
        roboprinter.printer_instance._printer.commands('M104 S0')
        roboprinter.printer_instance._printer.commands('M140 S0')
        roboprinter.printer_instance._printer.commands('M106 S255')

        roboprinter.printer_instance._printer.commands('G28') #Home Printer
        roboprinter.printer_instance._printer.commands('G1 X5 Y10 F5000') # go to first corner
        roboprinter.printer_instance._printer.commands('G1 Z5')

        fork_mode = self.open_3_point_screen
        title = "Manual"
        if self.mode == "guided":
            fork_mode = self.guided_instructions
            title = "Guided"
            

        layout = Wait_Screen(fork_mode,
                             "Preparing Printer",
                             "Please wait while the printer prepares for the next step.")
        name = "wait_screen"
        back_destination = roboprinter.robo_screen()


        roboprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )

    def guided_instructions(self):
        #turn off fans
        roboprinter.printer_instance._printer.commands('M106 S0')
        point_string = "Error"
        screw = "Error"
        point_icon = "Icons/Bed_Calibration/Bed placement left.png"
        body = ("Adjust the " + screw + " using the"
                "\nZ Offset Tool")
        self.counter = 1
        self.done = False
        def point_1():
            point_string = "Left Point"
            screw = "left front screw"
            point_icon = "Icons/Bed_Calibration/Bed placement left.png"
            self.update_body(point_string, screw, point_icon)

            roboprinter.printer_instance._printer.commands('G1 Z10')
            roboprinter.printer_instance._printer.commands('G1 X35 Y35 F5000') # go to first corner
            roboprinter.printer_instance._printer.commands('G1 Z0')

        def point_2():
            point_string = "Right Point"
            screw = "right front screw"
            point_icon = "Icons/Bed_Calibration/Bed placement right.png"
            self.update_body(point_string, screw, point_icon)
            
            roboprinter.printer_instance._printer.commands('G1 Z10')
            roboprinter.printer_instance._printer.commands('G1 X160 Y35 F5000') # go to first corner
            roboprinter.printer_instance._printer.commands('G1 Z0')

        def point_3():
            point_string = "Back Right Point"
            screw = "back right screw"
            point_icon = "Icons/Bed_Calibration/Bed placement back right.png"
            self.update_body(point_string, screw, point_icon)
            
            roboprinter.printer_instance._printer.commands('G1 Z10')
            roboprinter.printer_instance._printer.commands('G1 X160 Y160 F5000') # go to first corner
            roboprinter.printer_instance._printer.commands('G1 Z0')

        def point_4():
            point_string = "Back Left Point"
            screw = "back left screw"
            point_icon = "Icons/Bed_Calibration/Bed placement back left.png"
            self.update_body(point_string, screw, point_icon)
            
            roboprinter.printer_instance._printer.commands('G1 Z10')
            roboprinter.printer_instance._printer.commands('G1 X35 Y160 F5000') # go to first corner
            roboprinter.printer_instance._printer.commands('G1 Z0')


        def next_point():
            points = [point_1, point_2, point_3, point_4]

            if self.counter == 4 and not self.done:
                self.counter = 0
                self.done = True
            elif self.counter == 4 and self.done:
                self.finish_screws_instructions()
                return

            points[self.counter]()    

            self.counter += 1   

        self.guided_layout = Picture_Button_Screen(point_string, 
                                       body,
                                       point_icon,
                                       next_point,
                                       button_text = "Next")

        title = "Fine Adjustment"
        name = 'adjust_screws'
        back_destination = roboprinter.robo_screen()

        roboprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=self.guided_layout
        )

        point_1()

    def update_body(self, point_string, screw, icon):
        body = ("Adjust the " + screw + " using the"
                "\nZ Offset Tool")
        self.guided_layout.body_text = body
        self.guided_layout.title_text = point_string
        self.guided_layout.image_source = icon

        

    def open_instructions(self):
        #turn off fans
        roboprinter.printer_instance._printer.commands('M106 S0')
        layout = Button_Screen("Use the buttons on the next screen to go to different points"
                               "\non the bed. Then use the screws on the underside of the"
                               "\nbed to properly calibrate the bed level", 
                               self.open_3_point_screen)
        title = "Instructions"
        name = 'instructions'
        back_destination = roboprinter.robo_screen()

        roboprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )

    def open_3_point_screen(self):
        #turn off fans
        roboprinter.printer_instance._printer.commands('M106 S0')
       
        def point_1(state):
            if state:
                roboprinter.printer_instance._printer.commands('G1 Z10')
                roboprinter.printer_instance._printer.commands('G1 X35 Y35 F5000') # go to first corner
                roboprinter.printer_instance._printer.commands('G1 Z0')

        def point_2(state):
            if state:
                roboprinter.printer_instance._printer.commands('G1 Z10')
                roboprinter.printer_instance._printer.commands('G1 X160 Y35 F5000') # go to first corner
                roboprinter.printer_instance._printer.commands('G1 Z0')

        def point_3(state):
            if state:
                roboprinter.printer_instance._printer.commands('G1 Z10')
                roboprinter.printer_instance._printer.commands('G1 X160 Y160 F5000') # go to first corner
                roboprinter.printer_instance._printer.commands('G1 Z0')

        def point_4(state):
            if state:
                roboprinter.printer_instance._printer.commands('G1 Z10')
                roboprinter.printer_instance._printer.commands('G1 X35 Y160 F5000') # go to first corner
                roboprinter.printer_instance._printer.commands('G1 Z0')

        #make the button observer
        point_observer = Button_Group_Observer()

        #make the buttons
        p1 = OL_Button("Left", 
                       "Icons/Bed_Calibration/Bed placement left.png",
                       point_1,
                       enabled = True,
                       observer_group = point_observer)
        p2 = OL_Button("Right", 
                       "Icons/Bed_Calibration/Bed placement right.png",
                       point_2,
                       enabled = False,
                       observer_group = point_observer)
        p3 = OL_Button("Back Right", 
                       "Icons/Bed_Calibration/Bed placement back right.png",
                       point_3,
                       enabled = False,
                       observer_group = point_observer)
        p4 = OL_Button("Back Left", 
                       "Icons/Bed_Calibration/Bed placement back left.png",
                       point_4,
                       enabled = False,
                       observer_group = point_observer)

        bl2 = [p1, p2]
        bl1 = [p4, p3]

        #make screen
        layout = Quad_Icon_Layout(bl1, bl2,  "Select a corner and adjust the corresponding Screws")
        back_destination = roboprinter.robo_screen()
        roboprinter.back_screen(name = 'point_selection', 
                                title = 'Select Points', 
                                back_destination=back_destination, 
                                content=layout,
                                cta = self.finish_screws_instructions,
                                icon = "Icons/Slicer wizard icons/next.png")

    def finish_screws_instructions(self):
        layout = Button_Screen("Make sure that the bed is seated correctly and does\n"
                               "not tilt. [color=#69B3E7]Push down on each corner.[/color] If a corner tilts,\n"
                               "adjust the screw below until the tilting stops.", 
                               self.finish_wizard,
                               button_text = "Next")
        title = "Tilt Check"
        name = 'tilt2'
        back_destination = roboprinter.robo_screen()

        roboprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )

    def finish_wizard(self):
        
        layout = Picture_Button_Screen("Bed Calibration Complete", 
                                      "You are now ready to print!",
                                      'Icons/Manual_Control/check_icon.png',
                                      self.goto_main)
        title = "Finished Wizard"
        name = 'finish_wizard'
        back_destination = roboprinter.robo_screen()

        roboprinter.back_screen(
            name=name,
            title=title,
            back_destination=back_destination,
            content=layout
        )

    def goto_main(self):
        roboprinter.printer_instance._printer.commands('G28')
        roboprinter.robosm.go_back_to_main('utilities_tab')



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

          

