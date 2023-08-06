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
from aurori.monits.types import MonitChartType, MonitType, MonitPropertyType
from aurori.monits.types import MonitTimeAggregationType, MonitTimeSpanDisplayType
from aurori.monits.views import MonitView, ALL


class Monit(object):
    group = None
    subgroup = None
    event = None
    description = ""
    monit_type = MonitType.PROPERTIES_ONLY
    monit_time_aggregation = MonitTimeAggregationType.HOURLY
    monit_display_time_span = MonitTimeSpanDisplayType.UNSET
    monit_display_property = MonitPropertyType.UNSET
    resetable = False  # allow the monit to be reseted mannualy
    floating_average_size = 100

    def __init__(self, workspace):
        self.workspace = workspace
        if not hasattr(self, 'name'):
            self.name = self.__class__.__name__
        self.views = []

    def add_barchart_view(self,
                          name,
                          label,
                          display_property,
                          display_classifier=ALL,
                          display_timespan=MonitTimeSpanDisplayType.WEEK,
                          fill_timeline_gaps=False,
                          description=""):
        view = MonitView(name,
                         label,
                         MonitChartType.BAR,
                         description,
                         display_classifier,
                         display_property,
                         display_timespan,
                         fill_timeline_gaps=fill_timeline_gaps)
        self_type = type(self)
        if self_type.monit_type == MonitType.PROPERTIES_ONLY:
            logManager.error(f"Unable to add bar chart monit view: \
                    {self.workspace.name}{str(self_type)}.{name} \
                        for a PROPERTIES_ONLY monit.")
            return

        if self_type.monit_type == MonitType.BUFFER:
            logManager.error(f"Unable to add bar chart monit view: \
                    {self.workspace.name}{str(self_type)}.{name} \
                        for a BUFFER type only scatter charts are allowed.")
            return
        self.views.append(view)

    def add_timelinechart_view(self,
                               name,
                               label,
                               display_property,
                               display_classifier=ALL,
                               display_timespan=MonitTimeSpanDisplayType.WEEK,
                               fill_timeline_gaps=False,
                               description=""):
        view = MonitView(name,
                         label,
                         MonitChartType.LINE,
                         description,
                         display_classifier,
                         display_property,
                         display_timespan,
                         fill_timeline_gaps=fill_timeline_gaps)
        self_type = type(self)
        if self_type.monit_type == MonitType.PROPERTIES_ONLY:
            logManager.error(f"Unable to add line chart monit view: \
                    {self.workspace.name}{str(self_type)}.{name} \
                        for a PROPERTIES_ONLY monit.")
            return

        if self_type.monit_type == MonitType.BUFFER:
            logManager.error(f"Unable to add line chart monit view: \
                    {self.workspace.name}{str(self_type)}.{name} \
                        for a BUFFER type only scatter charts are allowed.")
            return
        self.views.append(view)

    def add_bufferscatter_view(self,
                               name,
                               label,
                               display_property,
                               display_classifier=ALL,
                               description=""):
        self_type = type(self)
        view = MonitView(name,
                         label,
                         MonitChartType.SCATTER,
                         description,
                         display_classifier,
                         display_property,
                         fill_timeline_gaps=False)
        if self_type.monit_type == MonitType.PROPERTIES_ONLY:
            logManager.error(f"Unable to add scatter chart monit view: \
                    {self.workspace.name}{str(self_type)}.{name} \
                        for a PROPERTIES_ONLY monit.")
            return
        self.views.append(view)

    def add_property_view(self,
                          name,
                          label,
                          description="",
                          display_classifier=ALL):
        view = MonitView(name, label, MonitChartType.NONE, description,
                         display_classifier)
        self.views.append(view)

    def define_views(self):
        self_type = type(self)
        if self_type.monit_type == MonitType.PROPERTIES_ONLY:
            self.add_property_view("base", "Stats")
        self_type
        timespan = self_type.monit_display_time_span
        if timespan is MonitTimeSpanDisplayType.UNSET:
            timespan = MonitTimeSpanDisplayType.WEEK
        if self_type.monit_type == MonitType.TIMELINE:
            if self_type.monit_display_property is MonitPropertyType.UNSET:
                self.add_timelinechart_view("base", "Count",
                                            MonitPropertyType.COUNT, timespan)
            else:
                self.add_bufferscatter_view(
                    "base",
                    str(self_type.monit_display_property.value.title()),
                    self_type.monit_display_property)
        if self_type.monit_type == MonitType.BUFFER:
            if self_type.monit_display_property is MonitPropertyType.UNSET:
                self.add_bufferscatter_view("base", "Value",
                                            MonitPropertyType.LAST_VALUE)
            else:
                self.add_bufferscatter_view(
                    "base",
                    str(self_type.monit_display_property.value.title()),
                    self_type.monit_display_property)
        pass