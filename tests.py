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
    test_file = Path(file_path + '/' + file_name)
    if test_file.exists():
        with open(file_path + '/' + file_name, 'r') as myfile:
            data = myfile.readlines()
            for each_line in data:
                if re.search('##', each_line, re.I):
                    if re.search('Description', each_line, re.I):
                        description_data = True
                        example_data = False
                     # print('Found Description')
                    elif re.search('Examples', each_line, re.I):
                        example_data = True
                        description_data = False
                        # print('Found Examples')
                    else:
                        description_data = False
                        example_data = False
                elif description_data:
                    each_line = re.sub('[*\n"]+', '', each_line)
                    each_line = each_line.strip()
                    if len(each_line) > 0:
                        description_list.append(each_line)
                elif example_data:
                    each_line = re.sub('[*\n"]+', '', each_line)
                    each_line = each_line.strip()
                    if len(each_line) > 0:
                        example_list.append(each_line)
            print(description_list)
            print(example_list)

def get_skills_list():
    skill_directories = []
    skill_names = []
    location = os.path.dirname(os.path.realpath(__file__))
    location = location + '/../' # get skill parent directory path
    for name in os.listdir(location):
        path = os.path.join(location, name)
        if os.path.isdir(path):
            skill_directories.append(path)
            skill_names.append(name)
    print(skill_directories)
    print(skill_names)
    print(len(skill_names))
    scrape_readme_file(skill_directories[2])  # index begins at 0

# scrape_readme_file('c:/Users/PhilC/Documents/Kelsey.ai/')
get_skills_list()