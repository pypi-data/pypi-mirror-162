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
from datetime import datetime, timedelta
from aurori.monits.types import MonitType


def update_monitor_view_item_from_event(view_item,
                                        event,
                                        floating_average_size,
                                        update_total=True):
    view_item.values_last = event.value
    if view_item.values_max is None:
        view_item.values_max = event.value
    if event.value > view_item.values_max:
        view_item.values_max = event.value
    if view_item.values_min is None:
        view_item.values_min = event.value
    if event.value < view_item.values_min:
        view_item.values_min = event.value
    if view_item.values_count is None:
        view_item.values_count = 0
    view_item.values_count += 1
    if update_total is True and view_item.total_count is not None:
        view_item.total_count += 1
    if view_item.values_sum is None:
        view_item.values_sum = 0.0
    view_item.values_sum += event.value
    if update_total is True and view_item.total_sum is not None:
        view_item.total_sum += event.value
    if view_item.values_count <= floating_average_size:
        view_item.values_average = view_item.values_sum / view_item.values_count
    else:
        view_item.values_average = (view_item.values_average *
                                    (floating_average_size - 1) +
                                    event.value) / floating_average_size

    view_item.last_event_at = event.timestamp


def get_view_item_for_classifier_from_list(view_items, classifier):
    if view_items is None or len(view_items) == 0:
        return None
    for i in view_items:
        if i.classifier == classifier:
            return i
    return None


class ProcessMonitJob(Job):

    description = "Process a monit"

    def define_arguments(self):
        self.addDictArgument('monit',
                             label="The monit",
                             description="The monit to process")

    def run(self, **kwargs):
        from aurori.monits.models import MonitorEvent, MonitorViewItem
        monit_dict = kwargs['monit']
        monit_key = kwargs['monit_key']
        floating_average_size = monit_dict.floating_average_size
        now = datetime.utcnow()
        current_hour_threshold = now.replace(minute=0, second=0, microsecond=0)
        last_hour_threshold = now.replace(minute=0, second=0,
                                          microsecond=0) - timedelta(hours=1)

        monit_events_of_actual_and_last_hour = MonitorEvent.query.filter(
            MonitorEvent.timestamp >= last_hour_threshold,
            MonitorEvent.name == monit_dict.event.name).order_by(
                MonitorEvent.timestamp.asc()).all()
        # get the events of the actual hour
        monit_events_of_actual_hour = MonitorEvent.query.filter(
            MonitorEvent.timestamp >= current_hour_threshold,
            MonitorEvent.name == monit_dict.event.name).order_by(
                MonitorEvent.timestamp.asc()).all()
        # get the events of the last hour
        monit_events_of_last_hour = MonitorEvent.query.filter(
            MonitorEvent.timestamp >= last_hour_threshold,
            MonitorEvent.timestamp <= current_hour_threshold,
            MonitorEvent.name == monit_dict.event.name).order_by(
                MonitorEvent.timestamp.asc()).all()

        # get the monits general view items
        # the gernal view items store the general statistics
        # they are stored in addition to the time aggreated view items
        monit_global_view_items = MonitorViewItem.query.filter(
            MonitorViewItem.monit_key == monit_key,
            MonitorViewItem.timestamp is None, MonitorViewItem.year is None,
            MonitorViewItem.month is None, MonitorViewItem.day is None,
            MonitorViewItem.hour is None).all()

        if (monit_dict.monit_type == MonitType.TIMELINE):
            monit_current_hour_view_items = MonitorViewItem.query.filter(
                MonitorViewItem.monit_key == monit_key,
                MonitorViewItem.timestamp is None,
                MonitorViewItem.year == current_hour_threshold.year,
                MonitorViewItem.month == current_hour_threshold.month,
                MonitorViewItem.day == current_hour_threshold.day,
                MonitorViewItem.hour == current_hour_threshold.hour).order_by(
                    MonitorViewItem.timestamp.asc()).all()

            monit_last_hour_view_items = MonitorViewItem.query.filter(
                MonitorViewItem.monit_key == monit_key,
                MonitorViewItem.timestamp is None,
                MonitorViewItem.year == last_hour_threshold.year,
                MonitorViewItem.month == last_hour_threshold.month,
                MonitorViewItem.day == last_hour_threshold.day,
                MonitorViewItem.hour == last_hour_threshold.hour).order_by(
                    MonitorViewItem.timestamp.asc()).all()
        else:
            monit_container_view_items = MonitorViewItem.query.filter(
                MonitorViewItem.monit_key == monit_key,
                MonitorViewItem.timestamp != None).order_by(
                    MonitorViewItem.timestamp.desc()).first()
            print(monit_container_view_items)

        global_general_view_item = None
        if len(monit_global_view_items) == 0:
            # create
            global_general_view_item = MonitorViewItem(monit_key=monit_key)
            self.db.session.add(global_general_view_item)
        else:
            global_general_view_item = get_view_item_for_classifier_from_list(
                monit_global_view_items, None)

        # global_classifier_view_item = None
        # if check_for_classifier(monit_global_view_items,) is None:

        for e in monit_events_of_actual_and_last_hour:
            classifier = e.classifier
            # update the global general view item for the monit
            if (global_general_view_item.last_event_at is None) \
                    or (e.timestamp > global_general_view_item.last_event_at):
                update_monitor_view_item_from_event(global_general_view_item,
                                                    e, floating_average_size)

            if classifier is not None:
                # check for global classifier view item
                global_classifier_view_item = get_view_item_for_classifier_from_list(
                    monit_global_view_items, classifier)
                if global_classifier_view_item is None:
                    global_classifier_view_item = MonitorViewItem(
                        monit_key=monit_key, classifier=classifier)
                    monit_global_view_items.append(global_classifier_view_item)
                    self.db.session.add(global_classifier_view_item)

                if (global_classifier_view_item.last_event_at is None) \
                        or (e.timestamp > global_classifier_view_item.last_event_at):
                    update_monitor_view_item_from_event(
                        global_classifier_view_item, e, floating_average_size)

            if monit_dict.monit_type == MonitType.BUFFER:
                if (monit_container_view_items is None) \
                        or (monit_container_view_items.last_event_at is None) \
                        or (e.timestamp > monit_container_view_items.last_event_at):
                    container_view_item = MonitorViewItem(
                        monit_key=monit_key, classifier=classifier)
                    container_view_item.timestamp = e.timestamp
                    update_monitor_view_item_from_event(
                        container_view_item, e, floating_average_size)
                    self.db.session.add(container_view_item)

        if (monit_dict.monit_type == MonitType.TIMELINE):
            update_total = True
            for e in monit_events_of_last_hour:
                classifier = e.classifier

                monit_last_hour_classifier_item = get_view_item_for_classifier_from_list(
                    monit_last_hour_view_items, classifier)

                if monit_last_hour_classifier_item is None:
                    monit_last_hour_classifier_item = MonitorViewItem(
                        monit_key=monit_key, classifier=classifier)
                    monit_last_hour_classifier_item.year = last_hour_threshold.year
                    monit_last_hour_classifier_item.month = last_hour_threshold.month
                    monit_last_hour_classifier_item.day = last_hour_threshold.day
                    monit_last_hour_classifier_item.hour = last_hour_threshold.hour
                    self.db.session.add(monit_last_hour_classifier_item)
                    update_total = False

                    last_view_item = get_view_item_for_classifier_from_list(
                        monit_global_view_items, classifier)

                    # compute total values
                    if last_view_item.total_count is None:
                        monit_last_hour_classifier_item.total_count = last_view_item.values_count
                    else:
                        monit_last_hour_classifier_item.total_count = last_view_item.total_count

                    if last_view_item.total_sum is None:
                        monit_last_hour_classifier_item.total_sum = last_view_item.values_sum
                    else:
                        monit_last_hour_classifier_item.total_sum = last_view_item.total_sum
                    monit_last_hour_view_items.append(
                        monit_last_hour_classifier_item)

                if (monit_last_hour_classifier_item.last_event_at is None) \
                        or (e.timestamp > monit_last_hour_classifier_item.last_event_at):
                    update_monitor_view_item_from_event(
                        monit_last_hour_classifier_item, e,
                        floating_average_size, update_total)

            update_total = True
            for e in monit_events_of_actual_hour:
                classifier = e.classifier
                monit_current_hour_classifier_item = get_view_item_for_classifier_from_list(
                    monit_current_hour_view_items, classifier)

                if monit_current_hour_classifier_item is None:
                    monit_current_hour_classifier_item = MonitorViewItem(
                        monit_key=monit_key, classifier=classifier)
                    monit_current_hour_classifier_item.year = current_hour_threshold.year
                    monit_current_hour_classifier_item.month = current_hour_threshold.month
                    monit_current_hour_classifier_item.day = current_hour_threshold.day
                    monit_current_hour_classifier_item.hour = current_hour_threshold.hour
                    self.db.session.add(monit_current_hour_classifier_item)

                    last_view_item = get_view_item_for_classifier_from_list(
                        monit_global_view_items, classifier)

                    # compute total values
                    if last_view_item.total_count is None:
                        monit_current_hour_classifier_item.total_count = last_view_item.values_count
                    else:
                        monit_current_hour_classifier_item.total_count = last_view_item.total_count

                    if last_view_item.total_sum is None:
                        monit_current_hour_classifier_item.total_sum = last_view_item.values_sum
                    else:
                        monit_current_hour_classifier_item.total_sum = last_view_item.total_sum

                    update_total = False
                    monit_current_hour_view_items.append(
                        monit_current_hour_classifier_item)

                if (monit_current_hour_classifier_item.last_event_at is None) \
                        or (e.timestamp > monit_current_hour_classifier_item.last_event_at):
                    update_monitor_view_item_from_event(
                        monit_current_hour_classifier_item, e,
                        floating_average_size, update_total)

        print(f"ProcessMonitJob for {monit_dict.name} done")
        pass
