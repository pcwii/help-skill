from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler, intent_file_handler
from mycroft.util.log import getLogger
from mycroft.skills.context import adds_context, removes_context
from mycroft.audio import wait_while_speaking

import re
import os
from pathlib import Path

_author__ = 'PCWii'
# Release - 20180729

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
        self.skill_index = 0

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
            self.speak_dialog("location.error", expect_response=False)
            wait_while_speaking()
            self.stop_help_chat()

    def get_skills_list(self):
        self.skill_directories = []
        self.skill_names = []
        self.skill_quantity = 0
        location = os.path.dirname(os.path.realpath(__file__))
        location = location + '/../'  # get skill parent directory path
        for name in os.listdir(location):
            path = os.path.join(location, name)
            if os.path.isdir(path):  # if path item is a directory then process
                if "fallback" not in name:
                    if "skill" in name:
                        self.skill_directories.append(path)  # Directory path list
                        self.skill_names.append(name)  # Skill name list based on the path
        self.skill_quantity = len(self.skill_names)  # The number of skills detected

    @intent_handler(IntentBuilder('HelpStartIntent').require("HelpKeyword")
                    .build())
    @adds_context('HelpChat')
    @removes_context('SearchChat')
    def handle_help_start_intent(self, message):  # The user requested help
        self.get_skills_list()
        self.speak_dialog('help.start', data={"result": str(self.skill_quantity)}, expect_response=True)

    @intent_handler(IntentBuilder('HelpChatIntent').require("YesKeyword").require('HelpChat')
                    .build())
    @adds_context('HelpChat')
    @removes_context('SearchChat')
    def handle_help_chat_intent(self, message):  # The user requires more help
        self.skill_index = 0
        self.speak_dialog('help.chat', data={"qty_result": str(self.skill_quantity),
                                             "name_result": self.skill_names[self.skill_index]},
                          expect_response=True)
        wait_while_speaking()

    @intent_handler(IntentBuilder('HelpChatDecisionIntent').require("DecisionKeyword").require('HelpChat')
                    .build())
    @adds_context('HelpChat')
    @adds_context('SearchChat')
    def handle_help_chat_decision_intent(self, message):  # A decision was made other than Cancel
        decision_kw = message.data.get('DecisionKeyword')
        if decision_kw == "moore":
            decision_kw = "more"
        if decision_kw == "more":
            self.more_help_item()
        if decision_kw == "next":
            self.next_help_item()
        if decision_kw == "search":
            self.search_help_item()

    @intent_handler(IntentBuilder('SearchHelpIntent').require('SearchChat').require('SkillName')
                    .build())  # regex searches must reference the regex search term not the rx filename
    @removes_context('SearchChat')
    def handle_search_help_intent(self, message):  # A decision was made other than Cancel
        LOGGER.info('--LOG(handle_search_help_intent)--')
        LOGGER.info('--')
        LOGGER.info(message.data.get('SkillName'))
        LOGGER.info('--END LOGGING--')
        search_skill = message.data.get('SkillName')
        search_skill.replace('skill', '')
        if "cancel" in search_skill:
            self.stop_help_chat()
        else:
            for each_skill in self.skill_names:
                if search_skill in each_skill:
                    self.skill_index = self.skill_names.index(each_skill)
                    self.read_search_help_item()
                else:
                    self.speak_dialog('location.error', data={"result": search_skill}, expect_response=False)
                    wait_while_speaking()

    @adds_context('HelpChat')
    @removes_context('SearchChat')
    def next_help_item(self):
        self.skill_index += 1
        LOGGER.info('--LOG(next_help_item)--')
        LOGGER.info('skill index: ' + str(self.skill_index))
        LOGGER.info('skill length: ' + str(len(self.skill_names)))
        LOGGER.info('--END LOGGING--')
        if self.skill_index < len(self.skill_names):
            self.speak_dialog('next.help', data={"result": self.skill_names[self.skill_index]}, expect_response=True)
            wait_while_speaking()
        else:
            self.speak_dialog("search.end", expect_response=False)
            wait_while_speaking()
            self.stop_help_chat()

    @adds_context('HelpChat')
    @removes_context('SearchChat')
    def more_help_item(self):
        self.scrape_readme_file(self.skill_directories[self.skill_index])
        for phrase in self.example_list:
            self.speak_dialog('joining.words', data={"result": phrase}, expect_response=False)
            wait_while_speaking()
        self.next_help_item()

    @removes_context('HelpChat')
    @removes_context('SearchChat')
    def read_search_help_item(self):
        self.scrape_readme_file(self.skill_directories[self.skill_index])
        for phrase in self.example_list:
            self.speak_dialog('joining.words', data={"result": phrase}, expect_response=False)
            wait_while_speaking()

    @removes_context('HelpChat')
    @adds_context('SearchChat')
    def search_help_item(self):
        self.speak_dialog('search.for', expect_response=True)
        wait_while_speaking()

    @intent_handler(IntentBuilder('HelpChatCancelIntent').require("CancelKeyword").require('HelpChat')
                    .build())
    @removes_context('HelpChat')
    @removes_context('SearchChat')
    def handle_cancel_help_chat_intent(self):  # Cancel was spoken, Cancel the list navigation
        self.speak_dialog('search.cancel', expect_response=False)

    @removes_context('HelpChat')
    @removes_context('SearchChat')
    def stop_help_chat(self):  # An internal conversational context stoppage was issued
        self.speak_dialog('search.cancel', expect_response=False)

    def stop(self):
        pass


def create_skill():
    return HelpSkill()
