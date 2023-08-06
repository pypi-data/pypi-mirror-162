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

import sys
import collections
import datetime
import threading


class LogManager(object):
    def __init__(self):
        self.logQueue = collections.deque(maxlen=512)
        self.app = None

    def init_app(self, app):
        self.app = app
        gettrace = getattr(sys, 'gettrace', None)
        if gettrace and gettrace():
            self.run_in_debug_mode = True
        else:
            self.run_in_debug_mode = False

    def info(self, msg, *args, **kwargs):
        """
        Delegate a info log call to the underlying logger,
        """
        if self.app is None:
            return
        if type(msg) is str:
            try:
                s = msg % args
            except Exception:
                s = msg.format(*args)
            indents = s.replace("\n", "\n" + " " * 29)
            self.logQueue.append(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                " [INFO] : " + indents)
        else:
            s = str(msg)
            indents = s.replace("\n", "\n" + " " * 29)
            self.logQueue.append(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                " [INFO] : " + indents)
        try:
            self.app.logger.info(msg, *args, **kwargs)
            indents = s.replace("\n", "\n" + " " * 14)
            print("[{:4.4}][INFO]: {}".format(threading.current_thread().name,
                                              indents))
        except Exception as e:
            print("logger failed to print: ", s, e)

    def warning(self, msg, *args, **kwargs):
        """
        Delegate a warning log call to the underlying logger,
        """
        if type(msg) is str:
            try:
                s = msg % args
            except Exception:
                s = msg
            self.logQueue.append(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                " [WARN] : " + s)
        else:
            s = str(msg)
            self.logQueue.append(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                " [WARN] : " + s)

        try:
            self.app.logger.info(msg, *args, **kwargs)
            print("[WARNING]:", s)
        except Exception:
            print("logger failed to print: ", s)

    def error(self, msg, *args, **kwargs):
        """
        Delegate a error log call to the underlying logger,
        """
        if type(msg) is str:
            try:
                s = msg % args
            except Exception:
                s = msg
            self.logQueue.append(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                " [FAIL] : " + s)
        else:
            s = str(msg)
            self.logQueue.append(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                " [FAIL] : " + s)

        try:
            self.app.logger.info(msg, *args, **kwargs)
            print("[FAIL]:", s)
        except Exception:
            print("logger failed to print: ", s)

    def debug(self, msg, *args, **kwargs):
        """
        Delegate a error log call to the underlying logger,
        """
        if self.run_in_debug_mode is not True:
            return
        if type(msg) is str:
            try:
                s = msg % args
            except Exception:
                s = msg
            self.logQueue.append(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                " [DEBUG] : " + s)
        else:
            s = str(msg)
            self.logQueue.append(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
                " [DEBUG] : " + s)

        try:
            self.app.logger.info(msg, *args, **kwargs)
            print("[DEBUG]:", s)
        except Exception:
            print("logger failed to print: ", s)
