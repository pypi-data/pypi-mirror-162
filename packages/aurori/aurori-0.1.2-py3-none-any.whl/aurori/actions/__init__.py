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

from flask import Blueprint
from aurori.actions.actionManager import ActionManager

actions_bp = Blueprint('actions', __name__)

actionManager = ActionManager()


def generateActionLink(workspace,
                       action_uri,
                       action_params,
                       redirect_to="",
                       once=True,
                       need_login=True,
                       expire_days=7):
    return actionManager.createActionLink(workspace, action_uri, action_params,
                                          redirect_to, once, need_login,
                                          expire_days)


def executeActionLink(hash, user):
    return actionManager.executeActionLink(hash, user)


from aurori.actions import routes
