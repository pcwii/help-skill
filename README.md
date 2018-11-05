# Help Skill for Mycroft AI
## help-skill
Scrapes the skills directory to provide conversational help on installed skills
based on the standard skill README.md file layout recomended by the mycroft.ai team.

## Description 
This skill will provide conversational help for the installed skills by scraping the Readme files for any examples.
## Examples
* "help"
* "what can you do?"
* "how do I use kodi skill"
## Conversational Context
* The help skill uses a complex conversational context sequence to list all the installed skills and provide
any examples of the selected skill that may be found in the Examples section of the README.md file for the skill.
## Credits
PCWii
## Require 
Tested on platform_picroft (others untested) 
## Other Requirements
- [Mycroft](https://docs.mycroft.ai/installing.and.running/installation)
## Further Reading
- None
## Installation Notes
- msm install https://github.com/pcwii/help-skill.git
## ToDo
- implement options for available, not installed skills
- How do I use "named skill"
