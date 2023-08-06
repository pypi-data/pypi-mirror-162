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
from aurori.jobs import jobManager, add_dated_job

from aurori.monits.monits import Monit
from aurori.monits.events import MonitorBaseEvent
from aurori.monits.types import MonitType, MonitViewStats, MonitPropertyType, MonitChartType
from aurori.monits.processMonitJob import ProcessMonitJob
from aurori.monits.triggerMonitProcessingJob import TriggerMonitsProcessingJob
from aurori.monits.cleanupMonitorEventsJob import CleanupMonitorEventsJob
from aurori.monits.cleanupMonitorItemsJob import CleanupMonitorItemsJob

import datetime


class MonitManager(object):
    """ The MonitManager ...
    """
    def __init__(self, ):
        self.monits = {}
        self.config = None
        self.app = None
        self.db = None
        self.workspaceManager = None
        self.userManager = None

    def init_manager(self, app, db, userManager, workspaceManager, config):
        self.config = config
        self.app = app
        self.db = db
        self.workspaceManager = workspaceManager
        self.userManager = userManager

        from aurori.monits.models import MonitorEvent, MonitorViewItem
        self.MonitorEvent = MonitorEvent
        self.MonitorViewItem = MonitorViewItem

        jobManager.register_job(None, ProcessMonitJob)
        jobManager.register_job(None, TriggerMonitsProcessingJob)
        jobManager.register_job(None, CleanupMonitorEventsJob)
        jobManager.register_job(None, CleanupMonitorItemsJob)
        logManager.info("MonitManager initialized")

    def _get_key_from_monit_and_workspace_name(self, monit_name,
                                               workspace_name):
        key = monit_name
        if workspace_name is not None and workspace_name != '':
            key = workspace_name + '.' + key
        else:
            # add system monit group key
            key = '~' + '.' + key
        return key

    def _get_key_from_monit(self, monit: Monit):
        if monit.workspace is not None:
            workspace_name = monit.workspace.name
        else:
            workspace_name = None
        return self._get_key_from_monit_and_workspace_name(
            monit.name, workspace_name)

    def trigger_monit_processing(self, monit: Monit):
        key = self._get_key_from_monit(monit)
        args = {
            'monit': self.monits[self._get_key_from_monit(monit)],
            'monit_key': key,
        }
        add_dated_job(None, ProcessMonitJob(), args)

    def get_monits_list(self,
                        workspace=None,
                        group=None,
                        subgroup=None,
                        get_system_monits=False):
        return self.monits

    def get_monit_view(self, monit, view_name):
        for v in monit.views:
            if v.name == view_name:
                return v
        return None

    def get_value_from_item(self, item, last_item, _monit, view):
        if item is not None:
            if view.display_property == MonitPropertyType.COUNT:
                return item.values_count
            if view.display_property == MonitPropertyType.SUM:
                return item.values_sum
            if view.display_property == MonitPropertyType.AVERAGE:
                return item.values_average
            if view.display_property == MonitPropertyType.LAST_VALUE:
                return item.values_last
            if view.display_property == MonitPropertyType.TOTAL_COUNT:
                if item is not None and item.total_count is not None:
                    return item.total_count
                else:
                    return 0
            if view.display_property == MonitPropertyType.TOTAL_SUM:
                if item is not None and item.total_sum is not None:
                    return item.total_sum
                else:
                    return 0
        else:
            if view.display_property == MonitPropertyType.COUNT:
                return 0
            if view.display_property == MonitPropertyType.SUM:
                return 0
            if view.display_property == MonitPropertyType.AVERAGE:
                return None
            if view.display_property == MonitPropertyType.LAST_VALUE:
                return None
            if view.display_property == MonitPropertyType.TOTAL_COUNT:
                if last_item is not None and last_item.total_count is not None:
                    return last_item.total_count
                else:
                    return 0
            if view.display_property == MonitPropertyType.TOTAL_SUM:
                if last_item is not None and last_item.total_sum is not None:
                    return last_item.total_sum
                else:
                    return 0

    def get_chart_type(self, monit, view):
        if monit.monit_type == MonitType.BUFFER:
            return 'scatter'
        if monit.monit_type == MonitType.PROPERTIES_ONLY:
            return 'bar'
        if monit.monit_type == MonitType.TIMELINE:
            if view.chart_type == MonitChartType.LINE:
                return 'line'
            else:
                return 'bar'

    def get_monit_view_chart_data(self, monit_key, view_name):
        monit = self.monits[monit_key]
        view = self.get_monit_view(monit, view_name)
        chart_data = {
            'timeline_data': [],
            'series_data': [],
            'xAxesType': 'category'
        }
        classifiers = self.get_monit_view_classifier(monit, view)
        classifiers_series_index = {}
        timeline = {}
        last_classifier_item = {}

        # prepare timeline data structures

        for c in classifiers:
            classifiers_series_index[c] = len(chart_data['series_data'])
            last_classifier_item[c] = None
            if c is not None:
                chart_data['series_data'].append({
                    'label':
                    c,
                    'data': [],
                    'type':
                    self.get_chart_type(monit, view)
                })
                if view.chart_type == MonitChartType.BAR:
                    chart_data['series_data'][-1]['data'].append("0")

            else:
                chart_data['series_data'].append({
                    'label':
                    view.label,
                    'data': [],
                    'type':
                    self.get_chart_type(monit, view)
                })
                if view.chart_type == MonitChartType.BAR:
                    chart_data['series_data'][-1]['data'].append("0")

        if monit.monit_type == MonitType.BUFFER:
            chart_data['xAxesType'] = 'time'
            view_items = self.MonitorViewItem.query.filter(
                self.MonitorViewItem.monit_key == monit_key,
                self.MonitorViewItem.timestamp != None,
                self.MonitorViewItem.year == None,
                self.MonitorViewItem.month == None,
                self.MonitorViewItem.day == None,
                self.MonitorViewItem.hour == None).order_by(
                    self.MonitorViewItem.timestamp.asc()).all()
            for i in view_items:
                timestamp = i.timestamp.isoformat(" ")
                last_classifier_item[i.classifier] = i
                chart_data['series_data'][classifiers_series_index[
                    i.classifier]]['data'].append([
                        timestamp,
                        self.get_value_from_item(
                            i, last_classifier_item[i.classifier], monit, view)
                    ])
                chart_data['timeline_data'].append(timestamp)
                pass

        if monit.monit_type == MonitType.TIMELINE:
            if view.chart_type == MonitChartType.BAR:
                chart_data['timeline_data'].append("")

            # chart_data['xAxesType'] = 'time'
            view_items = self.MonitorViewItem.query.filter(
                self.MonitorViewItem.monit_key == monit_key,
                self.MonitorViewItem.timestamp is None,
                self.MonitorViewItem.year is not None,
                self.MonitorViewItem.month is not None,
                self.MonitorViewItem.day is not None, self.MonitorViewItem.hour
                is not None).order_by(self.MonitorViewItem.year.asc(),
                                      self.MonitorViewItem.month.asc(),
                                      self.MonitorViewItem.day.asc(),
                                      self.MonitorViewItem.hour.asc()).all()
            last_item = None
            last_item_datetime = None
            for i in view_items:
                actual_item_datetime = datetime.datetime(year=i.year,
                                                         month=i.month,
                                                         day=i.day,
                                                         hour=i.hour)
                time_delta = datetime.timedelta(hours=1)
                if view.fill_timeline_gaps is True and last_item is not None:
                    while last_item_datetime + time_delta <= actual_item_datetime:
                        time_string = last_item_datetime.strftime(
                            "%Y-%m-%d-%Hh")
                        if time_string not in timeline:
                            timeline[time_string] = {}
                        if view.display_property == MonitPropertyType.TOTAL_SUM or view.display_property == MonitPropertyType.TOTAL_COUNT:
                            timeline[time_string][
                                last_item.classifier] = last_item
                        else:
                            timeline[time_string][last_item.classifier] = None
                        last_item_datetime += time_delta
                if last_item is not None or actual_item_datetime == last_item_datetime:
                    time_string = actual_item_datetime.strftime("%Y-%m-%d-%Hh")
                    if time_string not in timeline:
                        timeline[time_string] = {}
                    timeline[time_string][i.classifier] = i
                last_item = i
                last_item_datetime = datetime.datetime(year=i.year,
                                                       month=i.month,
                                                       day=i.day,
                                                       hour=i.hour)
                last_item_datetime += time_delta

            for k, s in timeline.items():
                chart_data['timeline_data'].append(k)
                for c in classifiers:
                    if c in s:
                        last_classifier_item[c] = s[c]
                        chart_data['series_data'][
                            classifiers_series_index[c]]['data'].append(
                                self.get_value_from_item(
                                    s[c], last_classifier_item[c], monit,
                                    view))
                    else:
                        chart_data['series_data'][
                            classifiers_series_index[c]]['data'].append(
                                self.get_value_from_item(
                                    None, last_classifier_item[c], monit,
                                    view))
            if view.chart_type == MonitChartType.BAR:
                chart_data['timeline_data'].append("")
        return chart_data
        '''
            this.chart_data.timeline_data = ["Mo.", "Tu2"];
            this.chart_data.series_data = [
            {
                label: "SeriesA",
                data: [1, 2.2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            },
            {
                label: "SeriesB",
                data: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            },
            {
                label: "SeriesC",
                data: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            },
            ];
        '''

    def get_monit_view_stats(self, monit, view) -> MonitViewStats:
        monit_key = self._get_key_from_monit(monit)
        general_view_items = self.MonitorViewItem.query.filter(
            self.MonitorViewItem.monit_key == monit_key,
            self.MonitorViewItem.classifier == None,
            self.MonitorViewItem.timestamp == None,
            self.MonitorViewItem.year == None,
            self.MonitorViewItem.month == None,
            self.MonitorViewItem.day == None,
            self.MonitorViewItem.hour == None).first()
        if general_view_items is not None:
            stats = MonitViewStats(
                min=general_view_items.values_min,
                max=general_view_items.values_max,
                average=general_view_items.values_average,
                count=general_view_items.values_count,
                sum=general_view_items.values_sum,
                last=general_view_items.values_last,
                last_event_at=general_view_items.last_event_at,
                last_reset_at=general_view_items.last_reset_at)
        else:
            stats = MonitViewStats(min=None,
                                   max=None,
                                   average=None,
                                   count=None,
                                   sum=None,
                                   last=None,
                                   last_event_at=None,
                                   last_reset_at=None)
        return stats

    def get_monit_view_classifier(self, monit, view) -> list:
        monit_key = self._get_key_from_monit(monit)
        monit_classifier_view_items = self.MonitorViewItem.query.filter(
            self.MonitorViewItem.monit_key == monit_key,
            self.MonitorViewItem.timestamp == None,
            self.MonitorViewItem.year == None,
            self.MonitorViewItem.month == None,
            self.MonitorViewItem.day == None,
            self.MonitorViewItem.hour == None).all()

        classifier = []
        if len(monit_classifier_view_items) == 0:
            pass
        else:
            if len(monit_classifier_view_items) == 1:
                classifier.append(monit_classifier_view_items[0].classifier)
            else:
                for c in monit_classifier_view_items:
                    if c.classifier is not None:
                        classifier.append(c.classifier)
        return classifier

    def register_monit(self, monit: Monit):
        self.monits[self._get_key_from_monit(monit)] = monit

    def raise_monitor_event(self, event: MonitorBaseEvent):
        logManager.info(f"Monitor event raised: {event}")
        e = self.MonitorEvent()
        e.name = event.name
        e.classifier = event.classifier
        e.value = event.value
        if event.timestamp is not None:
            e.timestamp = event.timestamp
        self.db.session.add(e)
