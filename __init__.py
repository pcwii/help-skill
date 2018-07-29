from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler, intent_file_handler
from mycroft.util.log import getLogger
from mycroft.skills.context import adds_context, removes_context

import re
import os
from pathlib import Path

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
        self.skill_directories = []
        self.skill_names = []
        self.skill_quantity = 0

    def initialize(self):
        self.load_data_files(dirname(__file__))

    def scrape_readme_file(self, file_path):
        file_name = 'README.md'
        self.description_data = False
        self.description_list = []
        self.example_data = False
        self.example_list = []
        test_file = Path(file_path + '/' + file_name)  # check if the readme file exists
        if test_file.exists():
            with open(file_path + '/' + file_name, 'r', errors='ignore') as myfile:
                data = myfile.readlines()
                for each_line in data:
                    if re.search('##', each_line, re.I):  # check for the ## header flag in the readme
                        if re.search('Description', each_line, re.I):  # start of the Description section
                            self.description_data = True
                            self.example_data = False
                        # print('Found Description')
                        elif re.search('Examples', each_line, re.I):  # start of the Examples section
                            self.example_data = True
                            self.description_data = False
                            # print('Found Examples')
                        else:  # some other section was detected end processing
                            self.description_data = False
                            self.example_data = False
                    elif self.description_data:  # The description section was detected, continue parsing
                        each_line = re.sub('[*\n"]+', '', each_line)
                        each_line = each_line.strip()
                        if len(each_line) > 0:
                            self.description_list.append(each_line)
                    elif self.example_data:  # The example section was detected, continue parsing
                        each_line = re.sub('[*\n"]+', '', each_line)
                        each_line = each_line.strip()
                        if len(each_line) > 0:
                            self.example_list.append(each_line)
                if len(self.description_list) > 0:  # The description section contained no information for this skill
                    print(self.description_list)
                if len(self.example_list) > 0:  # The example section contained no information for this skill
                    print(self.example_list)
        else:
            vocal_response = "I am sorry, I had trouble locating the skills directory"
            print(vocal_response)

    def get_skills_list(self):
        self.skill_directories = []
        self.skill_names = []
        self.skill_quantity = 0
        location = os.path.dirname(os.path.realpath(__file__))
        location = location + '/../'  # get skill parent directory path
        for name in os.listdir(location):
            path = os.path.join(location, name)
            if os.path.isdir(path):  # if path item is a directory then process
                self.skill_directories.append(path)  # Directory path list
                # Todo Need to run the name through regex to remove the "skill" and "-" portions from the "name"
                self.skill_names.append(name)  # Skill name list based on the path
        print(self.skill_directories)  # For debugging only
        print(self.skill_names)  # For debugging only
        self.skill_quantity = len(self.skill_names)  # The number of skills detected
    #    for each_skill in skill_names:  # obtain the description and examples for each of the readme files
    #        scrape_readme_file(skill_directories[int(skill_names.index(each_skill))])  # index begins at 0

    @intent_handler(IntentBuilder('HelpStartIntent').require("HelpKeyword")
                    .build())
    @adds_context('HelpChat')
    def handle_help_start_intent(self, message):
        self.get_skills_list()
        vocal_response = "i can tell you a bit about the skills installed on your system. I currently detect, " .\
            + str(self.skill_quantity) + ", installed on your system, would you like to know more about these skills?"
        self.speak_dialog("response.modifier", data={"result": vocal_response}, expect_response=False)

    def stop(self):
        pass


def create_skill():
    return HelpSkill()
