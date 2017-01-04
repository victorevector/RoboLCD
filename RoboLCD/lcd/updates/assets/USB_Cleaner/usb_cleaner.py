import os
import shutil

FILES_DIR = '/home/pi/.octoprint/uploads' 

class USB_Cleaner():
    def __init__(self):
        self._delete_symlinks()

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

usb_cleaner = USB_Cleaner()
