# coding=utf-8
from __future__ import absolute_import
import octoprint.plugin

# import os
# import subprocess
import thread
import qrcode
from . import lcd
from . import roboprinter
from .lcd.pconsole import pconsole



class RobolcdPlugin(octoprint.plugin.SettingsPlugin, octoprint.plugin.AssetPlugin, octoprint.plugin.StartupPlugin):
    def _get_api_key(self):
        return self._settings.global_get(['api', 'key'])

    def _write_qr_to_file(self, api_key):
        folder = self.get_plugin_data_folder()
        img = qrcode.make(api_key)
        img.save('{}/{}'.format(folder, 'qr_code.png'))

    def on_after_startup(self):
        """
        Run this plugin when octoprint server has start up.
        1) Starts the kivy applicatio. function start() is called. it is located in ./lcd/__init__.py
        2) Converts Octoprint's API key to a QR code and saves it to file
        """
        self._logger.info("RoboLCD Starting up")
        # saves the printer instance so that it can be accessed by other modules
        roboprinter.printer_instance = self
        thread.start_new_thread(lcd.start, ())
        self._logger.info("Rendering screen... ")

        # writes printer's QR code to plugin data folder
        api_key = self._get_api_key()
        self._write_qr_to_file(api_key)

        self._logger.info('Preparing Callback to PConsole')
        self._printer.register_callback(pconsole)
        self._logger.info('Callback Complete')

        #get the helper function to determine if the board is updating or not

        helpers = self._plugin_manager.get_helpers("firmwareupdater", "firmware_updating")
        if helpers and "firmware_updating" in helpers:
            self._logger.info("Firmware updater has a helper function")
            self.firmware_updating = helpers["firmware_updating"]
        else :
            self._logger.info("Firmware updater does not have a helper function")
            self.firmware_updating = self.updater_placeholder

    def updater_placeholder(self):
        return False



    def get_update_information(self):
        return dict(
            robolcd=dict(
                displayName="RoboLCD",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="victorevector",
                repo="RoboLCD",
                current=self._plugin_version,

                # update method: pip w/ dependency links
                pip="https://github.com/victorevector/RoboLCD/archive/{target_version}.zip"
            )
        )


__plugin_name__ = "RoboLCD"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = RobolcdPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
