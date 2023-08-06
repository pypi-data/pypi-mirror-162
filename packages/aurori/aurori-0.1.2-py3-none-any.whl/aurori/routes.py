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

import os
from aurori import app_bp
from flask import redirect, url_for, send_from_directory


# index route
@app_bp.route('/')
def index():
    return send_from_directory('../client', 'index.html')
    #return render_template("index.html")


@app_bp.route('/<path:path>')
def static_proxy(path):
    # send_static_file will guess the correct MIME type
    if (os.path.isdir("./client/" + path)):
        return send_from_directory('../client/' + path, 'index.html')
    if (os.path.isfile("./client/" + path)):
        return app_bp.send_static_file(path)
    else:
        return send_from_directory('../client/section', 'index.html')


@app_bp.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('index'))


@app_bp.after_request
def add_header(r):

    r.headers[
        "Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r
