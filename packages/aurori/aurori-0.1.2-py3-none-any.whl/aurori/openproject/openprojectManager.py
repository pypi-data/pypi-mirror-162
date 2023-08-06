"""
The aurori project

Copyright (C) 2022  Marcus Drobisch,

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__authors__ = ["Marcus Drobisch"]
__contact__ = "aurori@fabba.space"
__credits__ = []
__license__ = "AGPLv3+"

from aurori.logs import logManager
from aurori.jobs import jobManager, add_dated_job
import re

from aurori.openproject.jobs import CreateTicketJob


class OpenprojectManager(object):
    """ The OpenprojectManager
    """
    def __init__(self):
        # preparation to instanciate
        self.config = None
        self.app = None
        self.db = None
        self.workspaceManager = None

    def init_manager(self, app, db, workspaceManager, config):
        self.config = config
        self.app = app
        self.db = db
        self.workspaceManager = workspaceManager

        from aurori.openproject.models import OpenProject
        self.openproject = OpenProject

        jobManager.register_job(None, CreateTicketJob, True)

        if 'openproject_api_key' in config['SYSTEM']:
            key_matcher = re.compile('^([0-9a-z]{50,})$')
            if not key_matcher.match(config['SYSTEM']['openproject_api_key']):
                logManager.error(
                    "OpenprojectManager: 'openproject_api_key' doesn't look valid"
                )
        else:
            logManager.error(
                "OpenprojectManager attribute 'openproject_api_key' not defined in config under 'SYSTEM'"
            )

        logManager.info("OpenprojectManager initialized")

    def add_create_ticket_job(self, project, subject, creating_object):
        print('\n\n\n\n')
        print('{} - {} - {}'.format(project, subject, creating_object))
        args = {
            'project': project,
            'subject': subject,
            'object': creating_object,
        }
        add_dated_job(None, CreateTicketJob(), args)
