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

        Clock.schedule_once(self.refresh_versions)

    def refresh_versions(self, *args):
        """populates self.installed_version && self.avail_version"""
        self.installed_version = self._installed_version()
        self.avail_version = self.latest_version()

    def _installed_version(self):
        path = self.versioning_path
        if os.path.exists(path):
            with open(path, 'r') as f:
                v = f.readline().strip()
        else:
            with open(path, 'w') as f:
                v = '1.0.3'
                f.write(v)
        return v

    def latest_version(self):
        """queries github api for repo's latest release version"""
        try:
            r = requests.get(self.repo_info_url)
            code = r.status_code
        except Exception as e:
            r = None
            code = None
        if r and code is 200:
            return self._latest_version(r.json())
        else:
            return 'Error'

    def _latest_version(self, r):
        # parse json response for latest release version
        versions = map(lambda info: info.get('name', 0), r)
        versions.sort()
        return versions.pop()

    def update_updater(self, *args):
        if os.path.exists(self.repo_local_path):
            repo = Repo(self.repo_local_path)
            repo.remote().pull()
        else:
            Repo.clone_from(self.repo_remote_path, self.repo_local_path, branch='master')

    def run_updater(self, *args):
        self.disable_me()
        self.update_updater()
        self._run_updater()

    def _run_updater(self):
        from multiprocessing import Process
        Update_Checker = imp.load_source('Update_Checker', self.updater_path).Update_Checker
        Logger.info('UPDATING!!!!!!!!!!!!!')
        p = Process(target=Update_Checker, args=(self.versioning_path,))
        p.start()

    def disable_me(self):
        self.ids.updatebtn.disabled = True
        self.ids.updatebtn.canvas.ask_update()
        # Clock.schedule_once(self.run_updater)
