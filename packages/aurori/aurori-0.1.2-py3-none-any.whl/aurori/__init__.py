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

import logging
import sys
from os import environ

from flask import Flask, Blueprint
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from sqlalchemy_utils import database_exists

from aurori.config import configure_app, config_manager
from aurori.version import version
from aurori.logs import logManager
from aurori.workspaces import workspaceManager
from aurori.nodes import nodeManager
from aurori.users import userManager
from aurori.messages import messageManager
from aurori.monits import monit_manager
from aurori.jobs import jobManager
from aurori.actions import actionManager
from aurori.files import fileManager
from aurori.menus import menuBuilder
from aurori.openproject import openprojectManager
from aurori.widgets import widgetManager

jwt = JWTManager()
db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()

__version__ = version


def create_app(config, flask_config=None, minimal=False):
    config_manager.init_manager(config, flask_config)
    app = Flask(__name__, static_folder="./client")
    # configure the app
    configure_app(app, config, flask_config)

    if __name__ != '__main__':
        gunicorn_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
        if 'log_level' in config['SYSTEM']:
            app.logger.setLevel(
                logging._nameToLevel.get(config['SYSTEM']['log_level']))
    # logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')

    gettrace = getattr(sys, 'gettrace', None)
    if gettrace and gettrace():
        app.logger.setLevel(logging.DEBUG)

    if not minimal:
        CORS(app)
        logManager.init_app(app)
        logManager.info("Aurori framework started: " + version)
        jwt.init_app(app)
        workspaceManager.discover_models()
        bcrypt.init_app(app)

    from aurori import app_bp
    app.register_blueprint(app_bp)

    from aurori.actions import actions_bp, models  # noqa: F401, F811
    app.register_blueprint(actions_bp)

    from aurori.monits import monit_bp, models  # noqa: F401, F811
    app.register_blueprint(monit_bp)

    from aurori.users import auth_bp, models  # noqa: F401, F811
    app.register_blueprint(auth_bp)

    from aurori.logs import logs_bp
    app.register_blueprint(logs_bp)

    from aurori.jobs import jobs_bp
    app.register_blueprint(jobs_bp)

    from aurori.messages import messages_bp
    app.register_blueprint(messages_bp)

    from aurori.files import files_bp
    app.register_blueprint(files_bp)

    from aurori.nodes import nodes_bp
    app.register_blueprint(nodes_bp)

    from aurori.openproject import openproject_bp
    app.register_blueprint(openproject_bp)

    # import workspace blueprint and models
    from aurori.workspaces import workspaces_bp
    from aurori.workspaces import models

    app.register_blueprint(workspaces_bp)

    from aurori.api import api_bp
    app.register_blueprint(api_bp)

    from aurori.widgets import widgets_bp
    app.register_blueprint(widgets_bp)

    is_database_new = not database_exists(
        app.config['SQLALCHEMY_DATABASE_URI'])

    only_create_all_on_new_database_env = environ.get(
        'ONLY_CREATE_ALL_ON_NEW_DATABASE')
    if only_create_all_on_new_database_env is None:
        check_for_database_new = True
    else:
        if only_create_all_on_new_database_env == "1":
            check_for_database_new = True
        else:
            check_for_database_new = False

    db.init_app(app)

    # only create all schemas for new databases
    # otherwise this breaks the migration path
    if is_database_new or check_for_database_new is False:
        with app.app_context():
            db.create_all()

    if not minimal:
        migrate.init_app(app, db)
        jobManager.init_manager(app, db, config_manager.config)
        workspaceManager.init_app(app, db, config_manager.config)
        userManager.init_manager(app, db, workspaceManager,
                                 config_manager.config)
        monit_manager.init_manager(app, db, userManager, workspaceManager,
                                   config_manager.config)
        nodeManager.init_manager(app, db, workspaceManager)
        messageManager.init_manager(app, db, workspaceManager,
                                    config_manager.config)
        menuBuilder.init_builder(app, db, userManager, workspaceManager)
        actionManager.init_manager(app, db, userManager, menuBuilder,
                                   workspaceManager, nodeManager,
                                   config_manager.config)
        fileManager.init_manager(app, db, config_manager.config)
        openprojectManager.init_manager(app, db, openprojectManager,
                                        config_manager.config)
        widgetManager.init_manager(app, db, userManager, workspaceManager,
                                   config_manager.config)

    return app


# declare app routes
app_bp = Blueprint('app', __name__, static_folder="../client")
from aurori import routes
