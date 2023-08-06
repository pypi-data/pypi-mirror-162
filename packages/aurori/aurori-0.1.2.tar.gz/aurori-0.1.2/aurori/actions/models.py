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

from aurori import db
from sqlalchemy_utils import ArrowType
import arrow

from aurori.common.jsonDict import JsonDict


class ActionLink(db.Model):
    __tablename__ = 'actionlinks'
    # nonvolatile data stored in the db
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(128), default="")
    workspace = db.Column(db.String(120), default="")
    need_login = db.Column(db.Boolean, default=True)
    action = db.Column(db.String(120), default="")
    action_data_json = db.Column(JsonDict)
    run_only_once = db.Column(db.Boolean, default=True)
    expire_on_date = db.Column(ArrowType, default=arrow.utcnow)
    redirect_to = db.Column(db.String(255), default="")

    def __repr__(self):
        return '<ActionLink {} for {}/{} [expires on {}] >'.format(
            self.link, self.workspace, self.action, self.expire_on_date)
