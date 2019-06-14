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

import csv
import os
import time
import json
from datetime import datetime
from datetime import timedelta
from datetime import date
from adapt.intent import IntentBuilder

from mycroft.skills.core import MycroftSkill, intent_file_handler, intent_handler
from mycroft.skills.context import adds_context, removes_context
from mycroft.util.log import getLogger


__author__ = 'eward'

LOGGER = getLogger(__name__)
DIR_PATH = os.path.dirname(os.path.realpath(__file__))


def read_data():
    """Reads projects.json and returns in dict format.

    Returns:
        current_data (dict): Current read data from projects.json.
    """
    try:
        with open(DIR_PATH + "/projects.json", "r") as rf:
            data = json.load(rf)
        return data
    except:
        return {}

def write_data(data):
    """Writes any new data to projects.json.

    Args:
        newdata (dict): New data to write to projects.json.
    """
    with open(DIR_PATH + "/projects.json", "w") as wf:
        json.dump(data, wf)

def record_total_time(data=None, new_time=None, project=None):
    """Records the total time into current read projects.json.

    Checks if total time needs to be added or recorded only, then
    returns the newly updated data variable. Used in stop command.

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
    projects.json. Used in stop command.

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
    """Converts seconds to a readable time format.

    Used in function format_time() and the detail command.

    Args:
        seconds (float): Amount of seconds needed to be converted.

    Returns:
        time_str (str): A string of [time] [time_type]. Ex: 1 minute 30 seconds
    """
    sec = timedelta(seconds=int(seconds))
    d = datetime(1, 1, 1) + sec
    days = d.day - 1
    hrs = d.hour
    minutes = d.minute
    secs = d.second
    times = {"days": days, "hours": hrs, "minutes": minutes, "seconds": secs}
    time_str = ""
    # Removing s at the end if it is singular
    keys = list(times)
    for i in keys:
        if times[i] == 1:
            key = i[:-1]
            times[key] = times[i]
            del times[i]
    for k, v in times.items():
        if v != 0:
            temp = "{} {} ".format(v, k)
            time_str += temp
    return time_str

def format_time(new_time=None, day_time=None):
    """Formats the times for mycroft's dialog.

    Used in the stop command.

    Args:
        new_time (float): Total time of a start-stop session.
        day_time (float): Total time for a day.

    Returns:
        [current_sess, day_sess] (list): List of formatted time for dialog.
    """
    current_sess = None
    day_sess = None
    # Formatting current session time
    if new_time:
        current_sess = convert_time(new_time)
    # Formatting day's total time
    if day_time:
        day_sess = convert_time(day_time)
    return [current_sess, day_sess]


class TimeTrackerSkill(MycroftSkill):
    """Time Tracker that can create and delete activities/tasks, track day
    by day the amount of time spent on each activity/task, and export all data
    to csv files. All activity/tasks and their time data are written to
    projects.json in this skill's directory.
    """
    def add_project(self, project):
        """Adds a project in projects.json when create_project is invoked."""
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
        """Deletes a project from projects.json if exists when delete_project
        is invoked.
        """
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
        """Handler for creating a project/task/activity."""
        project = message.data.get('ProjectName')
        if not project:
            self.set_context('SpecifyContext', 'True')
            self.set_context('CreateContext', 'True')
            self.speak("What would you like to call the new project?", expect_response=True)
        else:
            self.add_project(project)

    @removes_context('CreateContext')
    @intent_handler(IntentBuilder('DeleteIntent').require('DeleteKeyword').optionally('ProjectName'))
    def handle_delete_project_intent(self, message):
        """Handler for deleting a project/task/activity."""
        project = message.data.get('ProjectName')
        if not project:
            self.set_context('SpecifyContext', 'True')
            self.set_context('DeleteContext', 'True')
            self.speak("Which project would you like to delete?", expect_response=True)
        else:
            self.delete_project(project)

    @intent_handler(IntentBuilder('StartIntent').require('StartKeyword').require('ProjectName'))
    def handle_start_project_intent(self, message):
        """Handler for starting the time on a project/task/activity."""
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
        """Handler for stopping the time on a project/task/activity."""
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
        """Handler for directing unknown project/task/activity input."""
        project = message.data.get('ProjectName')
        if message.data.get('CreateContext'):
            self.add_project(project)
        elif message.data.get('DeleteContext'):
            self.delete_project(project)

    @intent_file_handler('List.intent')
    def handle_list_projects_intent(self, message):
        """Handler for listing current projects/tasks/activities in
        projects.json."""
        data = read_data()
        projects = list(data.keys())
        # project_list contains list of project names only for mycroft to say
        self.speak_dialog('list.projects', {'projects': projects})

    @intent_file_handler("Csv.intent")
    def handle_create_csv(self, message):
        """Handler for creating a csv for all projects/tasks/activities in
        projects.json."""
        data = read_data()
        try:
            os.mkdir(DIR_PATH + "/projects_csv")
        except FileExistsError:
            pass
        project_names = list(data)
        for name in project_names:
            with open(DIR_PATH + "/projects_csv/{}.csv".format(name), "w+") as f:
                writer = csv.writer(f)
                writer.writerow([name])
                writer.writerow(["total time", data[name]["total"]])
                writer.writerow(["day", "time"])
                days = data[name]["days"]
                for k, v in days.items():
                    writer.writerow([k, v])
        self.speak_dialog("csv.projects")

    @intent_handler(IntentBuilder('DetailsIntent').require('DetailsKeyword').require('ProjectName'))
    def handle_details_project_intent(self, message):
        """Handler for listing out details of a project."""
        project_name = message.data.get('ProjectName')
        data = read_data()
        data_daylist = data[project_name]["days"]
        today = date.today()
        daylist = []
        total_time = 0
        for i in range(0, 7):
            temp = today - timedelta(days=i)
            daylist.append(str(temp))
        for day in daylist:
            try:
                time = data_daylist[day]
                total_time += time
            except KeyError:
                pass
            except TypeError:
                pass
        total_time = convert_time(total_time)
        self.speak_dialog('details.projects', {"total_time": total_time, "project": project_name})
        
def create_skill():
    return TimeTrackerSkill()
