from kivy.uix.floatlayout import FloatLayout
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.properties import StringProperty
import yaml
import os
import imp
import requests
from git import Repo
from .. import roboprinter
from connection_popup import Error_Popup

class UpdateScreen(FloatLayout):
    installed_version = StringProperty('Checking...')
    avail_version = StringProperty('Checking...')

    def __init__(self):
        super(UpdateScreen, self).__init__()

        self.data_path = roboprinter.printer_instance.get_plugin_data_folder()

        self.repo_info_url = 'https://api.github.com/repos/robo3d/Update_Script/releases'
        self.repo_local_path = self.data_path + '/Update_Script'
        self.updater_path = self.repo_local_path + '/Update_Checker/Update_Checker.py'
        self.repo_remote_path = 'https://github.com/Robo3d/Update_Script.git'
        self.versioning_path = self.data_path + '/roboOS.txt'

        self.printer_model = roboprinter.printer_instance._settings.get(['Model'])

        #populate version numbers when screen gets initiated
        Clock.schedule_once(self.populate_values)

    def populate_values(self, *args):
        self.refresh_versions()
        self.refresh_button()

    def refresh_button(self, *args):
        if self.installed_version < self.avail_version and self.avail_version != "Connection Error!":
            self.enable_me()
        else:
            self.disable_me()

    def refresh_versions(self, *args):
        """populates self.installed_version && self.avail_version: values are rendered on the UpdateScreen."""
        self.installed_version = self.get_installed_version()
        self.avail_version = self.get_avail_version()
        if self.avail_version == 'Connection Error!':
            Error_Popup('Connection Error', 'Check internet connection.').show()

    def get_installed_version(self):
        path = self.versioning_path
        if os.path.exists(path):
            with open(path, 'r') as f:
                v = f.readline().strip()
        else:
            with open(path, 'w') as f:
                v = '1.0.3'
                f.write(v)
        return v

    def get_avail_version(self):
        """queries github api for repo's latest release version"""
        try:
            r = requests.get(self.repo_info_url)
            code = r.status_code
        except Exception as e:
            r = None
            code = None
        if r and code is 200:
            return self._get_avail_version(r.json())
        else:
            return "Connection Error!"

    def _get_avail_version(self, r):
        # parse json response for latest release version
        versions = map(lambda info: info.get('name', 0), r)
        versions.sort()
        return versions.pop()

    def update_updater(self, *args):
        if self.printer_model == 'Robo R2':
            branch = 'r2'
        else:
            branch = 'c2'

        if os.path.exists(self.repo_local_path):
            repo = Repo(self.repo_local_path).git
            repo.pull()
            repo.checkout(branch)
            repo.pull()
        else:
            Repo.clone_from(self.repo_remote_path, self.repo_local_path, branch=branch)

    def run_updater(self, *args):
        self.disable_me()
        self.update_updater()
        self._run_updater()

    def _run_updater(self):
        from multiprocessing import Process, Pipe
        import subprocess
        import time

        output_p, input_p = Pipe()
        Update_Checker = imp.load_source('Update_Checker', self.updater_path).Update_Checker
        Logger.info('!!!!UPDATING!!!!')
        p = Process(
            target=Update_Checker,
            args=(
                self.versioning_path,
                (output_p, input_p),
            )
        )
        p.start()
        input_p.close()
        # receive message from updater on update status
        while True:
            try:
                updating = output_p.recv()
                Logger.info('MESSAGE: {}'.format(updating))
            except EOFError:
                break
        if updating:
            # kill parent process Octoprint
            subprocess.call("sudo service octoprint stop".split(' '))
        else:
            p.join()


    def disable_me(self):
        self.ids.updatebtn.disabled = True
        self.ids.updatebtn.canvas.ask_update()
        # Clock.schedule_once(self.run_updater)
    def enable_me(self):
        self.ids.updatebtn.disabled = False
        self.ids.updatebtn.canvas.ask_update()
