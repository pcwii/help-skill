from os.path import dirname

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler, intent_file_handler
from mycroft.util.log import getLogger
from mycroft.skills.context import adds_context, removes_context
from mycroft.audio import wait_while_speaking
from mycroft.util.log import LOG

import re
import os
from pathlib import Path

_author__ = 'PCWii'
# Release - 20180729

LOGGER = getLogger(__name__)


class HelpSkill(MycroftSkill):
    """
    Scrapes the skills directory to provide conversational help on installed skills
    Utilize the readme.me files to discover intents and provide help on installed skills.
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
        LOG.info('Help Skill Scraping: ' + str(file_path))
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
                            LOG.info('Found Description')
                        elif re.search('Examples', each_line, re.I):  # start of the Examples section
                            self.example_data = True
                            self.description_data = False
                            LOG.info('Found Examples')
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
                    LOG.info(str(self.description_list))
                if len(self.example_list) > 0:  # The example section contained no information for this skill
                    LOG.info(str(self.example_list))
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
                        LOG.info('NOTICE: get_skills_list will only get skills that contain "skill" in the name and '
                                 'are not "fallback" skills')
                        self.skill_directories.append(path)  # Directory path list
                        self.skill_names.append(name)  # Skill name list based on the path
        self.skill_quantity = len(self.skill_names)  # The number of skills detected

    @intent_handler(IntentBuilder('HelpStartIntent').require("HelpKeyword")
                    .build())
    def handle_help_start_intent(self, message):  # The user requested help
        LOG.info('Help Skill Initiated')
        self.set_context('HelpStartContextKeyword', 'HelpStartContext')
        self.get_skills_list()
        self.speak_dialog('help.start', data={"result": str(self.skill_quantity)}, expect_response=True)

    @intent_handler(IntentBuilder('HelpChatYesIntent').require('HelpStartContextKeyword').require("YesKeyword")
                    .build())
    def handle_help_chat_yes_intent(self, message):  # The user requires more help
        LOG.info('The user requested more information about the installed skills')
        self.set_context('HelpStartContextKeyword', '')
        self.set_context('HelpListContextKeyword', 'HelpListContext')
        self.skill_index = 0
        self.speak_dialog('help.chat', data={"qty_result": str(self.skill_quantity),
                                             "name_result": self.skill_names[self.skill_index]},
                          expect_response=True)
        wait_while_speaking()

    @intent_handler(IntentBuilder('HelpChatNoIntent').require('HelpStartContextKeyword').require("CancelKeyword")
                    .build())
    def handle_help_chat_no_intent(self, message):  # The user requires more help
        LOG.info('The user requested a cancel')
        self.set_context('HelpStartContextKeyword', '')
        self.skill_index = 0
        self.speak_dialog('search.cancel', expect_response=False)
        wait_while_speaking()

    @intent_handler(IntentBuilder('HelpListCancelIntent').require('HelpListContextKeyword').require("CancelKeyword")
                    .build())
    def handle_help_list_cancel_intent(self, message):  # The user requires more help
        LOG.info('The user requested a cancel')
        self.set_context('HelpListContextKeyword', '')
        self.skill_index = 0
        self.speak_dialog('search.cancel', expect_response=False)
        wait_while_speaking()

    @intent_handler(IntentBuilder('HelpChatDecisionIntent').require('HelpListContextKeyword')
                    .require("DecisionKeyword").build())
    def handle_help_chat_decision_intent(self, message):  # A decision was made other than Cancel
        self.set_context('HelpListContextKeyword', 'HelpListContext')
        decision_kw = message.data.get('DecisionKeyword')
        LOGGER.info('--LOG(handle_help_chat_decision_intent)--')
        LOGGER.info('decision_kw: ' + str(decision_kw))
        LOGGER.info('--END LOGGING--')
        if any([decision_kw == "moore", decision_kw == "more"]):
            self.more_help_item()
        if decision_kw == "next":
            self.next_help_item()
        if decision_kw == "search":
            self.search_help_request_item()

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

    def more_help_item(self):
        self.scrape_readme_file(self.skill_directories[self.skill_index])
        for phrase in self.example_list:
            self.speak_dialog('joining.words', data={"result": phrase}, expect_response=False)
            wait_while_speaking()
        self.next_help_item()

    def read_search_help_item(self):
        self.scrape_readme_file(self.skill_directories[self.skill_index])
        for phrase in self.example_list:
            self.speak_dialog('example.phrases', data={"result": phrase}, expect_response=False)
            wait_while_speaking()
        self.stop_help_chat()


    def search_help_request_item(self):
        LOGGER.info('--LOG(search_help_item)--')
        self.set_context('HelpSearchContextKeyword', 'HelpSearchContext')
        self.speak_dialog('search.for', expect_response=True)

    @intent_handler(IntentBuilder('HelpSearchForIntent').require('HelpSearchContextKeyword')
                    .require('SkillName').build())
    def handle_help_search_for_intent(self, message):  # A decision was made other than Cancel
        self.set_context('HelpSearchContextKeyword', '')
        self.set_context('HelpListContextKeyword', '')
        LOG.info('help search for')
        request_skill = message.data.get("SkillName")
        LOGGER.info('request_skill: ' + str(request_skill))
        if not request_skill:
            LOGGER.info('get_response returned NONE')
            self.speak_dialog('skill.not.found',  data={"result": 'none'}, expect_response=False)
            self.stop_help_chat()
        else:
            for each_skill in self.skill_names:
                LOGGER.info('Checking skill: ' + str(request_skill))
                if request_skill in each_skill:
                    self.skill_index = self.skill_names.index(each_skill)
                    self.read_search_help_item()
                else:
                    self.speak_dialog('skill.not.found', data={"result": request_skill}, expect_response=False)
                    self.stop_help_chat()

    def stop_help_chat(self):  # An internal conversational context stoppage was issued
        self.speak_dialog('search.stop', expect_response=False)

    def stop(self):
        pass


def create_skill():
    return HelpSkill()
