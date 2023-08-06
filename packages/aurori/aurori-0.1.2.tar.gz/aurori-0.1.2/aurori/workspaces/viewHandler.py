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

from aurori.actions.action import Action
from aurori.common.objDict import ObjDict
from aurori.logs import logManager
from aurori.actions import webclientActions
import sys
import traceback


class RemoveViewEntryActionHandler(Action):
    def __init__(self, app, db, uri="removeViewEntry"):
        self.uri = uri
        self.app = app
        self.db = db
        # logManager.info("Instance of RemoveViewEntryActionHandler created")

    def handle(self, action, user, workspace, _actionManager):
        logManager.info("Execute removal for view entry for", action['view'])
        viewname = action['view']

        if viewname in workspace.dataViews:
            view = workspace.dataViews[viewname]
            # check if login required for this view
            if view.requireLogin is True and user is None:
                notification_action = webclientActions.NotificationAction.generate(
                    "Login required", "error")
                route_action = webclientActions.RouteAction.generate('',
                                                                     delay=3)
                return 'success', [notification_action, route_action]
            else:
                # build actions to get view
                response_actions = []
                try:
                    if view.entrykey not in action['entry']:
                        notification_action = webclientActions.NotificationAction.generate(
                            "UpdateViewEntryActionHandler miss entrykey",
                            "error")
                        response_actions = [notification_action]
                    else:
                        view.dataSyncs = []
                        view.removeViewEntryHandler(
                            user, workspace,
                            action['entry'][str(view.entrykey)])
                        self.db.session.commit()
                        for v in view.dataSyncs:
                            updateView = workspace.dataViews[v['view']]
                            dictionary = v['query']
                            entries = updateView.getViewHandler(
                                user, workspace, None
                                if dictionary is None else ObjDict(dictionary))
                            if type(entries) == tuple:
                                meta_data = entries[1]
                                entries = entries[0]
                            else:
                                meta_data = {}
                            properties = updateView.getProperties()
                            uri = workspace.uri + '/' + updateView.uri
                            loadviewaction = webclientActions.LoadViewAction.generate(
                                uri, properties, entries, meta_data)
                            response_actions.append(loadviewaction)
                    response_actions.append(
                        webclientActions.NotificationAction.generate(
                            "Removed successfully", "success"))
                    return 'success', response_actions
                except Exception as e:
                    notification_action = webclientActions.NotificationAction.generate(
                        "RemoveViewEntry '" + str(action['view']) +
                        "' failed with: " + str(e), "error")
                    response_actions = [notification_action]
                    logManager.error(
                        str(type(e).__name__) +
                        'in ExecuteViewActionsActionHandler ' + action['view'])
                    traceback.print_exc(file=sys.stdout)
                return 'success', response_actions

        notification_action = webclientActions.NotificationAction.generate(
            "View >" + viewname + "< not found", "error")
        return 'success', [notification_action]


class CreateViewEntryActionHandler(Action):
    def __init__(self, app, db, uri="createViewEntry"):
        self.uri = uri
        self.app = app
        self.db = db
        # logManager.info("Instance of CreateViewEntryActionHandler created")

    def handle(self, action, user, workspace, actionManager):
        logManager.info("Execute creation of view entry for " + action['view'])
        viewname = action['view']

        if viewname in workspace.dataViews:
            view = workspace.dataViews[viewname]
            # check if login required for this view
            if view.requireLogin is True and user is None:
                notification_action = webclientActions.NotificationAction.generate(
                    "Login required", "error")
                route_action = webclientActions.RouteAction.generate('',
                                                                     delay=3)
                return 'success', [notification_action, route_action]
            else:
                # build actions to get view
                response_actions = []
                response_data = None
                try:
                    view.dataSyncs = []
                    dictionary = action['entry']
                    response_data = view.createViewEntryHandler(
                        user, workspace, ObjDict(dictionary))
                    try:
                        notification_action = webclientActions.NotificationAction.generate(
                            response_data['notification']['message'],
                            response_data['notification']['type'],
                        )
                        response_actions.append(notification_action)
                    except Exception:
                        pass
                    self.db.session.commit()
                    for v in view.dataSyncs:
                        updateView = workspace.dataViews[v['view']]
                        dictionary = v['query']
                        entries = updateView.getViewHandler(
                            user, workspace, None)
                        if type(entries) == tuple:
                            meta_data = entries[1]
                            entries = entries[0]
                        else:
                            meta_data = {}
                        properties = updateView.getProperties()
                        uri = workspace.uri + '/' + updateView.uri
                        loadviewaction = webclientActions.LoadViewAction.generate(
                            uri, properties, entries, meta_data)
                        response_actions.append(loadviewaction)
                    if response_data is not None:
                        return 'success', response_actions, response_data
                    else:
                        return 'success', response_actions
                except Exception as e:
                    notification_action = webclientActions.NotificationAction.generate(
                        "CreateViewEntry '" + str(action['view']) +
                        "' failed with: " + str(e), "error")
                    response_actions = [notification_action]
                    logManager.error(
                        str(type(e).__name__) +
                        'in ExecuteViewActionsActionHandler ' + action['view'])
                    traceback.print_exc(file=sys.stdout)
                return 'success', response_actions

        notification_action = webclientActions.NotificationAction.generate(
            "View >" + viewname + "< not found", "error")
        return 'success', [notification_action]


class UpdateViewEntryActionHandler(Action):
    def __init__(self, app, db, uri="updateViewEntry"):
        self.uri = uri
        self.app = app
        self.db = db
        # logManager.info("Instance of UpdateViewEntryActionHandler created")

    def handle(self, action, user, workspace, actionManager):
        logManager.info("Execute update of view entry for '{}'".format(
            action['view']))
        viewname = action['view']

        if viewname in workspace.dataViews:
            view = workspace.dataViews[viewname]
            # check if login required for this view
            if view.requireLogin is True and user is None:
                notification_action = webclientActions.NotificationAction.generate(
                    "Login required", "error")
                route_action = webclientActions.RouteAction.generate('',
                                                                     delay=3)
                return 'success', [notification_action, route_action]
            else:
                # build actions to get view
                response_actions = []
                response_data = None
                try:
                    if view.entrykey not in action['entry']:
                        notification_action = webclientActions.NotificationAction.generate(
                            "UpdateViewEntryActionHandler miss entrykey",
                            "error")
                        response_actions = [notification_action]
                    else:
                        view.dataSyncs = []
                        dictionary = action['entry']
                        response_data = view.updateViewEntryHandler(
                            user, workspace,
                            action['entry'][str(view.entrykey)],
                            ObjDict(dictionary))
                        try:
                            notification_action = webclientActions.NotificationAction.generate(
                                response_data['notification']['message'],
                                response_data['notification']['type'],
                            )
                            response_actions.append(notification_action)
                        except Exception:
                            response_actions.append(
                                webclientActions.NotificationAction.generate(
                                    "Updated successfully", "success"))
                        self.db.session.commit()
                        for v in view.dataSyncs:
                            updateView = workspace.dataViews[v['view']]
                            dictionary = v['query']
                            entries = updateView.getViewHandler(
                                user, workspace, None
                                if dictionary is None else ObjDict(dictionary))
                            if type(entries) == tuple:
                                meta_data = entries[1]
                                entries = entries[0]
                            else:
                                meta_data = {}
                            properties = updateView.getProperties()
                            uri = workspace.uri + '/' + updateView.uri
                            loadviewaction = webclientActions.LoadViewAction.generate(
                                uri, properties, entries, meta_data)
                            response_actions.append(loadviewaction)
                    if response_data is not None:
                        return 'success', response_actions, response_data
                    else:
                        return 'success', response_actions
                except Exception as e:
                    notification_action = webclientActions.NotificationAction.generate(
                        "UpdateViewEntry '" + str(action['view']) +
                        "' failed with: " + str(e), "error")
                    response_actions = [notification_action]
                    logManager.error(
                        str(type(e).__name__) +
                        'in ExecuteViewActionsActionHandler ' + action['view'])
                    traceback.print_exc(file=sys.stdout)
                return 'success', response_actions

        notification_action = webclientActions.NotificationAction.generate(
            "View >" + viewname + "< not found", "error")
        return 'success', [notification_action]


class ExecuteViewActionsActionHandler(Action):
    def __init__(self, app, db, uri="executeViewAction"):
        self.uri = uri
        self.app = app
        self.db = db

    def handle(self, action, user, workspace, actionManager):
        logManager.info("Execute action '{}' on view '{}'".format(
            action['viewAction'], action['view']))
        viewname = action['view']
        if viewname in workspace.dataViews:
            print('found view', viewname, 'in', workspace.name,
                  workspace.dataViews[viewname])
            view = workspace.dataViews[viewname]

            # check if login required for this view
            if view.requireLogin is True and user is None:
                # login required but got no user identity
                notification_action = webclientActions.NotificationAction.generate(
                    "Login required", "error")
                route_action = webclientActions.RouteAction.generate('',
                                                                     delay=3)
                return 'success', [notification_action, route_action]
            else:
                # build actions to get view
                response_actions = []
                response_data = None
                try:
                    view.dataSyncs = []
                    dictionary = action
                    response_data = view.executeViewActionHandler(
                        user, workspace, ObjDict(dictionary))
                    try:
                        notification_action = webclientActions.NotificationAction.generate(
                            response_data['notification']['message'],
                            response_data['notification']['type'],
                        )
                    except Exception:
                        notification_action = webclientActions.NotificationAction.generate(
                            "Action '" + str(action['viewAction']) +
                            "' executed", "info")
                    response_actions.append(notification_action)
                    self.db.session.commit()
                    for v in view.dataSyncs:
                        updateView = workspace.dataViews[v['view']]
                        dictionary = v['query']
                        entries = updateView.getViewHandler(
                            user, workspace, None
                            if dictionary is None else ObjDict(dictionary))
                        if type(entries) == tuple:
                            meta_data = entries[1]
                            entries = entries[0]
                        else:
                            meta_data = {}
                        properties = updateView.getProperties()
                        uri = workspace.uri + '/' + updateView.uri
                        loadviewaction = webclientActions.LoadViewAction.generate(
                            uri, properties, entries, meta_data)
                        response_actions.append(loadviewaction)

                except Exception as e:
                    notification_action = webclientActions.NotificationAction.generate(
                        "Action '" + str(action['viewAction']) +
                        "' failed with: ", "error")
                    response_actions = [notification_action]
                    logManager.error(
                        str(type(e).__name__) +
                        'in ExecuteViewActionsActionHandler', action['view'])
                    traceback.print_exc(file=sys.stdout)
                if response_data is not None:
                    return 'success', response_actions, response_data
                else:
                    return 'success', response_actions

        # view not found
        notification_action = webclientActions.NotificationAction.generate(
            "View >" + viewname + "< not found", "error")
        return 'success', [notification_action]


class GetViewActionHandler(Action):
    def __init__(self, app, db, uri="getView"):
        self.uri = uri
        self.app = app
        self.db = db
        # logManager.info("Instance of GetViewActionHandler created")

    def handle(self, action, user, workspace, actionManager):
        logManager.info("Execute get view action for %s", action['view'])

        viewname = action['view']
        print(workspace.dataViews)
        if viewname in workspace.dataViews:
            print('found view', viewname, 'in', workspace.name,
                  workspace.dataViews[viewname])
            view = workspace.dataViews[viewname]

            # check if login required for this view
            if view.requireLogin is True and user is None:
                # login required but got no user identity
                notification_action = webclientActions.NotificationAction.generate(
                    "Login required", "error")
                route_action = webclientActions.RouteAction.generate('',
                                                                     delay=3)
                return 'success', [notification_action, route_action]
            else:
                # build actions to get view
                # this shows a notification on every view load, is this really necessary?
                # notification_action = webclientActions.NotificationAction.generate("Load view", "info")
                notification_action = []
                dictionary = action['query']
                entries = view.getViewHandler(user, workspace,
                                              ObjDict(dictionary))
                if type(entries) == tuple:
                    meta_data = entries[1]
                    entries = entries[0]
                else:
                    meta_data = {}
                properties = view.getProperties()
                uri = workspace.uri + '/' + view.uri
                loadviewaction = webclientActions.LoadViewAction.generate(
                    uri, properties, entries, meta_data)
                return 'success', [loadviewaction, notification_action]

        # view not found
        notification_action = webclientActions.NotificationAction.generate(
            "View >" + viewname + "< not found", "error")
        return 'success', [notification_action]
