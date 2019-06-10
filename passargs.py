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

def get_project(data=None, name=None):
    """Checks if the user_input is within project list

    Args:
        data (dict): Entire projects.json.
        name (str): Name of project to match in projects.json

    Returns:
        k (str): Project ID key from projects.json IF EXISTS.
        None: If project name not found.
    """
    try:
        data_value = data.get(name)
        return name
    except KeyError:
        return None

class TimeTrackerSkill(MycroftSkill):

    @intent_file_handler('Create.intent')
    def create_project(self, message):
        project = message.data['project']
        # TODO get rid of this
        if not project:
            self.speak_dialog('project.not.found')
        else:
            projects = read_data()
            if projects:
                proj_id = int(list(projects.keys())[-1]) + 1
            else:
                proj_id = 0
                projects = OrderedDict()
            projects[proj_id] = {'name': project, 'total': 0, 'days': {}, 'start': 0.0, 'active': False}
            write_data(projects)
            self.speak_dialog('create.project', {'project': project})

    @intent_file_handler('Create.intent')
    def list_project(self, message):
        project_list = []
        data = read_data()
        for k in data.keys():
            project_list.append(data[k]["name"])
        # project_list contains list of project names only for mycroft to say
        self.speak_dialog('list.project', {})

    @intent_file_handler('Create.intent')
    def start_project(self, message):
        project = message.data['project']
        data = read_data()
        name_test = get_project(data, project)
        if name_test:
            data[project]["start"] = time.time()
            data[project]["active"] = True
        else:
            # project name not in project list
            pass
        write_data(data)
        self.speak_dialog('create.project', {})

    @intent_file_handler('Create.intent')
    def stop_project(self, message):
        project = message.data['project']
        data = read_data()
        name_test = get_project(data, project)
        if name_test:
            if data[project]["active"] == True:
                new_time = time.time() - data[project]["start"]
                # Tracking total time
                if data[project][total] > 0:
                    new_total = data[project][total] + new_time
                    data[project][total] = new_total
                else:
                    data[project][total] = new_total
                # Tracking day time
                today_date = str(datetime.today()).split()[0]
                try:
                    day_time = data[project]["days"][today_date]
                    new_day_time = day_time + new_time
                    data[project]["days"][today_date] = new_day_time
                except KeyError:
                    data[project]["days"][today_date] = new_time
            else:
                # Project is not active
                pass
        write_data(data)
        self.speak_dialog('create.project', {})

def create_skill():
    return TimeTrackerSkill()
