from kivy.uix.button import Button
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, BooleanProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
from .. import roboprinter
from functools import partial
from kivy.logger import Logger
from kivy.clock import Clock
from pconsole import pconsole
import thread
from connection_popup import Connection_Popup, Updating_Popup, Error_Popup, Warning_Popup, USB_Progress_Popup
import os
import tempfile
import traceback
import shutil
import subprocess
from scrollbox import ScrollBox, Scroll_Box_Even
from file_explorer import Save_File
from file_explorer import File_Explorer

USB_DIR = '/home/pi/.octoprint/uploads/USB'
FILES_DIR = '/home/pi/.octoprint/uploads'
TEMP_DIR = '/tmp/stl'
CURA_DIR = '/home/pi/.octoprint/slicingProfiles/cura'

class Slicer_Wizard(FloatLayout):

    def __init__(self,robosm, back_destination):
        super(Slicer_Wizard, self).__init__()

        #make default meta data
        self.meta = {
            'layer height' : '--',
            'layers' : '--',
            'infill' : '--',
            'time' : {'hours': str(0), 
                      'minutes': str(0),
                      'seconds': str(0)
                      }
        }
        #make sure the tmp directory exists
        self.search_for_temp_dir()

        self.sm = robosm
        self.oprint = roboprinter.printer_instance

        #show the confirmation screen

        self.show_confirmation_screen()

    def show_confirmation_screen(self):
        next_action = self.open_file_select_screen
        screen_name = "slicing wizard"
        title = "Slicing Wizard"
        back_destination = self.sm.current
        layout = STL_Confirmation_Screen(next_action)
        self.sm._generate_backbutton_screen(name = screen_name, title = title, back_destination=back_destination, content=layout)


        

    def open_file_select_screen(self):
        layout = File_Explorer('model', self.create_button, enable_editing = False)
        #continue to the stl select screen
        back_destination = self.sm.current
        name = "Choose STL File"
        

        self.sm._generate_backbutton_screen(name = name, title = name, back_destination=back_destination, content=layout)

    #a helper function so we can use the file explorer
    def create_button(self, filename, date, path, **kwargs):
        return stl_Button(filename, path, date, self.choose_overrides)



    def search_for_temp_dir(self):
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
            Logger.info("Made temp directory for slicing")

    def choose_overrides(self, name, path):
        screen_name = 'slicer_overrides'
        title = "Choose Slicer Options"
        back_destination = self.sm.current
        real_path = roboprinter.printer_instance._file_manager.path_on_disk('local', path)
        Logger.info(real_path)
        layout = Override_Page(name, real_path, self.slice_stl)

    
    def slice_stl(self, name, path, overrides):
        #get the profile from octoprint
        self.progress_pop =  USB_Progress_Popup("Slicing " + name, 1)
        self.progress_pop.show()
        self.stl_name = name.replace(".stl", "")
        self.stl_name = self.stl_name.replace(".STL", "")
        self.stl_name = self.stl_name + ".gcode"
        self.stl_path = path
        self.overrides = overrides

        Clock.schedule_once(self.start_slice, 0.1)

    def start_slice(self,dt):
        
        profiles = roboprinter.printer_instance._slicing_manager.all_profiles('cura', require_configured=False)
        if 'robo' in profiles:
            #start slice
            self.temp_path = TEMP_DIR + "/" + self.stl_name
            Logger.info("Starting Slice")
            Logger.info(self.overrides)
            roboprinter.printer_instance._slicing_manager.slice('cura', 
                                                                self.stl_path, 
                                                                self.temp_path, 
                                                                'robo', 
                                                                self.sliced, 
                                                                overrides=self.overrides,
                                                                on_progress = self.slice_progress)
        else:
            #put our profile in the profile list
            profile_path = os.path.dirname(os.path.realpath(__file__))
            profile_path += '/slicer_profile/robo.profile'

            if os.path.isfile(profile_path):
                #copy a backup of the profile to the default profile directory
                shutil.copyfile(profile_path, CURA_DIR + '/robo.profile')
                
                #if the backup exists and we have tried restoring it 5 times give up and error out
                if dt < 5:
                    Logger.info('Restarting the slice, Rec Depth = ' + str(dt+1))
                    self.start_slice(dt+1)
                else:
                    ep = Error_Popup("Profile Error", "The profile \"robo.profile\" does not exist\nand cannot be automatically restored")
                    ep.show()
            #if the backup does not exist then error out
            else:
                Logger.info('Slicer Error: Path Does not exist')
                ep = Error_Popup("Profile Error", "The profile \"robo.profile\" does not exist\nand cannot be automatically restored")
                ep.show()
            

    def sliced(self, **kwargs):
        Logger.info(kwargs)
        if '_error' in kwargs:
            self.progress_pop.hide()
            Logger.info(str(kwargs['_error']))
            os.remove(self.temp_path)
            ep = Error_Popup("Slicing Failed", "The File has failed to slice correctly\nPlease try again")
            ep.show()
        elif '_analysis' in kwargs:
            #initialize meta data
            ept = 0
            lh = str(self.overrides['layer_height'])
            infill = str(self.overrides['fill_density'])
            if 'estimatedPrintTime' in kwargs['_analysis']:
                ept = kwargs['_analysis']['estimatedPrintTime']
            #save meta data
            self.meta = {
                'layer height' : lh,
                'infill' : infill,
                'time' : ept
            }

            Logger.info("finished Slice")
            self.progress_pop.hide()
            #after slicing ask the user where they want the file to be saved at
            Clock.schedule_once(self.save_file, 0.01)

        else:
            Logger.info("finished Slice")
            self.progress_pop.hide()
            #after slicing ask the user where they want the file to be saved at
            Clock.schedule_once(self.save_file, 0.01)

     # This takes a number in seconds and returns a dictionary of the hours/minutes/seconds
    def parse_time(self, time):
        m, s = divmod(time, 60)
        h, m = divmod(m, 60)

        time_dict = {'hours': str(h),
                     'minutes': str(m),
                     'seconds': str(s)
                     }

        return time_dict


    # this function exists because calling the Save_File class directly from the sliced function resulted in Graphical issues
    # Setting a clock to call this function fixed the graphical issues. I believe it is because the sliced function gets called
    # by the slicing manager thread, and graphical issues do present themselves when calling kivy objects outside the thread
    # they are created in.
    def save_file(self, dt):
        Logger.info('Saving data ' + self.temp_path + ' along with the meta data: ' + str(self.meta))
        Save_File(self.temp_path, meta_data=self.meta)

    def slice_progress(self, *args, **kwargs):
        if '_progress' in kwargs:
            #Logger.info(str(kwargs['_progress']))
            self.progress_pop.update_progress(kwargs['_progress'])
    

class stl_Button(Button):
    button_text = StringProperty("Error")
    stl_name = StringProperty("ERROR")
    path = StringProperty("Error")
    date = StringProperty("Error")
    button_function = ObjectProperty(None)
    def __init__(self,hexname, path, date, function):
        super(stl_Button, self).__init__()
        self.stl_name = hexname
        self.path = path
        self.button_function = function
        self.button_text = self.stl_name
        self.date = date

class STL_Confirmation_Screen(GridLayout):
    button_function = ObjectProperty(None)

    def __init__(self, function):
        super(STL_Confirmation_Screen, self).__init__()
        self.button_function = function

class Override_Page(object):

    def __init__(self, name, path, slice_callback):
        super(Override_Page, self).__init__()
        #initialize properties
        self._support = False
        self._raft = False
        self._first_layer_width = 300.0
        self._material = 'PLA'
        self._layer_height = 0.15
        self._infill = 20
        self._fans = True

        #variable for calling once the user is done setting overrides
        self.slice_callback = slice_callback
        self.name = name
        self.path = path
        self.load_raft_and_supports()

        

    ####################################Property Settings#########################

    #These are the class settings that will eventually become overrides

    @property
    def support(self):
        Logger.info("Getting support")
        return self._support

    @support.setter
    def support(self, value):
        self._support = value
        Logger.info("setting support to: " + str(self._support))

    @property
    def raft(self):
        Logger.info("Getting raft")
        return self._raft

    @raft.setter
    def raft(self, value):
        self._raft = value
        Logger.info("setting raft to: " + str(self._raft))
        if self._raft == True:
            self._first_layer_width = 100.0
        else:
            self._first_layer_width = 300.0

    @property
    def material(self):
        Logger.info("Getting material")
        return self._material

    @material.setter
    def material(self, value):
        acceptable_material = {'ABS':'ABS', 'PLA': 'PLA'}
        if value in acceptable_material:
            self._material = value
            if self._material == 'ABS':
                self._fans = False
            else:
                self._fans = True
        Logger.info("setting material to: " + str(self._material))
    @property
    def layer_height(self):
        Logger.info("Getting layer_height")
        return self._layer_height

    @layer_height.setter
    def layer_height(self, value):
        Logger.info("setting layer_height to: "+ str(self._layer_height))
        self._layer_height = value

    @property
    def infill(self):
        Logger.info("Getting infill")
        return self._infill

    @infill.setter
    def infill(self, value):
        Logger.info("setting infill to: " + str(self._infill))
        self._infill = value

    #########################################end Class Properties



    def load_raft_and_supports(self):
        def supports(state):
            self.support = state
        def rafts(state):
            self.raft = state

        support_button = OL_Button("Supports", "Icons/Slicer wizard icons/Supports.png", supports)
        raft_button = OL_Button("Raft", "Icons/Slicer wizard icons/Rafts.png", rafts)

        bl = [support_button, raft_button]

        layout = Override_Layout(bl, "Adding a raft will improve bed adhesion\nSupports are suggested for prints with steep overhangs")
        back_destination = roboprinter.robosm.current
        roboprinter.back_screen(name = 'raft and support', 
                                title = 'Raft and Support', 
                                back_destination=back_destination, 
                                content=layout,
                                cta = self.print_quality,
                                icon = "Icons/Slicer wizard icons/next.png")

    def print_quality(self):
        
        bgo_pq = Button_Group_Observer()

        def mm_20(state):
            if state:
                self.layer_height = 0.20
        def mm_15(state):
            if state:
                self.layer_height = 0.15
        def mm_10(state):
            if state:
                self.layer_height = 0.10
        def mm_06(state):
            if state:
                self.layer_height = 0.06

        mm_20_button = OL_Button("0.20 mm", "Icons/Slicer wizard icons/60px/step1 (1).png", mm_20, enabled = False, observer_group = bgo_pq)
        mm_15_button = OL_Button("0.15 mm", "Icons/Slicer wizard icons/60px/step2 (1).png", mm_15, enabled = True, observer_group = bgo_pq)
        mm_10_button = OL_Button("0.10 mm", "Icons/Slicer wizard icons/60px/step3 (1).png", mm_10, enabled = False, observer_group = bgo_pq)
        mm_06_button = OL_Button("0.06 mm", "Icons/Slicer wizard icons/60px/step4.png", mm_06, enabled = False, observer_group = bgo_pq)
        bl = [mm_20_button, mm_15_button, mm_10_button, mm_06_button]


        layout = Override_Layout(bl, "A smaller print quality will produce a fine print,\nbut it will take longer to print")
        back_destination = roboprinter.robosm.current
        roboprinter.back_screen(name = 'print quality', 
                                title = 'Print Quality', 
                                back_destination=back_destination, 
                                content=layout,
                                cta = self.infill_layout,
                                icon = "Icons/Slicer wizard icons/next.png")

    
    def infill_layout(self):
        
        bgo_pq = Button_Group_Observer()

        def p_0(state):
            if state:
                self.infill = 0
        def p_10(state):
            if state:
                self.infill = 10
        def p_25(state):
            if state:
                self.infill = 25
        def p_100(state):
            if state:
                self.infill = 100

        percent_0 = OL_Button("0%", "Icons/Slicer wizard icons/hollow.png", p_0, enabled = False, observer_group = bgo_pq)
        percent_10 = OL_Button("10%", "Icons/Slicer wizard icons/10%.png", p_10, enabled = True, observer_group = bgo_pq)
        percent_25 = OL_Button("25%", "Icons/Slicer wizard icons/25%.png", p_25, enabled = False, observer_group = bgo_pq)
        percent_100 = OL_Button("100%", "Icons/Slicer wizard icons/100%.png", p_100, enabled = False, observer_group = bgo_pq)
        bl = [percent_0, percent_10, percent_25, percent_100]


        layout = Override_Layout(bl, "Infill sets how dense the inside of the object is")
        back_destination = roboprinter.robosm.current
        roboprinter.back_screen(name = 'infill', 
                                title = 'Infill', 
                                back_destination=back_destination, 
                                content=layout,
                                cta = self.choose_material,
                                icon = "Icons/Slicer wizard icons/next.png")

    def choose_material(self):
        
        bgo_pq = Button_Group_Observer()

        def absm(state):
            if state:
                self.material = 'ABS'
        def plam(state):
            if state:
                self.material = 'PLA'
        

        abs_button = OL_Button("ABS", "Icons/Slicer wizard icons/ABS.png", absm, enabled = False, observer_group = bgo_pq)
        pla_button = OL_Button("PLA", "Icons/Slicer wizard icons/PLA.png", plam, enabled = True, observer_group = bgo_pq)
        bl = [abs_button, pla_button]


        layout = Override_Layout(bl, "PLA will set the nozzle to 190 degrees celsius\nABS will set the nozzle to 230 degrees celsius")
        back_destination = roboprinter.robosm.current
        roboprinter.back_screen(name = 'material', 
                                title = 'Print Material', 
                                back_destination=back_destination, 
                                content=layout,
                                cta = self.continue_slicing,
                                icon = "Icons/Slicer wizard icons/next.png")

    def placeholder(self):
        current_overrides = {'rafts': self.raft,
                             'support': self.support,
                             'material': self.material,
                             'infill': self.infill,
                             'layer_height': self.layer_height}
        Logger.info(str(current_overrides))
        pass

    def continue_slicing(self):
        acceptable_material = {
                                'ABS': [230,0,0,0],
                                'PLA': [190,0,0,0]
        }
        model = roboprinter.printer_instance._settings.get(['Model'])

        if model == "Robo R2":
            bed = {
                    'ABS': 80,
                    'PLA': 60
            }
        elif model == "Robo C2":
            bed = {
                    'ABS': 0,
                    'PLA': 0
            }
        #just in case Model is set to None or someone has messed with it and broken everything
        else:
            bed = {
                    'ABS': 0,
                    'PLA': 0
            }

        if self.material in acceptable_material:
            self.print_temperature = acceptable_material[self.material]

            self.print_bed_temperature = bed[self.material]
        else:
            Logger.info("Defaulting to PLA. #############")
            self.print_temperature = acceptable_material['PLA']

        if self.raft:
            self.platform_adhesion = 'raft'
        else:
            self.platform_adhesion = 'none'
             
        if self.support:
            self.support = 'buildplate'
        else:
            self.support = 'none'

        overrides = {
                    'layer_height': self.layer_height,
                    'print_temperature': self.print_temperature,
                    'print_bed_temperature': self.print_bed_temperature,
                    'fill_density': self.infill,
                    'support': self.support,
                    'platform_adhesion': self.platform_adhesion,
                    'first_layer_width_factor': self._first_layer_width,
                    'fan_enabled': self._fans,
                    'fan_speed': 100 if self._fans else 0,
                    'fan_speed_max': 100 if self._fans else 0,
                    'fan_full_height': 0.1 if self._fans else -1
                    
                    }

        Logger.info(str(overrides))

        self.slice_callback(self.name, self.path, overrides)

class Override_Layout(BoxLayout):
    body_text = StringProperty("Error")

    def __init__(self, button_list, body_text, **kwargs):
        super(Override_Layout, self).__init__()
        self.body_text =  body_text
        self.button_list = button_list
        self.alter_layout()

    def alter_layout(self):
        grid = self.ids.button_grid

        grid.clear_widgets()

        button_count = len(self.button_list)
        if button_count == 2:
            #make a 2 grid
            grid.add_widget(Label(text=""))
            for button in self.button_list:
                grid.add_widget(button)
            grid.add_widget(Label(text=""))
        elif button_count == 4:
            #make a 4 grid
            for button in self.button_list:
                grid.add_widget(button)
        elif button_count == 3:
            #make a 3 grid
            for button in self.button_list:
                grid.add_widget(button)
        else:
            #Throw an error because there's only supposed to be 2 and 4
            pass


class OL_Button(Button):
    button_text = StringProperty("Error")
    pic_source = StringProperty("Icons/Slicer wizard icons/low.png")
    button_background = ObjectProperty("Icons/Keyboard/keyboard_button.png")
    button_bg = ObjectProperty(["Icons/Slicer wizard icons/button bkg inactive.png", "Icons/Slicer wizard icons/button bkg active.png"])
    bg_count = NumericProperty(0)
    button_function = ObjectProperty(None)
    def __init__(self, body_text, image_source, button_function, enabled = True, observer_group = None, **kwargs):
        super(OL_Button, self).__init__()
        self.button_text = body_text
        self.pic_source = image_source
        self.button_function = button_function

        #add self to observer group
        self.observer_group = observer_group
        if self.observer_group != None:
            self.observer_group.register_callback(self.button_text, self.toggle_bg)
            if enabled:
                self.observer_group.change_button(self.button_text)
        else:
            if enabled:
                #show blue or grey for enabled or disables
                self.change_state(enabled)
                

    def change_bg(self):
        if self.observer_group != None:
            if self.observer_group.active_button != self.button_text:
                if self.bg_count == 1 :
                    self.bg_count = 0
                else:
                    self.bg_count += 1
        
                if self.bg_count == 1:
                    self.observer_group.change_button(self.button_text)

                #self.change_state(self.bg_count)
        else:
            if self.bg_count == 1:
                self.bg_count = 0
            else:
                self.bg_count += 1
            self.change_state(self.bg_count)

    def toggle_bg(self, name):
        if str(name) == str(self.button_text):
            self.button_function(True)
            self.bg_count = 1
        else:
            self.bg_count = 0
        self.button_background = self.button_bg[self.bg_count]

    def change_state(self, state):
        if state:
            self.bg_count = 1
            self.button_function(True)
        else:
            self.bg_count = 0
            self.button_function(False)
        self.button_background = self.button_bg[self.bg_count]

class Button_Group_Observer():
    def __init__(self):
        self._observers = {}
        self.active_button = 'none'

    def register_callback(self, name, callback):
        self._observers[name] = callback

    def change_button(self, name):
        self.active_button = name
        if name in self._observers:
            for observer in self._observers:
                self._observers[observer](name)




   



