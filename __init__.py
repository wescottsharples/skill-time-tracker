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


# TODO close enough function


class TimeTrackerSkill(MycroftSkill):

    @intent_file_handler('Create.intent')
    def create_project(self, message):
        project = message.data.get('project')
        # TODO get rid of this
        if not project:
            self.speak_dialog('project.not.found')
        else:
            projects = read_data()
            projects[project] = {'total': 0.0, 'days': {}, 'start': 0.0, 'active': False}
            write_data(projects)
            self.speak_dialog('create.project', {'project': project})

    @intent_file_handler('Delete.intent')
    def delete_project(self, message):
        project = message.data.get('project')
        projects = read_data()
        if not projects:
            self.speak_dialog('projects.not.found')
        else:
            try:
                del projects[project]
                write_data(projects)
                self.speak_dialog('delete.project', {'project': project})
            except KeyError:
                self.speak_dialog('project.not.found')

    @intent_file_handler('List.intent')
    def list_project(self, message):
        data = read_data()
        projects = list(data.keys())
        # project_list contains list of project names only for mycroft to say
        self.speak_dialog('list.projects', {'projects': projects})

    @intent_file_handler('Start.intent')
    def start_project(self, message):
        project = message.data.get('project')
        data = read_data()
        try:
            data[project]["start"] = time.time()
            data[project]["active"] = True
            write_data(data)
            self.speak_dialog('start.project', {'project': project})
        except KeyError:
            self.speak_dialog('project.not.found')

    @intent_file_handler('Stop.intent')
    def stop_project(self, message):
        project = message.data.get('project')
        data = read_data()
        new_time = None
        day_time = None
        day_sess = ""
        current_sess = ""
        try:
            if data[project]["active"] == True:
                new_time = time.time() - data[project]["start"]
                # Tracking total time
                if data[project]['total'] > 0:
                    new_total = data[project]['total'] + new_time
                    data[project]['total'] = new_total
                else:
                    data[project]['total'] = new_time
                data[project]['active'] = False
                # Tracking day time
                today_date = str(datetime.today()).split()[0]
                try:
                    day_time = data[project]["days"][today_date]
                    new_day_time = day_time + new_time
                    data[project]["days"][today_date] = new_day_time
                except KeyError:
                    data[project]["days"][today_date] = new_time
                    day_time = data[project]["days"][today_date]
                write_data(data)
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
                # Have some kind of pause between cureent_sess and day_sess
                self.speak_dialog('stop.project', {'project': project, 'current': current_sess, 'today': day_sess})
        except KeyError:
            self.speak_dialog('project.not.found')

def create_skill():
    return TimeTrackerSkill()
