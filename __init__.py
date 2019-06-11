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
from datetime import timedelta
from adapt.intent import IntentBuilder

from mycroft.skills.core import MycroftSkill, intent_file_handler, intent_handler
from mycroft.skills.context import adds_context, removes_context
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
            data = json.load(rf)
        return data
    except:
        return {}


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

def record_total_time(data=None, new_time=None, project=None):
    """Records the total time into current read projects.json.

    Checks if total time needs to be added or recorded only, then
    returns the newly updated data variable.

    Args:
        data (dict): Read projects.json file's data.
        new_time (float): New calculated start-stop time.
        project (str): Project name.
    Returns:
        data (dict):
    """
    if data[project]['total'] > 0:
        new_total = data[project]['total'] + new_time
        data[project]['total'] = new_total
    else:
        data[project]['total'] = new_time
    return data

def record_day_time(data=None, new_time=None, project=None):
    """Records and checks today's logged time.

    Checks if today's date exists in the dict. If not, create a new key,
    and if yes, add current total with new time. Then write data to
    projects.json.

    Args:
        data (dict): Read projects.json file's data.
        new_time (float): New calculated start-stop time.
        project (str): Project name.
    Returns:
        day_time (float): Either newly added time, or new_time.
    """
    day_time = None
    today_date = str(datetime.today()).split()[0]
    try:
        day_time = data[project]["days"][today_date]
        new_day_time = day_time + new_time
        data[project]["days"][today_date] = new_day_time
        day_time = new_day_time
    except KeyError:
        data[project]["days"][today_date] = new_time
        day_time = data[project]["days"][today_date]
    write_data(data)
    return day_time

def convert_time(seconds=None):
    """Converts the seconds format to proper readable time."""
    sec = timedelta(seconds=int(seconds))
    d = datetime(1, 1, 1) + sec
    days = d.day - 1
    hrs = d.hour
    minutes = d.minute
    secs = d.second
    times = {"days": days, "hours": hrs, "minutes": minutes, "seconds": secs}
    keys = ["days", "hours", "minutes", "seconds"]
    for i in keys:
        if times[i] == 0:
            del times[i]
    # Removing s at the end if it is singular
    keys = list(times)
    for i in keys:
        if times[i] == 1:
            key = i[:-1]
            times[key] = times[i]
            del times[i]
    return times

def format_time(new_time=None, day_time=None):
    """Formats the times for mycroft's dialog.
    """
    current_sess = None
    day_sess = None
    # Formatting current session time
    if new_time:
        curr_time_list = convert_time(new_time)
        res = []
        for k, v in curr_time_list.items():
            res.append("{} {}".format(v, k))
        try:
            res = res.join(" and ")
        except AttributeError:
            res = res[0]
            pass
        current_sess = res
    # Formatting day's total time
    if day_time:
        day_time_list = convert_time(day_time)
        res = []
        for k, v in day_time_list.items():
            res.append("{} {}".format(v, k))
        try:
            res = res.join(" and ")
        except AttributeError:
            res = res[0]
            pass
        day_sess = res
    return [current_sess, day_sess]


# TODO close enough function


class TimeTrackerSkill(MycroftSkill):

    def add_project(self, project):
        projects = read_data()
        if not projects:
            self.speak_dialog('projects.not.found')
        if project in projects:
            self.speak("{} already exists.".format(project))
        else:
            projects[project] = {'total': 0.0, 'days': {}, 'start': 0.0, 'active': False}
            write_data(projects)
            self.speak_dialog('create.project', {'project': project})

    def delete_project(self, project):
        projects = read_data()
        try:
            del projects[project]
            write_data(projects)
            self.speak_dialog('delete.project', {'project': project})
        except KeyError:
            self.speak_dialog('project.not.found')

    @adds_context('ProjectName')
    @removes_context('DeleteContext')
    @intent_handler(IntentBuilder('CreateIntent').require('CreateKeyword').optionally('ProjectName'))
    def handle_create_project_intent(self, message):
        project = message.data.get('ProjectName')
        # TODO get rid of this
        if not project:
            self.set_context('SpecifyContext', 'True')
            self.set_context('CreateContext', 'True')
            self.speak("What would you like to call the new project?", expect_response=True)
        else:
            self.add_project(project)

    @removes_context('CreateContext')
    @intent_handler(IntentBuilder('DeleteIntent').require('DeleteKeyword').optionally('ProjectName'))
    def handle_delete_project_intent(self, message):
        project = message.data.get('ProjectName')
        if not project:
            self.set_context('SpecifyContext', 'True')
            self.set_context('DeleteContext', 'True')
            self.speak("Which project would you like to delete?", expect_response=True)
        else:
            self.delete_project(project)

    @intent_handler(IntentBuilder('StartIntent').require('StartKeyword').require('ProjectName'))
    def handle_start_project_intent(self, message):
        project_name = message.data.get('ProjectName')
        data = read_data()
        project = data.get(project_name)
        if project is None:
            self.speak_dialog('project.not.found')
        elif project.get('active'):
            self.speak("{} is already being tracked.".format(project_name))
        else:
            project['start'] = time.time()
            project['active'] = True
            write_data(data)
            self.speak_dialog('start.project', {'project': project_name})

    @intent_handler(IntentBuilder('StopIntent').require('StopKeyword').require('ProjectName'))
    def handle_stop_project_intent(self, message):
        project_name = message.data.get('ProjectName')
        data = read_data()
        project = data.get(project_name)
        new_time = None
        if project is None:
            self.speak_dialog('project.not.found')
        elif project.get('active'):
                new_time = time.time() - project.get("start")
                # Tracking total time
                data = record_total_time(data, new_time, project_name)
                project['active'] = False
                # Tracking day time
                day_time = record_day_time(data, new_time, project_name)
                # Formatting times
                format_list = format_time(new_time, day_time)
                current_sess = format_list[0]
                day_sess = format_list[1]
                self.speak_dialog('stop.project', {'project': project_name, 'current': current_sess, 'today': day_sess})
        else:
            self.speak("{} was not being tracked.".format(project_name))

    @removes_context('SpecifyContext')
    @removes_context('CreateContext')
    @removes_context('DeleteContext')
    @intent_handler(IntentBuilder('SpecifyProjectIntent').require('ProjectName').require('SpecifyContext').optionally('CreateContext').optionally('DeleteContext'))
    def handle_unspecified_project(self, message):
        project = message.data.get('ProjectName')
        if message.data.get('CreateContext'):
            self.add_project(project)
        elif message.data.get('DeleteContext'):
            self.delete_project(project)

    @intent_file_handler('List.intent')
    def handle_list_projects_intent(self, message):
        data = read_data()
        projects = list(data.keys())
        # project_list contains list of project names only for mycroft to say
        self.speak_dialog('list.projects', {'projects': projects})

def create_skill():
    return TimeTrackerSkill()
