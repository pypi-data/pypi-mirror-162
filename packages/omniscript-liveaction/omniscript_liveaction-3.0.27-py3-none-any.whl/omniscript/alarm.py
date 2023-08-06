"""Alarm class.
"""
#Copyright (c) LiveAction, Inc. 2022. All rights reserved.
#Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
#Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import six

import omniscript

from .omniid import OmniId
from .peektime import PeekTime

from .invariant import ALARM_TRACK_TYPE_UNDEFINED


find_attribs = ['name', 'id']

class AlarmCondition(object):
    """A condition of an Alarm."""

    comparison_type = 0
    duration = 0
    enabled = False
    severity = 0
    type = 0
    value = 0.0

    # Tags
    _json_comparison_type = 'comparison_type'
    _json_duration = 'duration'
    _json_enabled = 'enabled'
    _json_severity = 'severity'
    _json_type = 'type'
    _json_value = 'value'

    _tag_comparison_type = 'comparison_type'
    _tag_duration = 'duration'
    _tag_enabled = 'enabled'
    _tag_severity = 'severity'
    _tag_type = 'type'
    _tag_value = 'value'

    def __init__(self, props):
        self.comparison_type =  AlarmCondition.comparison_type
        self.duration =  AlarmCondition.duration
        self.enabled =  AlarmCondition.enabled
        self.severity =  AlarmCondition.severity
        self.type =  AlarmCondition.type
        self.value =  AlarmCondition.value
        self._load(props)

    def _load(self, props):
        if isinstance(props, dict):
            for k,v in props.items():
                if k == AlarmCondition._json_comparison_type:
                    self.comparison_type = v
                elif k == AlarmCondition._json_duration:
                    self.duration = int(v)
                elif k == AlarmCondition._json_enabled:
                    self.enabled = v
                elif k == AlarmCondition._json_type:
                    self.type = int(v)
                elif k == AlarmCondition._json_severity:
                    self.severity = int(v)
                elif k == AlarmCondition._json_value:
                    self.value = float(v)


class TrackingSummary(object):
    flags = 0
    id = None
    type = 0

    _json_flags = 'flags'
    _json_id = 'id'
    _json_type = 'summaryStatisticsType'

    _tag_flags = 'flags'
    _tag_id = 'id'
    _tag_type = 'type'

    def __init__(self, props):
        flags = TrackingSummary.flags
        id = TrackingSummary.id
        type = TrackingSummary.type
        self._load(props)

    def _load(self, props):
        if isinstance(props, dict):
            for k,v in props.items():
                if k == TrackingSummary._json_flags:
                    self.flags = int(v)
                elif k == TrackingSummary._json_id:
                    self.id = OmniId(v)
                elif k == TrackingSummary._json_type:
                    self.type = int(v)


class StatisticsTracker(object):
    classid = None
    type = 0
    history = 0
    summary = None

    _json_classid = 'clsid'
    _json_type = 'statisticsType'
    _json_history = 'history'
    _json_summary = 'summary'

    _tab_classid = 'classid'
    _tab_type = 'type'
    _tab_history = 'history'
    _tab_summary = 'summary'

    def __init__(self, props):
        self.classid = None
        self.type = 0
        self.history = 0
        self.summary = None
        self._load(props)

    def _load(self, props):
        if isinstance(props, dict):
            for k,v in props.items():
                if k == StatisticsTracker._json_classid:
                    self.classid = OmniId(v)
                elif k == StatisticsTracker._json_type:
                    self.type = int(v)
                elif k == StatisticsTracker._json_history:
                    self.history = int(v)
                elif k == StatisticsTracker._json_summary:
                    self.summary = TrackingSummary(v)


class Alarm(object):
    """The Alarm class has the attributes of an alarm.
    The 
    :func:`get_alarm_list() 
    <omniscript.omniengine.OmniEngine.get_alarm_list>`
    function returns a list of Alarm objects.
    """

    conditions = []
    """The conitions of the alarm."""

    created = None
    """The time and date the alarm was created as
    :class:`PeekTime <omniscript.peektime.PeekTime>`.
    """

    id = OmniId()
    """The alarms's identifier."""

    modified = None
    """The time and date of the last modification as
    :class:`PeekTime <omniscript.peektime.PeekTime>`.
    """

    name = ''
    """The name of the alarm."""

    track_type = ALARM_TRACK_TYPE_UNDEFINED
    """The Track Type of the alarm."""

    tracker = None
    """The Statistics Tracker for the Alarm."""

    _class_id = None

    _json_classid = 'clsid'
    _json_alarms = 'alarms'
    _json_classid_name = 'Alarm'
    _json_conditions = 'conditions'
    _json_created = 'created'
    _json_id = 'id'
    _json_modified = 'modified'
    _json_name = 'name'
    _json_track_type = 'trackType'
    _json_tracker = 'statisticsTracker'

    _tag_classid = '_class_id'
    _tag_conditions = 'conditions'
    _tag_created = 'created'
    _tag_id = 'id'
    _tag_modified = 'modified'
    _tag_name = 'name'
    _tag_track_type = 'track_type'
    _tag_tracker = 'tracker'

    _alarm_node_prop_dict = {
        _json_classid: _tag_classid,
        _json_conditions: _tag_conditions,
        _json_created: _tag_created,
        _json_id: _tag_id,
        _json_modified: _tag_modified,
        _json_name: _tag_name,
        _json_track_type: _tag_track_type,
        _json_tracker: _tag_tracker
    }

    def __init__(self, criteria):
        self.id = OmniId(True) if criteria is None else Alarm.id
        self.name = Alarm.name
        self.created = PeekTime() if criteria is None else Alarm.created
        self.modified = PeekTime() if criteria is None else Alarm.modified
        self.track_type = Alarm.track_type
        self._load(criteria)

    def __str__(self):
        return f'Alarm: {self.name}'

    def _load(self, props):
        if not isinstance(props, dict):
            return
        for k,v in props.items():
            a = Alarm._alarm_node_prop_dict.get(k)
            if a == Alarm._tag_classid:
                self._class_id = OmniId(v)
            elif a == Alarm._tag_id:
                self.id = OmniId(v)
            elif a == Alarm._tag_conditions:
                self.conditions = _make_condition_list(v)
            elif a == Alarm._tag_created:
                self.created = PeekTime(v)
            elif a == Alarm._tag_modified:
                self.modified = PeekTime(v)
            elif a == Alarm._tag_name:
                self.name = v
            elif a == Alarm._tag_track_type:
                self.track_type = int(v)
            elif a == Alarm._tag_tracker:
                self.tracker = StatisticsTracker(v)
        if not self.id:
            self.id = OmniId(None)


def _make_condition_list(props):
    result = []
    if isinstance(props, list):
        for condition in props:
            result.append(AlarmCondition(condition))
    return result


def _create_alarm_list(resp):
    lst = []
    alarms = resp['alarms']
    if alarms is not None:
        for props in alarms:
            lst.append(Alarm(props))
    lst.sort(key=lambda x: x.name)
    return lst


def find_alarm(alarms, value, attrib=find_attribs[0]):
    """Finds an alarm in the list"""
    if (not alarms) or (attrib not in find_attribs):
        return None

    if len(alarms) == 0:
        return None

    if isinstance(value, Alarm):
        _value = value.id
        attrib = 'id'
    else:
        _value = value

    return next((i for i in alarms if getattr(i, attrib) == _value), None)
