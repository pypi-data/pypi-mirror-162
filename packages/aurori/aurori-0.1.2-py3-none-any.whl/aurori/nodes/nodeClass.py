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

from enum import Enum
from aurori.logs import logManager


class NodeStatus(Enum):
    UNKNOWN = "UNKNOWN"


class NodeClass(object):
    """Base class that each node class have to inherit from. 
       The class define methods that all nodes must implement
    """

    disable = False  # enable or disable detection
    name = None  # overwrites the name (default = self.__class__.__name__)
    identifier = "UNKNOWN"  # node identifier to map hardware nodes with the node class
    description = "UNKNOWN"
    version = "1.0"  # version of the node this class should handle

    def __init__(self, identifier=identifier, name=name):
        self.description = 'UNKNOWN'
        if name is None:
            self.name = self.__class__.__name__
        self.status = NodeStatus.UNKNOWN

    def init_node(self, app, db):
        self.app = app
        self.db = db