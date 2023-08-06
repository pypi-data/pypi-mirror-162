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

from aurori.users import auth_bp
from flask import jsonify, request
from pprint import pprint

from flask_jwt_extended import (create_access_token,
                                jwt_refresh_token_required,
                                create_refresh_token, get_jwt_identity,
                                set_access_cookies, set_refresh_cookies,
                                unset_jwt_cookies)


@auth_bp.route('/activate', methods=['POST'])
def activate():
    return "Activate", 200


# With JWT_COOKIE_CSRF_PROTECT set to True, set_access_cookies() and
# set_refresh_cookies() will now also set the non-httponly CSRF cookies
# as well
@auth_bp.route('/login', methods=['POST'])
def login():

    # not used add the moment
    pprint(request.json, indent=4)
    return jsonify({'login': False}), 401
    """ username = request.json.get('username', None)
    password = request.json.get('password', None)

    # Create the tokens we will be sending back to the user
    expires = datetime.timedelta(days=1)
    access_token = create_access_token(identity=username,
                                       expires_delta=expires)
    refresh_token = create_refresh_token(identity=username)

    # Set the JWTs and the CSRF double submit protection cookies
    # in this response
    resp = jsonify({'login': True})
    # the access cookie expire after 15 minutes and have to get refreshed by the client
    set_access_cookies(resp, access_token, max_age=15 * 60)
    # the refresh cookie expire after 30 minutes
    set_refresh_cookies(resp, refresh_token, max_age=30 * 60)
    return resp, 200 """


@auth_bp.route('/login/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    # Set the access JWT and CSRF double submit protection cookies
    # in this response
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200


# Because the JWTs are stored in an httponly cookie now, we cannot
# log the user out by simply deleting the cookie in the frontend.
# We need the backend to send us a response to delete the cookies
# in order to logout. unset_jwt_cookies is a helper function to
# do just that.
@auth_bp.route('/logout', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200
