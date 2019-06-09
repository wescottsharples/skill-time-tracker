#!/usr/bin/env python3
"""Util contains helper functions for the init."""
import os
import json
from datetime import timedelta
from datetime import datetime


def read_data():
    """Reads current data and returns it's json in dict format.

    Returns:
        current_data (dict): Current read data from projects.json.
    """
    with open("projects.json", "r") as rf:
        data = json.load(rf)

    return data

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

    with open("projects.json", "w") as wf:
        json.dump(data, wf)

def write_data(newdata=None):
    """Creates new key in current projects.json and writes it.

    Args:
        newdata (dict): New data to write to projects.json.
    """
    data = read_data()
    newkeys = list(newdata)
    for i in newkeys:
        data[i] = newdata[i]

    with open("projects.json", "w") as wf:
        json.dump(data, wf)
    
def data_checker():
    """Checks if projects data exists (projects.json). If it does not exist,
    creates a template of the project data.
    """
    exists = os.path.isfile('projects.json')

    if exists:
        pass
    else:
        template = {"current_project": "None", "max_projects": "0"}
        with open("projects.json", "w") as wf:
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
            to track.
    """
    project_name = None
    # TODO Loop through user_input until it finds a project
    data = read_data()
    keys = list(data)
    for i in keys:
        if "list_p" in i:
            if data[i][0] == user_input:
                return i
