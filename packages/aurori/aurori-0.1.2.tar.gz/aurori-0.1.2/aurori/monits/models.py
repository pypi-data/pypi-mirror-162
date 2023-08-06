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

import datetime
from aurori import db


class MonitorEvent(db.Model):
    __tablename__ = 'monitor_event'
    # nonvolatile data stored in the db
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), default="")
    classifier = db.Column(db.String(64), default=None)
    value = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class MonitorViewItem(db.Model):
    __tablename__ = 'monitor_view_item'
    id = db.Column(db.Integer, primary_key=True)
    monit_key = db.Column(db.String(128), default=None)

    classifier = db.Column(db.String(64), default=None)

    values_last = db.Column(db.Float, default=None)
    values_min = db.Column(db.Float, default=None)
    values_max = db.Column(db.Float, default=None)
    values_average = db.Column(db.Float, default=None)
    values_sum = db.Column(db.Float, default=None)
    values_count = db.Column(db.Integer, default=None)

    total_sum = db.Column(db.Float, default=None)
    total_count = db.Column(db.Integer, default=None)

    timestamp = db.Column(db.DateTime, default=None)
    hour = db.Column(db.Integer, default=None)
    day = db.Column(db.Integer, default=None)
    month = db.Column(db.Integer, default=None)
    year = db.Column(db.Integer, default=None)

    last_event_at = db.Column(db.DateTime, default=None)
    last_reset_at = db.Column(db.DateTime, default=None)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
