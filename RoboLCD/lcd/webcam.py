import subprocess
from kivy.logger import Logger
from fine_tune_zoffset import Title_Button_Screen
from .. import roboprinter
from kivy.clock import Clock

class webcam():
    def __init__(self):
        pass
    #get state of the webcam
    def get_cam(self):
        webcam = False
        try:
            pid = subprocess.check_output(['pgrep', "mjpg_streamer"] )
            if pid:
                webcam = True
        except Exception as e:
            # Logger.info("Error Occured in Webcam Class")
            pass
        return webcam
    def start(self):
        subprocess.call(['/home/pi/scripts/webcam start'], shell=True)
    def stop(self):
        subprocess.call(['/home/pi/scripts/webcam stop'], shell=True)

class Camera(Title_Button_Screen):
    #title_text, body_text, button_function, button_text = "OK", **kwargs
    def __init__(self):
        self.webcam = webcam()
        self.title_text = "Checking Status"
        self.body_text = "Please use the button below to toggle the\nstate of the webcam"
        self.button_text = "Checking State"
        self.check_state()
        Clock.schedule_interval(self.check_status, 0.2)        
        super(Camera, self).__init__(self.title_text, self.body_text, self.button_function, button_text=self.button_text)

    def check_state(self):
        self.cam_on = self.webcam.get_cam()
        self.title_text = "Webcam is on" if self.cam_on else "Webcam is off"
        self.body_text = "Please use the button below to toggle the\nstate of the webcam"
        self.button_text = "Off" if self.cam_on else "On"
        self.button_function = self.webcam.stop if self.cam_on else self.webcam.start


    def check_status(self, dt):
        self.check_state()

        #exit the clock if we arent on the screen anymore
        if roboprinter.robosm.current != 'webcam_status':
            return False




