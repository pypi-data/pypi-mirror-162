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

from aurori.logs import logManager
import time
import threading


class NodeManager(object):
    """ The NodeManager holds all available node-types and load them while creation.
    """
    def __init__(self):
        self.node_classes = {}
        self.nodes = {}

    def register_node(self, name, fingerprint, identifier, version):
        logManager.info("Registered node")
        node_instance = None
        for k, v in self.node_classes.items():
            if v.identifier == identifier:
                node_instance = self.node_classes[k]()

        if node_instance is not None:
            self.nodes[fingerprint] = node_instance
        else:
            logManager.error(
                f"NodeManager is unable to register node {name} ({fingerprint}) with unknown identifier '{identifier}'"
            )

    def register_node_class(self, workspace, node_class):
        node_instance = node_class()
        nodekey = str(workspace.name) + '/' + node_instance.name
        self.node_classes[nodekey] = node_class

    def get_node_classes(self):
        return self.node_classes

    def statemachine(self):
        while True:
            time.sleep(2)
            logManager.info("run statemachine cylce {} {}".format(
                self.nodeSource,
                threading.current_thread().name))

    def init_manager(self, app, db, workspaceManager):
        self.app = app
        self.db = db
        self.workspaceManager = workspaceManager
        logManager.info("NodeManager initialized")

        from aurori.nodes.models import Node
        self.node = Node
        self.worker = threading.Thread(target=self.statemachine,
                                       name='NodeManagr')
        self.worker.setDaemon(True)
        # self.worker.start()
