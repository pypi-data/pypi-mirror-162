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
import pathlib
import pkgutil
import inspect
from aurori.workspaces.workspace import Workspace
from aurori.workspaces.workspaceHooks import WorkspaceHooks
from aurori.logs import logManager
import sys
import traceback
import sqlalchemy as sa


class WorkspaceManager(object):
    """ The WorkspaceManager holds all available workspaces and load them while creation.
    """
    def __init__(self, workspaceSource):
        self.workspaceSource = workspaceSource
        self.app = None
        self.db = None
        self.config = None
        self.workspaces = None

    def init_app(self, app, db, config):
        self.app = app
        self.db = db
        self.config = config
        with self.app.app_context():
            self.reloadWorkspaces()
            self.registerWorkspacePlugins()
            self.registerWorkspacePermissions()
            self.registerWorkspaceAPIs()
            logManager.info("Workspaces initialized")

    def getWorkspace(self, name):
        for w in self.workspaces:
            if w.name is name:
                return w
        return None

    def triggerWorkspaceHooks(self, hook: WorkspaceHooks, **kwargs):
        for w in self.workspaces:
            try:
                if hook == WorkspaceHooks.CREATEUSER:
                    w.createUserHook(**kwargs)
                if hook == WorkspaceHooks.REMOVEUSER:
                    w.removeUserHook(**kwargs)
            except Exception as e:
                logManager.error('Failed to run hook {} on {} with {}'.format(
                    hook, w.name, e))

    def reloadWorkspaces(self):
        """Reset the list of all plugins and initiate the walk over the main
        provided plugin package to load all available plugins
        """
        self.workspaces = []
        self.seen_paths = []
        logManager.info("")
        logManager.info(
            f'Discover workspaces in path : {self.workspaceSource}')
        self.discover_workspaces(self.workspaceSource)

    def registerWorkspacePermissions(self):
        """ Run createPermissions for all workspaces and store permissions
        """
        logManager.info("")
        all_permissions = {}
        for ws in self.workspaces:

            workspace_permissions = ws.permissions
            if workspace_permissions is not None:
                all_permissions = {**all_permissions, **workspace_permissions}
            logManager.info(
                f'Register permissions for {ws.name}-workspace : {workspace_permissions}'
            )

        logManager.info(f'Delete orphaned permissions')

        # delete orphaned permissions for security reasons
        from .models import Permission
        from aurori import db
        engine = db.get_engine()
        table_exists = sa.inspect(engine).has_table(Permission.__tablename__)
        if table_exists:
            db_permissions = Permission.query.all()
            for permission in db_permissions:
                if permission.name not in all_permissions:
                    print("Delete orphaned permission: ", permission)
                    db.session.delete(permission)
                    db.session.commit()

    def registerWorkspaceAPIs(self):
        from aurori.api.check import check_before_request

        logManager.info("")
        logManager.info("Register api's of workspaces:")
        logManager.info("")
        for w in self.workspaces:
            api_workspace_path = (self.workspaceSource) + '.' + w.name + '.api'
            try:
                api_module = __import__(api_workspace_path, fromlist=['blah'])
                module_members = inspect.getmembers(api_module)
                blueprint = None
                for _name, member in module_members:
                    if _name == 'workspace_bp':
                        blueprint = member
                if blueprint is not None:
                    logManager.info(f'Register "{w.name}" workspace API')
                    blueprint.before_request(check_before_request)
                    self.app.register_blueprint(
                        blueprint,
                        url_prefix='/api/v1/workspaces/' + str(w.name.lower()))
                    pass
            except ModuleNotFoundError:
                logManager.info(
                    f'No specific API found for "{w.name}" workspace')
        logManager.info("")

    def registerWorkspacePlugins(self):
        """Recursively walk the supplied package to retrieve components for all plugins (workspaces)
        """
        logManager.info("")
        logManager.info("Register components from workspaces:")
        logManager.info("")

        for w in self.workspaces:
            logManager.info(f'Workspace: "{w.name}"')

            # try to register permissions
            try:
                w.discoverPermissions(self.workspaceSource)
            except Exception as e:
                traceback.print_exc(file=sys.stdout)
                logManager.error(
                    f'Workspace "{w.name}" unable to discover permissions  ({str(type(e).__name__)}:{e})'
                )

            # try to register monits
            try:
                w.discoverMonits(self.workspaceSource, w)
            except ModuleNotFoundError:
                logManager.info(f'No monits discovered for "{w.name}"')
            except Exception as e:
                traceback.print_exc(file=sys.stdout)
                logManager.error(
                    f'Workspace "{w.name}" unable to discover monits  ({str(type(e).__name__)}:{e})'
                )

            # try to register dataViews
            try:
                w.discoverDataViews(self.workspaceSource)
            except Exception as e:
                traceback.print_exc(file=sys.stdout)
                logManager.error(
                    f'Workspace "{w.name}" unable to discover dataviews  ({str(type(e).__name__)}:{e})'
                )

            workspace_config_section_name = pathlib.Path(
                w.path).resolve().name.upper()

            if workspace_config_section_name in self.config and "disable_jobs" in self.config[
                    workspace_config_section_name] and self.config[
                        workspace_config_section_name]["disable_jobs"]:
                logManager.info(f'Jobs for "{w.name}" are disabled by config')
            else:
                # try to register jobs
                try:
                    w.discoverJobs(self.workspaceSource)
                except Exception as e:
                    traceback.print_exc(file=sys.stdout)
                    logManager.error(
                        f'Workspace "{w.name}" unable to discover jobs  ({str(type(e).__name__)}:{e})'
                    )

            # try to register actions
            try:
                w.discoverActions(self.workspaceSource)
            except Exception as exception:
                traceback.print_exc(file=sys.stdout)
                logManager.error(
                    f'Workspace "{w.name}" unable to discover actions  ({str(type(exception).__name__)}:{exception})'
                )

            # try to register sections
            try:
                w.discoverSections(self.workspaceSource)
            except Exception as exception:
                traceback.print_exc(file=sys.stdout)
                logManager.error(
                    f'Workspace "{w.name}" unable to discover sections  ({str(type(exception).__name__)}:{exception})'
                )

            # try to register node classes
            try:
                w.discoverNodeClasses(self.workspaceSource)
            except ModuleNotFoundError as me:
                logManager.info(f'No node classes discover for "{w.name}"')
            except Exception as exception:
                traceback.print_exc(file=sys.stdout)
                logManager.error(
                    f'Workspace "{w.name}" unable to discover node classes ' +
                    f'({str(type(exception).__name__)}:{exception})')

            # try to register permissions
            try:
                w.discoverPages(self.workspaceSource)
            except Exception as exception:
                traceback.print_exc(file=sys.stdout)
                logManager.error(
                    f'Workspace "{w.name}" unable to discover pages  ({str(type(exception).__name__)}:{exception})'
                )

            # try to register command line commands
            try:
                w.discoverCommands(self.workspaceSource)
            except Exception as exception:
                traceback.print_exc(file=sys.stdout)
                logManager.error(
                    f'Workspace "{w.name}" unable to discover commands  ({str(type(exception).__name__)}:{exception})'
                )

            # try to register widgets
            try:
                w.discoverWidgets(self.workspaceSource)
            except Exception as exception:
                traceback.print_exc(file=sys.stdout)
                logManager.error(
                    f'Workspace "{w.name}" unable to discover widgets ({str(type(exception).__name__)}:{exception})'
                )

            logManager.info("")

    def discover_models(self):
        source = self.workspaceSource
        try:
            imported_source = __import__(source, fromlist=['blah'])
        except Exception as exception:
            logManager.error(f"Unable to locate workspaces {str(exception)}")
            return
        all_current_paths = []

        # all_current_paths.append(imported_source.__path__._path)

        if isinstance(imported_source.__path__, str):
            all_current_paths.append(imported_source.__path__)
        else:
            all_current_paths.extend([x for x in imported_source.__path__])

        # remove duplicates
        all_current_paths = list(set(all_current_paths))

        for pkg_path in all_current_paths:
            # Walk through all sub directories
            child_pkgs = [
                p for p in os.listdir(pkg_path)
                if os.path.isdir(os.path.join(pkg_path, p))
            ]

            for child_pkg in child_pkgs:
                try:
                    # fixme: this was assigned to a later unused variable?
                    # imported_package = __import__(source + '.' + child_pkg + '.models', fromlist=['blah'])
                    __import__(source + '.' + child_pkg + '.models',
                               fromlist=['blah'])
                except ModuleNotFoundError:
                    modelmodule = source + '.' + child_pkg + '.models'
                    logManager.info(f'No model found for {modelmodule}')
                print(child_pkg)

    def discover_workspaces(self, source):
        """Recursively walk the supplied package to retrieve all plugins (workspaces)
        """

        try:
            imported_source = __import__(source, fromlist=['blah'])
        except Exception as e:
            logManager.error(f"Unable to locate workspaces {str(e)}")
            return

        all_current_paths = []

        # all_current_paths.append(imported_source.__path__._path)

        if isinstance(imported_source.__path__, str):
            all_current_paths.append(imported_source.__path__)
        else:
            all_current_paths.extend([x for x in imported_source.__path__])

        # remove duplicates
        all_current_paths = list(set(all_current_paths))

        for pkg_path in all_current_paths:
            # Walk through all sub directories
            child_pkgs = [
                p for p in os.listdir(pkg_path)
                if os.path.isdir(os.path.join(pkg_path, p))
            ]

            # Every sub directory contains one workspace
            for child_pkg in child_pkgs:
                imported_package = __import__(source + '.' + child_pkg,
                                              fromlist=['blah'])
                for _, workspacename, ispkg in pkgutil.iter_modules(
                        imported_package.__path__,
                        imported_package.__name__ + '.'):
                    workspaceCounter = 0
                    if not ispkg:
                        workspace_module = __import__(workspacename,
                                                      fromlist=['blah'])
                        clsmembers = inspect.getmembers(
                            workspace_module, inspect.isclass)

                        for (_, c) in clsmembers:
                            # Check for workspace classes
                            if issubclass(c, Workspace) & (c is not Workspace):
                                workspaceCounter += 1
                                if workspaceCounter > 1:
                                    logManager.error(
                                        'Only one workspace is allowed for one folder, other workspaces will skipped'
                                    )
                                    break

                                uri = ""
                                if hasattr(c, 'uri'):
                                    uri = c.uri
                                else:
                                    logManager.error(
                                        f'No uri defined and will not be accessable for workspace: {c.__module__}'
                                    )

                                name = c.__name__
                                if hasattr(c, 'name'):
                                    name = c.name
                                workspaceInstance = c(self.app, self.db, name,
                                                      uri)
                                workspaceInstance.path = os.path.dirname(
                                    workspace_module.__file__)
                                workspace_config_section_name = pathlib.Path(
                                    workspace_module.__file__).parent.resolve(
                                    ).name.upper()
                                logManager.info(
                                    f'Workspace discovered : {workspaceInstance.name} [{c.__module__}]'
                                    + f' with uri "{workspaceInstance.uri}"')

                                if (workspace_config_section_name
                                        in self.config) and (
                                            "disable" in self.config[
                                                workspace_config_section_name]
                                        ) and (self.config[
                                            workspace_config_section_name]
                                               ["disable"]):
                                    logManager.info(
                                        f'Workspace {workspaceInstance.name} [{c.__module__}]'
                                        +
                                        ' is disabled by config and wont show up'
                                    )
                                else:
                                    if workspaceInstance.disable is True:
                                        logManager.info(
                                            f'Workspace {workspaceInstance.name} [{c.__module__}]'
                                            +
                                            ' is disabled by definition and wont show up'
                                        )
                                    else:
                                        self.workspaces.append(
                                            workspaceInstance)
