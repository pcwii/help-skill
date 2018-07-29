# testing the parsing of readme files
import re
import os
from pathlib import Path

def scrape_readme_file(file_path):
    file_name = 'README.md'
    description_data = False
    description_list = []
    example_data = False
    example_list = []
    test_file = Path(file_path + '/' + file_name)  # check if the readme file exists
    if test_file.exists():
        with open(file_path + '/' + file_name, 'r', errors='ignore') as myfile:
            data = myfile.readlines()
            for each_line in data:
                if re.search('##', each_line, re.I):  # check for the ## header flag in the readme
                    if re.search('Description', each_line, re.I):  # start of the Description section
                        description_data = True
                        example_data = False
                     # print('Found Description')
                    elif re.search('Examples', each_line, re.I):  # start of the Examples section
                        example_data = True
                        description_data = False
                        # print('Found Examples')
                    else:  # some other section was detected end processing
                        description_data = False
                        example_data = False
                elif description_data:  # The description section was detected, continue parsing
                    each_line = re.sub('[*\n"]+', '', each_line)
                    each_line = each_line.strip()
                    if len(each_line) > 0:
                        description_list.append(each_line)
                elif example_data:  # The example section was detected, continue parsing
                    each_line = re.sub('[*\n"]+', '', each_line)
                    each_line = each_line.strip()
                    if len(each_line) > 0:
                        example_list.append(each_line)
            if len(description_list) > 0:  # The description section contained no information for this skill
                print(description_list)
            if len(example_list) > 0:  # The example section contained no information for this skill
                print(example_list)
    else:
        vocal_response = "I am sorry, I had trouble locating the skills directory"
        print(vocal_response)

def get_skills_list():
    skill_directories = []
    skill_names = []
    location = os.path.dirname(os.path.realpath(__file__))
    location = location + '/../'  # get skill parent directory path
    for name in os.listdir(location):
        path = os.path.join(location, name)
        if os.path.isdir(path):  # if path item is a directory then process
            skill_directories.append(path)  # Directory path list
            #Todo Need to run the name through regex to remove the "skill" and "-" portions from the "name"
            skill_names.append(name)  # Skill name list based on the path
    print(skill_directories)  # For debugging only
    print(skill_names)  # For debugging only
    skill_quantity = len(skill_names)  # The number of skills detected
    for each_skill in skill_names:  # obtain the description and examples for each of the readme files
        scrape_readme_file(skill_directories[int(skill_names.index(each_skill))])  # index begins at 0

# scrape_readme_file('c:/Users/PhilC/Documents/Kelsey.ai/')
get_skills_list()