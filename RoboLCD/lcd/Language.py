import yaml
import os

class Language():
    def __init__(self, language):
        acceptable_languages = {'english': "Language_Packs/english.yaml",
                                'giberish': 'Language_Packs/giberish.yaml'}

        if language in acceptable_languages:
            _dir = os.path.dirname(__file__)
            yaml_path = os.path.join(_dir, acceptable_languages[language])
            with open(yaml_path, 'r') as file:
                self.pack = yaml.load(file)

    def reload_language(self, language):
        self.__init__(language)

language = Language('english')

                    