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

from flask import request, make_response
from flask_jwt_extended import jwt_optional, get_jwt_identity, get_raw_jwt
from pprint import pformat
import json
import datetime

from aurori import actionManager
from aurori.api import api_bp
from aurori.logs import logManager

# this module routes the action based api on e.g. .../api/v1
# the api needs the generalized action based json-rpc form
# every app module can hold additional entrypoint in a rest based form
# e.g. '/login/refresh'


@api_bp.route('/api/v1', methods=["POST", "GET"])
@jwt_optional
def api_v1():
    logManager.debug("Call on api/v1")
    logManager.debug(pformat(request.json, depth=2, indent=2))

    a = get_raw_jwt()
    expire_date = None
    if 'exp' in a:
        expire_date = datetime.datetime.fromtimestamp(a['exp'])
    reply = actionManager.handleActionRequest(get_jwt_identity(), expire_date,
                                              request.json)
    logManager.debug("Send reply")
    logManager.debug(pformat(request.json, depth=2, indent=2))
    reply = json.dumps(reply)
    reply = make_response(reply, 200)
    return reply


@api_bp.route('/api/v1/workspaces/<workspace_id>/view/<view_id>',
              methods=['GET'])
@jwt_optional
def api_v1_get_view(workspace_id, view_id):
    pass


@api_bp.route(
    '/api/v1/workspaces/<workspace_id>/view/<view_id>/entry/<entry_id>',
    methods=['GET'])
@jwt_optional
def api_v1_get_view_entry(workspace_id, view_id, entry_id):
    pass


@api_bp.route(
    '/api/v1/workspaces/<workspace_id>/view/<view_id>/entry/<entry_id>',
    methods=['UPDATE'])
@jwt_optional
def api_v1_update_view_entry(workspace_id, view_id, entry_id):
    pass


@api_bp.route(
    '/api/v1/workspaces/<workspace_id>/view/<view_id>/entry/<entry_id>',
    methods=['DELETE'])
@jwt_optional
def api_v1_remove_view_entry(workspace_id, view_id, entry_id):
    pass


@api_bp.route(
    '/api/v1/workspaces/<workspace_id>/view/<view_id>/entry/<entry_id>',
    methods=['POST', 'PUT'])
@jwt_optional
def api_v1_add_view_entry(workspace_id, view_id, entry_id):
    pass


@api_bp.route(
    '/api/v1/workspaces/<workspace_id>/view/<view_id>/request/<view_action_id>',
    methods=['POST'])
@jwt_optional
def api_v1_request_view_action(workspace_id, view_id, view_action_id):
    pass


@api_bp.route('/api/v1/workspaces/<workspace_id>/request/<action_id>',
              methods=['POST'])
@jwt_optional
def api_v1_request_action(workspace_id, action_id):
    pass
