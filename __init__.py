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
import util
import time
from adapt.intent import IntentBuilder

from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'eward'

LOGGER = getLogger(__name__)


class TimeTrackerSkill(MycroftSkill):
    def __init__(self):
        super(TimeTrackerSkill, self).__init__(name="TimeTrackerSkill")
        self.project = util.get_project()
        self.s_time = 0
        # curr_total is a current start-stop total time (start-stop only)
        self.curr_total = 0
        # total_time is a current project total time (start-stop + start-stop)
        self.total_time = 0

    def initialize(self):
        list_projects_intent = IntentBuilder("ListProjectsIntent"). \
            require("ListProjectsKeyword").build()
        self.register_intent(list_projects_intent, self.handle_list_projects_intent)

        create_projects_intent = IntentBuilder("CreateProjectsIntent"). \
            require("CreateProjectsKeyword").build()
        self.register_intent(create_projects_intent, self.handle_create_projects_intent)

        delete_projects_intent = IntentBuilder("DeleteProjectsIntent"). \
            require("DeleteProjectsKeyword").build()
        self.register_intent(delete_projects_intent, self.handle_delete_projects_intent)

        start_projects_intent = IntentBuilder("StartProjectsIntent"). \
            require("StartProjectsKeyword").build()
        self.register_intent(start_projects_intent, self.handle_start_projects_intent)

        stop_projects_intent = IntentBuilder("StopProjectsIntent"). \
            require("StopProjectsKeyword").build()
        self.register_intent(stop_projects_intent, self.handle_stop_projects_intent)

    def handle_list_projects_intent(self, message):
        util.data_checker()
        data = util.read_data()
        keys = list(data)
        project_list = []
        for k in keys:
            if "list_p" in k:
                project_list.append(data[k][0])
        # project_list contains projects for mycroft to say
        self.speak_dialog("list.projects")

    def handle_create_projects_intent(self, message):
        util.data_checker()
        util.set_max_projects()
        data = util.read_data()
        proj_num = int(data["max_projects"]) + 1
        proj_val = [data[self.project][0], "0", {}]
        proj_key = "list_project_{}".format(str(proj_num))
        proj_data = {proj_key: proj_val}
        util.write_data(proj_data)
        self.speak_dialog("create.projects")

    def handle_delete_projects_intent(self, message):
        util.data_checker()
        data = util.read_data()
        proj_name = #TODO insert user input here
        name = get_project()
        del data[proj_name]
        util.update_data(data)
        self.speak_dialog("delete.projects")

    def handle_start_projects_intent(self, message):
        util.data_checker()
        self.s_time = time.time()
        self.speak_dialog("start.projects")

    def handle_stop_projects_intent(self, message):
        util.data_checker()
        data = util.read_data()
        self.curr_total = time.time() - self.s_time
        # Transferring current start-stop total time session to project session
        self.total_time += self.curr_total
        if str(data[self.project][1]) != "0":
            tempnum = float(data[self.project][1])
            tempnum += self.curr_total
            data[self.project][1] = str(tempnum)
        else:
            data[self.project][1] = str(self.total_time)
        util.update_data(data)
        self.speak_dialog("stop.projects")

    def stop(self):
        pass


def create_skill():
    return TimeTrackerSkill()
