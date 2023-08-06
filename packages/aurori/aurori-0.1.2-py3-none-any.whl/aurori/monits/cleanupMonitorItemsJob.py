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

from datetime import datetime, timedelta

from aurori.logs import logManager
from aurori.jobs.job import Job


class CleanupMonitorItemsJob(Job):

    cron = True
    hour = "*/4"
    minute = "0"
    disable = False
    description = "Cleanup monitor view items"

    def run(self, **kwargs):
        from aurori.monits import monit_manager
        from aurori.monits.models import MonitorEvent, MonitorViewItem
        now = datetime.utcnow()

        # remove all items from type buffer older than 1 week
        datetime_threshold = now.replace(minute=0, second=0,
                                         microsecond=0) - timedelta(days=7)
        monit_event_older_1week = MonitorViewItem.query.filter(
            MonitorViewItem.timestamp != None,
            MonitorViewItem.created_at < datetime_threshold).all()
        for m in monit_event_older_1week:
            self.db.session.delete(m)

        # remove all items from type timeline older than 2 month
        datetime_threshold = now.replace(minute=0, second=0,
                                         microsecond=0) - timedelta(days=60)
        monit_event_older_1week = MonitorViewItem.query.filter(
            MonitorViewItem.hour != None,
            MonitorViewItem.created_at < datetime_threshold).all()
        for m in monit_event_older_1week:
            self.db.session.delete(m)
        logManager.info("CleanupMonitorItemsJob done")