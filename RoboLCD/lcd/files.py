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
from kivy.core.window import Window
from kivy.uix.vkeyboard import VKeyboard

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from file_explorer import File_Explorer
from file_explorer import FileOptions
import re


USB_DIR = '/home/pi/.octoprint/uploads/USB'
FILES_DIR = '/home/pi/.octoprint/uploads'

class FileButton(Button):
    def __init__(self, filename, date, path, is_usb = False, **kwargs):
        super(FileButton, self).__init__(**kwargs)

        self.filename = filename
        self.path = path
        self.date = date
        self.is_usb = is_usb
        self.long_press = False

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

    def file_on_press(self):
        self.file_clock = Clock.schedule_once(self.file_clock_event, 1.0)
        pass

    def file_on_release(self):
        if not self.long_press:
            self.file_clock.cancel()
            roboprinter.robosm.generate_file_screen(filename=self.filename, file_path=self.path, is_usb=self.is_usb)
        else:
            self.long_press = False
        

    def file_clock_event(self, dt):
        # self.long_press = True
        # FileOptions(self.filename, self.path)
        pass # re enable for file options


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

    def __init__(self, **kwargs):
        super(FilesContent, self).__init__(**kwargs)
        Clock.schedule_interval(self.collect_meta_data, 0.1)

        #if octoprint has changed files then update them
        session_saver.save_variable('file_callback', self.call_to_update)
        session_saver.save_variable('usb_mounted', False)
        
        #schedule directory observer http://pythonhosted.org/watchdog/api.html#watchdog.events.FileSystemEventHandler
        self.dir_observe = Observer()
        self.callback = FileSystemEventHandler()
        self.callback.on_any_event = self.on_any_event
        self.dir_observe.schedule(self.callback, "/dev/", recursive=True)
        self.dir_observe.start()


        self.update_files()

    
    #This seems like a roundabout way to call 'update_files' However if it is not called in this way Graphical issues become present.
    #It is called in this way to make the request come from the thread kivy is on
    def call_to_update(self):
        Clock.schedule_once(self.call_to_update2, 0.01)
    def call_to_update2(self ,dt):
        self.update_files()

    def call_to_analyze(self,dt):
        
        roboprinter.printer_instance.start_analysis(files=session_saver.saved['current_files'])

    def update_files(self):
        files = File_Explorer('machinecode', FileButton, enable_editing=True)
        self.clear_widgets()
        self.add_widget(files)
        #helper function from the Meta Rader
        Clock.schedule_once(self.call_to_analyze, 0.01)

    #This function is a callback from an observer that is watching /dev for any device changes. Namely the USB being plugged in
    def on_any_event(self, event):
        usb_path = "/dev/sd"
        extern = re.match(usb_path, event.src_path)

        if extern != None and event.src_path.endswith('1'):

            if event.event_type == 'deleted':
                Logger.info("USB Removed " + event.src_path)
                session_saver.saved['usb_mounted'] = False
                self.has_usb_attached = False
                self.call_to_update()
                

            elif event.event_type == 'created':
                Logger.info("USB Plugged in " + event.src_path)
                session_saver.saved['usb_mounted'] = True
                session_saver.saved['usb_location'] = event.src_path
                self.has_usb_attached = True
                self.call_to_update()
            
    #This function uses a shared funtion in the Meta Reader Plugin to collect information from a pipe
    #without disturbing the main thread
    def collect_meta_data(self, dt):
        roboprinter.printer_instance.collect_data()

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
        saved_data = self.octo_meta.get_metadata(octoprint.filemanager.FileDestinations.LOCAL , self.file_path)


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
                    path_on_disk = roboprinter.printer_instance._file_manager.path_on_disk(octoprint.filemanager.FileDestinations.LOCAL, self.file_path)
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
    def __init__(self, **kwargs):
        super(PrintUSB, self).__init__(**kwargs)
        self.progress_pop =  USB_Progress_Popup("Saving File", 1)
        pass


    def save_file_to_local(self, *args):
        self.progress_pop.show()

        Clock.schedule_once(self.attempt_to_save, 0.01)

        

    def attempt_to_save(self, dt):
        try:
            copy_path = FILES_DIR + '/' + self.file_name
            real_path = roboprinter.printer_instance._file_manager.path_on_disk('local', self.file_path)

            #shutil.copy2(real_path, copy_path)
            Logger.info("Started the Copy src: " + real_path + " cp to dst: " + copy_path )
            copied = self.copy_file(real_path, copy_path, progress_callback=self.progress_update)
            if not copied:
                self.progress_pop.hide()
                ep = Error_Popup('File Error','There was an error with the selected file\nPlease try again')
                ep.show()
            

        except Exception as e:
            #raise error
            self.progress_pop.hide()
            ep = Error_Popup('File Error','There was an error with the selected file\nPlease try again')
            ep.show()
            Logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! "+ str(e))
            traceback.print_exc()


    def copy_file(self, fsrc, fdst, progress_callback=None, complete_callback = None, length=16*1024, **kwargs):
        
        self.copied = 0
        self.file_size = 0
        self.length = length
        self.p_callback = progress_callback
        self.c_callback = complete_callback
        if not os.path.isfile(fsrc):
            Logger.info("Will not copy")
            return False

        else:
            self.file_size = float(os.path.getsize(fsrc))
        #make the new file
        self.src_obj = open(fsrc, 'rb')
        self.dst_obj = open(fdst, 'wb')
        #Do the copy as fast as possible without blocking the UI thread
        Clock.schedule_interval(self.copy_object, 0)
        
                    

        return True

    #doing it this way with a clock object does not block the UI
    def copy_object(self, dt):
        #grab part of the file
        buf = self.src_obj.read(self.length)
        #if there isn't anything to read then close the files and return
        if not buf:
            self.src_obj.close()
            self.dst_obj.close()
            if self.c_callback != None:
                self.c_callback()
            return False
        #Write the buffer to the new file
        self.dst_obj.write(buf)
        #update how much of the file has been copied
        self.copied += len(buf)
        
        #report progress
        if self.p_callback != None:
            progress = float(self.copied/self.file_size)
            self.p_callback(progress)

    def progress_update(self, progress):
        self.progress_pop.update_progress(progress)
        #Logger.info(str(progress))

        if progress == 1.0:
            self.progress_pop.hide()
            ep = Error_Popup('File Saved','File has been saved to\nthe local directory')
            ep.show()
            if 'file_callback' in session_saver.saved:
                session_saver.saved['file_callback']()


