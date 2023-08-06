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
from aurori.common.objDict import ObjDict


class WidgetManager(object):
    """ The WidgetManager ...
    """
    def __init__(self, ):
        # preparation to instanciate
        self.widgets = {}

    def init_manager(self, app, db, userManager, workspaceManager, config):
        self.config = config
        self.app = app
        self.db = db
        self.workspaceManager = workspaceManager
        self.userManager = userManager
        logManager.info("WidgetManager initialized")

    def get_widgets(self):
        return self.widgets

    def register_widget(self, workspace, widget_class):
        widgetkey = ''
        widgetkey += workspace.name.lower() + '/'

        widgetInstance = widget_class()
        widgetkey += 'widget_{}'.format(
            widgetInstance.__class__.__name__.lower())

        widget = {
            'group':
            widgetInstance.group,
            'name':
            widgetInstance.name,
            'workspace':
            workspace.name,
            'description':
            widgetInstance.description,
            'uri':
            'widget_{}'.format(widgetInstance.__class__.__name__.lower()),
            'component_path':
            'pages/{}/widgets/{}'.format(
                workspace.name.lower(),
                widgetInstance.__class__.__name__.lower()),
            'size':
            widgetInstance.size,
            'position':
            widgetInstance.position,
        }
        if widgetInstance.required_permission:
            widget['required_permission'] = '{}.{}'.format(
                workspace.name, widgetInstance.required_permission.name)

        self.widgets[str(widgetkey)] = ObjDict(widget.copy())
        return widgetInstance

    def get_widget_by_key(self, key):
        return self.widgets.get(key)
