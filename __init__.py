from os.path import dirname
import os

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler, intent_file_handler
from mycroft.util.log import getLogger
from mycroft.skills.context import adds_context, removes_context

import re

_author__ = 'PCWii'
# Release - 20180713

LOGGER = getLogger(__name__)

class HelpSkill(MycroftSkill):
    """
    Scrapes the skills directory to provide conversational help on installed skills
    Utilize the testing json files to discover intents and provide help on installed skills.
    """
    def __init__(self):
        super(HelpSkill, self).__init__(name="HelpSkill")
        self.description_data = False
        self.description_list = []
        self.example_data = False
        self.example_list = []

    def initialize(self):
        self.load_data_files(dirname(__file__))

    def scrape_readme_file(self, file_path):
        file_name = 'README.md'
        self.description_data = False
        self.description_list = []
        self.example_data = False
        self.example_list = []
        with open(file_path + file_name, 'r') as readme_file:
            raw_data = readme_file.readlines()
            for each_line in raw_data:
                if re.search('##', each_line, re.I):
                    if re.search('Description', each_line, re.I):
                        self.description_data = True
                        self.example_data = False
                        print('Found Description')
                    elif re.search('Examples', each_line, re.I):
                        self.example_data = True
                        self.description_data = False
                        print('Found Examples')
                    else:
                        self.description_data = False
                        self.example_data = False
                elif self.description_data:
                    self.description_list.append(each_line)
                elif self.example_data:
                    self.example_list.append(each_line)
                else:
                    print('data not relevant')
            print(self.description_list)  # An iterated list of descrption items in the readme file
            print(self.example_list)  # An iterated list of examples found in the readme file

    def get_skills_list(self):  # retrieves a list of skills
        path = 'c:/Users/PhilC/Documents/'
        self.skill_names = []
        self.skill_directories = []
        for item_name in os.listdir(path):
            path = os.path.join(path, item_name)
            if os.path.isdir(path):
                self.skill_directories.append(path)
                self.skill_names.append(item_name)

    @intent_handler(IntentBuilder('HelpStartIntent').require("HelpKeyword")
                    .build())
    @adds_context('HelpChat')
    def handle_help_start_intent(self, message):
        self.my_skills = self.get_skills_list()

        self.speak_dialog('context', data={"result": ""}, expect_response=True)




    def stop(self):
        pass


def create_skill():
    return HelpSkill()
