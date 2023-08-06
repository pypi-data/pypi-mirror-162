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
from aurori.actions import webclientActions


class Widget(object):
    group = ''
    name = ''
    description = ''
    disable = False
    required_permission = None
    size = {'w': 0, 'h': 0}  # size in grid units
    position = {'x': 0, 'y': 0}  # distance from top left corner in grid units

    def __init__(self, name=None, uri=None):
        if name is None:
            self.name = type(self).name
        else:
            self.name = name
        if uri is None:
            self.uri = 'widget_{}'.format(self.__class__.__name__.lower())
        else:
            self.uri = uri

    def handle(self, widget, user, workspace, actionManager):
        from aurori.widgets import widgetManager
        self.status = None
        logManager.info('Request widget {} for workspace {} by user {}'.format(
            widget['action'],
            widget['workspace'],
            user,
        ))
        self.response_actions = []
        # check if this widget is registered
        self.registered_widget = widgetManager.get_widget_by_key(
            '{}/{}'.format(widget.workspace, widget.action))
        if self.registered_widget is None:
            notification_action = webclientActions.NotificationAction.generate(
                "Widget not registered", "error")
            self.response_actions.append(notification_action)
            self.status = 'error'
        # check permissions again
        if 'required_permission' in self.registered_widget:
            if not user.admin and not user.has_permission(
                    self.registered_widget['required_permission']):
                notification_action = webclientActions.NotificationAction.generate(
                    "No permission to view this widget.", "error")
                self.response_actions.append(notification_action)
                self.status = 'error'
        # try to parse options
        self.options = None
        if 'options' in widget and widget[
                'options'] is not None and widget['options'] != '':
            self.options = widget['options']
