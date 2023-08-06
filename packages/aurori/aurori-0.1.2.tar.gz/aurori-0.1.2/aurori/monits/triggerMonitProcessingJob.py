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


class TriggerMonitsProcessingJob(Job):

    cron = True
    minute = "*/15"
    disable = False
    description = "Update the account for monthly access budget users"

    def run(self, **kwargs):
        from aurori.monits import monit_manager

        for m in list(monit_manager.monits.values()):
            monit_manager.trigger_monit_processing(m)
        logManager.info("TriggerMonitsProcessingJob done")
