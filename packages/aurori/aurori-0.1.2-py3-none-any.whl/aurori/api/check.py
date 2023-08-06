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

import base64
from flask import request, g
from flask_jwt_extended import jwt_optional, get_jwt_identity
from aurori.users import userManager


def check_before_request():
    g.user = None
    jwt_id = get_jwt_identity()
    auth_header = request.headers.get('Authorization')

    if jwt_id is not None:  # check for jwt token
        user = (userManager.getUser(jwt_id))
        g.user = user
    else:  # check for header authentication basic
        if auth_header is not None:
            split_auth_header = auth_header.split()
            auth_type = split_auth_header[0]
            if auth_type == "Basic":
                decoded_auth = base64.b64decode(
                    split_auth_header[1]).decode('utf8').split(':')
                if decoded_auth[
                        0] == 'api_key':  # check for api_key authentication
                    user = userManager.get_user_by_api_key(decoded_auth[1])
                    g.user = user
                else:  # check for email and password authentication
                    user = userManager.getUser(decoded_auth[0])
                    if user is not None:
                        if userManager.checkUserPassword(
                                user, decoded_auth[1]):
                            g.user = user

    request.view_args['user'] = g.user
