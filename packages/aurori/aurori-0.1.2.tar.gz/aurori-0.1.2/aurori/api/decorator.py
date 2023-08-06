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

from functools import wraps
from flask import g, Response


def require_user_permission(permissions):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if g.user is None:
                return Response('Authentication required', 401, {
                    'WWW-Authenticate':
                    'Basic realm="Authentication required"'
                })
            for p in permissions:
                if g.user.has_permission(p):
                    return func(*args, **kwargs)
            return Response('Insufficient user permissions', 403)

        return wrapper

    return decorator


def require_user_authentification(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if g.user is None:
            return Response(
                'Authentication required', 401,
                {'WWW-Authenticate': 'Basic realm="Authentication required"'})
        return f(*args, **kwargs)

    return decorator
