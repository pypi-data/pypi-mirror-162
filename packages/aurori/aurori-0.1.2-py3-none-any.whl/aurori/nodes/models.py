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


class Node(db.Model):
    __tablename__ = 'nodes'
    # nonvolatile data stored in the db
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    fingerprint = db.Column(db.String(120), default="")
    class_name = db.Column(db.String(120), default="")
    workspace = db.Column(db.String(120), default="")
    network_ip = db.Column(db.String(64), default="")
    last_request_on = db.Column(ArrowType, default=arrow.utcnow)

    def __repr__(self):
        return '<Node {} {} [{}] >'.format(self.name, self.typeid,
                                           self.fingerprint)


class NodeSettings(db.Model):
    __tablename__ = 'node_settings'
    # nonvolatile data stored in the db
    id = db.Column(db.Integer, primary_key=True)
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'))
    node = db.relationship("Node",
                           backref=db.backref("settings", uselist=True))


class NodeLog(db.Model):
    __tablename__ = 'node_logs'
    id = db.Column(db.Integer, primary_key=True)
    node_name = db.Column(db.String(120), default="")
    node_class = db.Column(db.String(120), default="")
    node_fingerprint = db.Column(db.String(120), default="")
    node_ip = db.Column(db.String(120), default="")
    node_status = db.Column(db.String(120), default="")
    request_action = db.Column(db.String(120), default="")
    request_reply = db.Column(db.String(120), default="")
    request_status = db.Column(db.String(120), default="")
    request_on = db.Column(ArrowType, default=arrow.utcnow)
