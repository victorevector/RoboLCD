from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanelHeader
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.effects.scroll import ScrollEffect
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from pconsole import pconsole
import math
from datetime import datetime
from kivy.logger import Logger
from .. import roboprinter
import os
import shutil
from robo_sm import screen_manager
import re
from scrollbox import ScrollBox, Scroll_Box_Even
import collections
from connection_popup import Zoffset_Warning_Popup, Error_Popup, USB_Progress_Popup
import subprocess
from Meta_Reader import Meta_Reader
import threading
from session_saver import session_saver
import traceback
import octoprint.filemanager
from multiprocessing import Process


USB_DIR = '/media/usb0'
FILES_DIR = '/home/pi/.octoprint/uploads'

class FileButton(Button):
    def __init__(self, filename, length, date, path, is_usb=False, **kwargs):
        super(FileButton, self).__init__(**kwargs)

        self.filename = filename
        self.path = path
        self.length = length
        self.date = date
        self.is_usb = is_usb

        ##Format filename for display
        filename_no_ext = filename.replace('.gcode', '').replace('.gco', '')
        #Format spacing between filename and date
        if len(filename_no_ext) > 10:
            #filename_no_ext = filename_no_ext[:13] + '...' + filename_no_ext[-4:]
            self.ids.filename.text = filename_no_ext
            self.ids.date.text = date
        else:
            self.ids.filename.text = filename_no_ext
            self.ids.date.text = date



class FilesTab(TabbedPanelHeader):
    """
    Represents the Files tab header and dynamic content
    """
    pass



class FilesContent(BoxLayout):
    """
    This class represents the properties and methods necessary to render the dynamic components of the FilesTab

    Files content is a Boxlayout made up of 2 boxes: files list (widget type == ScrollView) and scrolling buttons (widget type == Gridlayout)
    self.update() handles generating the Files content and it will generate only when the files list changes; such as when a user adds a file via the webapp or ios app
    """
    files = ObjectProperty([])
    has_usb_attached = BooleanProperty(False)
    screen_lock = False
    usb_lock = False

    def __init__(self, **kwargs):
        super(FilesContent, self).__init__(**kwargs)
        Clock.schedule_interval(self.collect_meta_data, 0.1)
    #This function uses a shared funtion in the Meta Reader Plugin to collect information from a pipe
    #without disturbing the main thread
    def collect_meta_data(self, dt):
        roboprinter.printer_instance.collect_data()



    def create_file_button(self, filename, metadata, is_usb=False):
        """
        Returns a button widget based on the filename defined in parameter
        """

        try:
            length = math.ceil(metadata['analysis']['filament']['tool0']['length'])/1000
            date = str(metadata['date'])
            path = 'local'  # TODO remove hardcoding and utitlize path defined in self.update()
        except Exception as e: #because octoprint's analysis tool hasn't appended an analysis result to the file's metadata.
            length = ' -- '
            date = str(metadata['date'])
            path = 'local'

        if is_usb:
            return FileButton(filename=filename, length=length, date=date, path=path, is_usb=True, color=(1,0,0,1))
        return FileButton(filename=filename, length=length, date=date, path=path)

    def create_scroll_view(self):
        scroll = ScrollView(id='files_scroll_view', do_scroll_x=False, do_scroll_y=False, size_hint_y=1, size_hint_x=0.8, effect_cls=ScrollEffect)
        return scroll

    def create_layout(self):
        layout = GridLayout(cols=1, padding=0, spacing=0, size_hint_x=1, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        return layout

    def create_up_down_button(self):
        gridlayout = GridLayout(rows=2, size_hint_x=0.2, spacing=20, background_color=(0, 0, 0, 1), padding=(10,10,10,10))
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
        Logger.info('bar: {}'.format(self.scroll.vbar))

    def down_action_file(self, *args):
        scroll_distance = 0.4
        #makes sure that user cannot scroll into the negative space
        if self.scroll.scroll_y - scroll_distance < 0:
            scroll_distance = self.scroll.scroll_y
        self.scroll.scroll_y -= scroll_distance
        Logger.info('bar: {}'.format(self.scroll.vbar))


    def update(self, dt):
        '''
        finds gcode files in usb. If any, writes symlinks to local folder. These usb files get written to Files list and shown to user
        '''
        try:

            #find files in the USB first in order to catch symlink errors
            if os.path.isdir(USB_DIR):
                if len(os.listdir(USB_DIR)) != 0 and self.usb_lock == False:
                    Logger.info("USB Inserted")
                    self.usb_popup = USB_Progress_Popup("Importing USB Files", 200) #throw the error up without updating anything
                    self.usb_popup.show()
                    self.usb_lock = True
                    #fire off this in half a second so the USB warning has time to start up
                    Clock.schedule_once(self.usb_worker, 0.5)
                elif len(os.listdir(USB_DIR)) == 0 and self.usb_lock == True:
                    Logger.info("USB Removed")
                    self.usb_lock = False
                    self.has_usb_attached = False
                    self._delete_symlinks()


            current_files = self._grab_local_files()
            if len(current_files) != len(self.files):
                Logger.info( "current files length: " + str(len(current_files)) + " Self.Files length: " + str(len(self.files))) 
                self._update_files_list(current_files)

                #helper function from the Meta Rader
                roboprinter.printer_instance.start_analysis()

            
        except Exception as e:
            Logger.info("USB Removed")
            self.usb_lock = False
            self.has_usb_attached = False
            self._delete_symlinks()
            Logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! "+ str(e))
            traceback.print_exc()

        
    def usb_worker(self,dt):
       
        #find the amount of files that we have in the usb
        usb_files = self._find_gcode_in_usb()
        self.usb_popup.update_max(len(usb_files))
        if usb_files and not self.has_usb_attached: #new usb device attached
            self.has_usb_attached = True
            self._delete_symlinks() #clear all symlinks from local before writing to avoid any possible duplicates
            self._write_symlinks(usb_files)
        elif not usb_files and self.has_usb_attached: #usb device detached
            self.has_usb_attached = False
            self._delete_symlinks()

        #get rid of popup 
        self.usb_popup.hide()

    def _grab_local_files(self):
        return roboprinter.printer_instance._file_manager.list_files()['local']

    def _find_gcode_in_usb(self):
        arbitraty_counter = 0
        gcode_files = {}
        for r, d, files in os.walk(USB_DIR):
            for f in files:
                if (f.endswith('.gcode') or f.endswith('.gco')) and not f.startswith('._') :
                    path = r + '/' + f
                    gcode_files[f] = path
                    arbitraty_counter += 1
                    self.usb_popup.update_progress(arbitraty_counter)
                else:
                    continue
        return gcode_files

    def _find_symlinks(self):
        links = []
        for r, d, files in os.walk(FILES_DIR):
            for f in files:
                if '.usb.gcode' in f or 'usb.gco' in f:
                    links.append(r + '/' + f)
                else:
                    continue
        return links

    def _delete_symlinks(self):
        # deletes  gcode files that are symlinked to their counterparts that are stored in the usb storage device.
        links = self._find_symlinks()
        for l in links:
            os.unlink(l)

    def _append_usb_tag(self, filename):
        n, e = os.path.splitext(filename)
        return n + '.usb' + e

    def _write_symlinks(self, files):
        # writes local symlinks for the files found in USB storage device
        file_counter = 0
        links = []
        for name, path in files.iteritems():
            s_name = roboprinter.printer_instance._file_manager.sanitize_name('local',name) #sanitize the name according to octoprint standards
            new_name = self._append_usb_tag(s_name)
            new_path = FILES_DIR + '/' + new_name
            os.symlink(path, new_path)
            links.append(new_name)
            #add one to the file_counter
            file_counter += 1
            self.usb_popup.update_progress(file_counter)
        return links

    def _update_files_list(self, current_files):

        #find the current tab
        current_tab = roboprinter.open_tab
        self.files = current_files
        self._update_file_screen()

        # #if we are on the files tab we should run a callback that waits for the screen to change and then populates the file changes
        # if current_tab == "file_screen":
        #     #callback or wait
        #     if not self.screen_lock:
        #         self.screen_lock = True
        #         self._update_file_screen()
        #         #start callback


        # else:
            
        #     self._update_file_screen()

    def _update_file_screen(self):
        self.clear_widgets()
        buttons = []


        for fm, md in self.files.iteritems():
            name, ext = os.path.splitext(fm)
            if name.endswith('.usb'):
                buttons.append(self.create_file_button(fm, md, is_usb=True))
            else:
                if not self._is_gcode(md): continue
                buttons.append(self.create_file_button(fm, md))


        sorted_buttons = self.order_buttons_by_date(buttons)

        self.scroll = Scroll_Box_Even(sorted_buttons)
        self.add_widget(self.scroll)


    def wait_for_screen_change(self, dt):
        current_tab = roboprinter.open_tab

        if current_tab != "file_screen":
            self.screen_lock = False
            self._update_file_screen()
            return False




    def _is_gcode(self, metadata):
        return metadata['type'] == 'machinecode'

    def order_buttons_by_date(self, button_array):

        date_array = []

        for button in button_array:
            button_raw_date = int(button.ids.date.text)
            button.ids.date.text = datetime.fromtimestamp(int(button.ids.date.text)).strftime("%b %d")
            date_array.append([button,button_raw_date])

        date_array.sort(key=lambda date: date[1], reverse=True)

        sorted_array = []

        for button in date_array:
            sorted_array.append(button[0])

        return sorted_array




class PrintFile(GridLayout):
    """
    This class encapsulates the dynamic properties that get rendered on the PrintFile and the methods that allow the user to start a print.
    """


    name = StringProperty('')
    backbutton_name = ObjectProperty(None)
    file_name = ObjectProperty(None)
    print_layer_height = ObjectProperty(None)
    print_layers = ObjectProperty(None)
    print_length = ObjectProperty(None)
    hours = NumericProperty(0)
    minutes = NumericProperty(0)
    seconds = NumericProperty(0)
    infill = ObjectProperty(None)
    file_path = ObjectProperty(None)
    status = StringProperty('--')
    subtract_amount = NumericProperty(30)
    current_z_offset = StringProperty('--')

    def __init__(self, **kwargs):
        super(PrintFile, self).__init__(**kwargs)

        self.status = self.is_ready_to_print()
        Clock.schedule_interval(self.update, .1)

        self.current_z_offset = str(pconsole.zoffset['Z'])

        cura_meta = self.check_saved_data()
        self.print_layer_height = '--'
        self.print_layers = '--'
        self.infill = '--'
        self.hours = 0
        self.minutes = 0
        self.seconds = 0

        if cura_meta != False:
            if 'layer height' in cura_meta:
                self.print_layer_height = cura_meta['layer height']
            else:
                self.print_layer_height = "--"
            if 'layers' in cura_meta:
                self.print_layers = cura_meta['layers']
            else:
                layers = "--"
            if 'infill' in cura_meta:
                self.infill = cura_meta['infill']
            else:
                infill = "--"

            if 'time' in cura_meta:
                self.hours = int(cura_meta['time']['hours'])
                self.minutes = int(cura_meta['time']['minutes'])
                self.seconds = int(cura_meta['time']['seconds'])
            else:
                self.hours = 0
                self.minutes = 0
                self.seconds = 0

        else:
            self.print_layer_height = '--'
            self.print_layers = '--'
            self.infill = '--'
            self.hours = 0
            self.minutes = 0
            self.seconds = 0

    #This function will check the filename against saved data on the machine and return saved meta data
    def check_saved_data(self):
        self.octo_meta = roboprinter.printer_instance._file_manager
        saved_data = self.octo_meta.get_metadata(octoprint.filemanager.FileDestinations.LOCAL, self.file_name)


        if 'robo_data' in saved_data:
            return saved_data['robo_data']
        else:
            return False


    def update(self, dt):
        if roboprinter.printer_instance._printer.is_paused():
            self.status = 'PRINTER IS BUSY'
        else:
            self.status = self.is_ready_to_print()
        #toggle between button states
        if self.status == 'PRINTER IS BUSY' and self.ids.start.background_normal == "Icons/green_button_style.png":
            self.ids.start.background_normal = "Icons/red_button_style.png"
            self.ids.start_label.text = '[size=30]Printer Busy[/size]'
            self.ids.start_icon.source = 'Icons/Manual_Control/printer_button_icon.png'
            self.subtract_amount = 80
        elif self.status == "READY TO PRINT" and self.ids.start.background_normal == "Icons/red_button_style.png":
            self.ids.start.background_normal = "Icons/green_button_style.png"
            self.ids.start_label.text = '[size=30]Start[/size]'
            self.ids.start_icon.source = 'Icons/Manual_Control/start_button_icon.png'
            self.subtract_amount = 30

    def start_print(self, *args):
        #Throw a popup to display the ZOffset if the ZOffset is -10 or more
        try:
            if self.status == "READY TO PRINT":
                _offset = pconsole.zoffset['Z']

                if _offset <= -20 or _offset >= 0:
                    zoff = Zoffset_Warning_Popup(self)
                    zoff.open()
                else:
                    """Starts print but cannot start a print when the printer is busy"""
                    Logger.info(self.file_path)
                    path_on_disk = roboprinter.printer_instance._file_manager.path_on_disk(self.file_path, self.file_name)
                    roboprinter.printer_instance._printer.select_file(path=path_on_disk, sd=False, printAfterSelect=True)
                    Logger.info('Funtion Call: start_print')
        except Exception as e:
            #raise error
            error = Error_Popup('File Error','There was an error with the selected file\nPlease try again')
            error.open()
            Logger.info(e)

    def force_start_print(self, *args):
        """Starts print but cannot start a print when the printer is busy"""
        try:
            path_on_disk = roboprinter.printer_instance._file_manager.path_on_disk(self.file_path, self.file_name)
            roboprinter.printer_instance._printer.select_file(path=path_on_disk, sd=False, printAfterSelect=True)
            Logger.info('Funtion Call: start_print')
        except Exception as e:
            #raise error
            error = Error_Popup('File Error','There was an error with the selected file\nPlease try again')
            error.open()





    def is_ready_to_print(self):
        """ whether the printer is currently operational and ready for a new print job"""
        is_ready = roboprinter.printer_instance._printer.is_ready()
        printing = roboprinter.printer_instance._printer.is_printing()
        if is_ready and not printing:
            return 'READY TO PRINT'
        else:
            return 'PRINTER IS BUSY'

class PrintUSB(PrintFile):
    """
        This class encapsulates the dynamic properties that get rendered on the PrintUSB and the methods that allow the user to start a print from usb or save the file to local.
    """
    def save_file_to_local(self, *args):
        try:
            usb_removed = self.file_name.replace('.usb', '')
            link_path = FILES_DIR + '/' + self.file_name
            copy_path = FILES_DIR + '/' + usb_removed
            real_path = os.readlink(link_path)

            shutil.copy2(real_path, copy_path)
            os.unlink(link_path)
        except Exception as e:
            #raise error
            Error_Popup('File Error','There was an error with the selected file\nPlease try again')
