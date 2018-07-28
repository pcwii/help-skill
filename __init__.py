from os.path import dirname
import time

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler, intent_file_handler
from mycroft.util.log import getLogger
from mycroft.skills.context import adds_context, removes_context

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
        self.my_skills = []
        self.skills_list = []
        self.my_intents = []
        self.intents_list = []

    def initialize(self):
        self.load_data_files(dirname(__file__))

    def get_skills_list(self):  # retrieves a list of skills
        return self.skills_list

    def get_skill_intent_list(self, skill_name):  # retrieves a list of possible commands
        return self.intents_list

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
