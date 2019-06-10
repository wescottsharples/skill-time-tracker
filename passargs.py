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


class TimeTrackerSkill(MycroftSkill):

    @intent_file_handler('Create.intent')
    def create_project(self, message):
        project = message.data['project']
        if not project:
            self.speak_dialog('project.not.found')
        else:
            self.speak_dialog('create.project', {'project': project})

def create_skill():
    return TimeTrackerSkill()
