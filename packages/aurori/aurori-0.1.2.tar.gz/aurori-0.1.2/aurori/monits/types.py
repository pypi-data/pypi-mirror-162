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

from enum import Enum


class MonitType(Enum):
    PROPERTIES_ONLY = "PROPERTIES_ONLY"  # all properties only (e.g. count, last, average, min, max)
    TIMELINE = "TIMELINE"  # timeline monit of events aggregated (see MonitPropertyType)
    BUFFER = "BUFFER"  # a fixed size buffer (circular buffer) containing the events


class MonitChartType(Enum):
    SCATTER = "SCATTER"
    LINE = "LINE"
    BAR = "BAR"
    NONE = "NONE"


class MonitTimeAggregationType(Enum):
    HOURLY = "HOURLY"  # aggregate events to hourly timespan
    DAILY = "DAILY"  # aggregate events to daily timespan
    MONTHLY = "MONTHLY"  # aggregate events to monthly timespan


class MonitTimeSpanDisplayType(Enum):
    DAY = "DAY"  # aggregate events to hourly timespan
    WEEK = "WEEK"  # aggregate events to daily timespan
    MONTH = "MONTH"  # aggregate events to monthly timespan
    UNSET = "UNSET"


class MonitPropertyType(Enum):
    COUNT = "COUNT"  # count the events in the aggr. timespan (ignore values)
    LAST_VALUE = "LAST VALUE"  # take the last value from all events in the aggr. timespan
    SUM = "SUM"  # sum the values of all events in the aggr. timespan
    AVERAGE = "AVERAGE"  # take the average of the values from all events in the aggr. timespan
    TOTAL_COUNT = "TOTAL COUNT"
    TOTAL_SUM = "TOTAL COUNT"
    UNSET = "UNSET"


class MonitViewStats(object):
    def __init__(self, last, min, max, average, sum, count, last_event_at,
                 last_reset_at):
        self.last = last
        self.min = min
        self.max = max
        self.average = average
        self.sum = sum
        self.count = count
        self.last_event_at = last_event_at
        self.last_reset_at = last_reset_at