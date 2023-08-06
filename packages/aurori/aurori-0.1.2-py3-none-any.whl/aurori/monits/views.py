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

from aurori.monits.types import MonitChartType, MonitPropertyType, MonitTimeSpanDisplayType

ALL = ["*"]


class MonitView(object):
    def __init__(self,
                 name,
                 label,
                 chart_type: MonitChartType,
                 description="",
                 display_classifier=ALL,
                 display_property=MonitPropertyType.SUM,
                 display_timespan=MonitTimeSpanDisplayType.WEEK,
                 fill_timeline_gaps=False):
        self.name = name
        self.label = label
        self.description = description
        self.display_classifier = display_classifier
        self.display_property = display_property
        self.display_timespan = display_timespan
        self.chart_type = chart_type
        self.fill_timeline_gaps = fill_timeline_gaps
