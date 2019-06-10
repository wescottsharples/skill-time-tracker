# Copyright 2016 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

import os
import time
import json
from datetime import datetime
from collections import OrderedDict
from datetime import timedelta
from adapt.intent import IntentBuilder

from mycroft.skills.core import MycroftSkill, intent_file_handler, intent_handler
from mycroft.util.log import getLogger


__author__ = 'eward'

LOGGER = getLogger(__name__)
DIR_PATH = os.path.dirname(os.path.realpath(__file__))


def read_data():
    """Reads current data and returns it's json in dict format.

    Returns:
        current_data (dict): Current read data from projects.json.
    """
    try:
        with open(DIR_PATH + "/projects.json", "r") as rf:
            data = json.load(rf, object_pairs_hook=OrderedDict)

        return data
    except:
        return None


def update_data(newdata=None):
    """Updates current data and writes to projects.json.

    This function will update all key to new values in current projects.json.

    Args:
        newdata (dict): New data to update to projects.json.
    """
    data = read_data()
    newkeys = list(newdata)
    for k in data.keys():
        for i in newkeys:
            if k == i:
                data[k] = newdata[i]

    with open(DIR_PATH + "/projects.json", "w") as wf:
        json.dump(data, wf)


def write_data(data):
    """Creates new key in current projects.json and writes it.

    Args:
        newdata (dict): New data to write to projects.json.
    """
    with open(DIR_PATH + "/projects.json", "w") as wf:
        json.dump(data, wf)
    

def verify_data_exists():
    """Checks if projects data exists (projects.json). If it does not exist,
    creates a template of the project data.
    """
    exists = os.path.isfile(DIR_PATH + '/projects.json')

    if exists:
        pass
    else:
        template = {"current_project": "None", "max_projects": "0"}
        with open(DIR_PATH + "/projects.json", "w") as wf:
            json.dump(template, wf)


def set_max_projects():
    """Calculates the new max_projects data, and updates to a new value
    if it has changed.
    """
    data_checker()
    data = read_data()
    keycount = list(data)
    newmax = keycount - 2
    newmax = str(newmax)
    if newmax == data["max_projects"]:
        pass
    else:
        newdata = {"max_projects": newmax}
        update_data(newdata)


def convert_time(seconds=None):
    """Converts the seconds format to proper readable time."""
    sec = timedelta(seconds=int(seconds))
    d = datetime(1, 1, 1) + sec
    days = d.day - 1
    hrs = d.hour
    minutes = d.minute
    secs = d.second
    time_list = [days, hrs, minutes, secs]
    # TODO this list should be used to display any time format of a proj
    return time_list


def get_project(user_input=None):
    """Checks if the user_input is within project list

    Args:
        user_input (str): Project name that the user says.

    Returns:
        project_name (str): The name of the project that the user wants
            to track float.
    """
    project_name = None
    # TODO Loop through user_input until it finds a project
    data = read_data()
    keys = list(data)
    for i in keys:
        if "list_p" in i:
            if data[i][0] == user_input:
                return i


class TimeTrackerSkill(MycroftSkill):

    @intent_file_handler('Create.intent')
    def create_project(self, message):
        project = message.data['project']
        if not project:
            self.speak_dialog('project.not.found')
        else:
            verify_data_exists()
            projects = read_data()
            if projects:
                proj_id = int(list(projects.keys())[-1]) + 1
            else:
                proj_id = 0
                projects = OrderedDict()
            projects[proj_id] = {'name': project, 'total': 0, 'days': {}}
            write_data(projects)
            self.speak_dialog('create.project', {'project': project})


def create_skill():
    return TimeTrackerSkill()
