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

from aurori.jobs.job import Job
from aurori.logs import logManager
from datetime import datetime, timedelta


class CleanupMonitorEventsJob(Job):

    cron = True
    hour = "*/4"
    minute = "0"
    disable = False
    description = "Cleanup monitor events"

    def run(self, **kwargs):
        from aurori.monits.models import MonitorEvent
        now = datetime.utcnow()
        datetime_threshold = now.replace(minute=0, second=0,
                                         microsecond=0) - timedelta(hours=2)

        monit_event_older_2hours = MonitorEvent.query.filter(
            MonitorEvent.created_at < datetime_threshold).all()
        for m in monit_event_older_2hours:
            self.db.session.delete(m)
        logManager.info("CleanupMonitorEventsJob done")
