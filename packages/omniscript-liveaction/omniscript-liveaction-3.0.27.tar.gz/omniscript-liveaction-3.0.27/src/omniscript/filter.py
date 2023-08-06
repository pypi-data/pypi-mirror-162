"""Filter class.
"""
#Copyright (c) LiveAction, Inc. 2022. All rights reserved.
#Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
#Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

from re import L
import json
from numpy import isin
import six
import xml.etree.ElementTree as ET

import omniscript

from .omniid import OmniId
from .peektime import PeekTime

from .invariant import ID_FLAG_NONE, ID_FLAG_NO_BRACES, TIME_FLAGS_NANOSECONDS

from .filternode import parse_console_filter, parse_omni_filter, store_omni_filter


find_attribs = ['name', 'id']
_attrib_props = ['Name', 'ID']


class Filter(object):
    """The Filter class.
    """
    
    _class_id = None
    """The Class Identifier of the object."""

    _engine = False
    """Is this an Engine Filter. Or a OmniPeek Console Filter."""
    
    color = None
    """The color of the filter."""

    comment = None
    """The filter's comment."""

    created = None
    """When the filter was created as an
    :class:`PeekTime <omniscript.peektime.PeekTime>` object.
    """

    group = None
    """The group that the filter belongs to."""

    id = None
    """The id of the filter. Filter Ids are engine specific."""

    modified = None
    """The last time the filter was modified as an
    :class:`PeekTime <omniscript.peektime.PeekTime>` object.
    """

    name = ''
    """The name of the filter."""

    criteria = None
    """The criteria of the the filter. A hierarchy of
    objectes that are sub-classed from
    :class:`FilterNode <omniscript.filternode.FilterNode>`.
    """

    #Tags
    _json_classid = 'clsid'
    _json_filters = 'filters'
    _json_classid_name = 'Filter'
    _json_id = 'id'
    _json_name = 'name'
    _json_comment = 'comment'
    _json_color = 'color'
    _json_created = 'created'
    _json_modified = 'modified'
    _json_group = 'group'
    _json_criteria = 'rootNode'

    _tag_classid = '_class_id'
    _tag_color = 'color'
    _tag_comment = 'comment'
    _tag_created = 'created'
    _tag_group = 'group'
    _tag_id = 'id'
    _tag_modified = 'modified'
    _tag_name = 'name'
    _tag_criteria = 'criteria'

    _filter_prop_dict = {
        _json_classid: _tag_classid,
        _json_color: _tag_color,
        _json_comment: _tag_comment,
        _json_created: _tag_created,
        _json_group: _tag_group,
        _json_id: _tag_id,
        _json_modified: _tag_modified,
        _json_name:  _tag_name,
        _json_criteria: _tag_criteria
    }

    def __init__(self, name=None, criteria=None):
        class_name_ids = omniscript.get_class_name_ids()
        self._class_id = class_name_ids[Filter._json_classid_name]
        self.id = OmniId(True) if criteria is None else Filter.id
        self.name = name
        self.color = Filter.color
        self.comment = Filter.comment
        self.group = Filter.group
        self.created = Filter.created
        self.modified = Filter.modified
        self.criteria = Filter.criteria
        self._load(criteria)

    def __str__(self):
        return f'Filter: {self.name}'

    def _load(self, criteria):
        """Load the Filter from a Dictionairy."""
        if isinstance(criteria, dict):
            self._load_dict(criteria)
        elif isinstance(criteria, ET.Element):
            self._load_xml(criteria)
 
    def _load_dict(self, props):
        """Load the Filter from a Dictionairy."""
        if isinstance(props, dict):
            self._engine = True # Do the props contain an Engine Filter?
            for k,v in props.items():
                a = Filter._filter_prop_dict.get(k)
                if a is not None and hasattr(self, a):
                    if a == Filter._tag_classid:
                        self._class_id = OmniId(v)
                    elif a == Filter._tag_color:
                        self.color = int(v.strip('#'), 16)
                    elif a == Filter._tag_comment:
                        self.comment = v
                    elif a == Filter._tag_created:
                        self.created = PeekTime(v)
                    elif a == Filter._tag_group:
                        self.group = v
                    elif a == Filter._tag_id:
                        self.id = OmniId(v)
                    elif a == Filter._tag_modified:
                        self.modified = PeekTime(v)
                    elif a == Filter._tag_name:
                        self.name = v
                    elif a == Filter._tag_criteria:
                        self.criteria = parse_omni_filter(v)

    def _load_xml(self, element):
        """Load the Filter from XML."""
        engine = True # Does element contain an Engine Filter?
        filter_obj = element.find('filter')
        if filter_obj is None:
            filter_obj = element.find('filterobj') #from Filter List.
        if filter_obj is not None:
            for attrib in filter_obj.items():
                if attrib[0] == 'id':
                    engine = OmniId.is_id(attrib[1])
                    self.id = OmniId(attrib[1]) if engine else OmniId(True)
                elif attrib[0] == 'color':
                    self.color = int(attrib[1])
                elif attrib[0] == 'comment':
                    self.comment = attrib[1]
                elif attrib[0] == 'created':
                    self.created = PeekTime(attrib[1])
                elif attrib[0] == 'group':
                    self.group = attrib[1]
                elif attrib[0] == 'modified':
                    self.modified = PeekTime(attrib[1])
                elif attrib[0] == 'name':
                    self.name = attrib[1]
            if self.id is None:
                self.id = OmniId(None)
            root_node = filter_obj.find('rootnode')
            if root_node is not None:
                self.criteria = (parse_omni_filter(root_node)
                    if engine else parse_console_filter(root_node))

    def _store(self):
        """Returns the Filter as a Dictionairy."""
        props = {}
        props[Filter._json_id] = self.id.format(ID_FLAG_NO_BRACES)
        props[Filter._json_name] = self.name
        if self.comment:
            props[Filter._json_comment] = self.comment
        props[Filter._json_color] = f'#{self.color:6X}' if self.color else '#000000'
        if self.created:
            props[Filter._json_created] = self.created.iso_time(TIME_FLAGS_NANOSECONDS)
        if self.modified:
            props[Filter._json_modified] = self.modified.iso_time(TIME_FLAGS_NANOSECONDS)
        if self.group:
            props[Filter._json_group] = self.group
        if self.criteria:
            store_omni_filter(props, Filter._json_criteria, self.criteria)
        props[Filter._json_classid] = self._class_id.format(ID_FLAG_NO_BRACES)
        return json.dumps(props)

    def to_string(self, pad):
        text = str(self) + '\n'
        if self.criteria:
            operation = 'or: ' if self.criteria.or_node is not None else ''
            text += self.criteria.to_string((pad+1), operation)
        return text

    # def to_xml(self, pretty=False):
    #     """Return the Filter encoded in XML as a string."""
    #     class_name_ids = omniscript.get_class_name_ids()
    #     filter_obj = ET.Element('filterobj',
    #                             {'clsid':str(class_name_ids['Filter'])})
    #     self._store(filter_obj)
    #     return ET.tostring(filter_obj).replace('\n', '')


def _create_filter_list(resp):
    lst = []
    if isinstance(resp, dict) and Filter._json_filters in resp:
        for props in resp[Filter._json_filters]:
            lst.append(Filter(criteria=props))
    lst.sort(key=lambda x: x.name)
    return lst


def find_filter(filters, value, attrib=find_attribs[0]):
    """Finds a filter in the list"""
    if (not filters) or (attrib not in find_attribs):
        return None

    if isinstance(filters[0], Filter):
        return next((i for i in filters if getattr(i, attrib) == value), None)


def read_filter_file(filename):
    """Read filters from a file. The file may be either an Engines
    filters.xml file or Peek's filters.flt file.

    Returns:
        A list of :class:`Filter <omniscript.filter.Filter>` objects.
    """
    lst = []
    xml = ET.parse(filename)
    filters = xml.getroot()
    if filters is not None:
        for obj in filters.findall('filterobj'):
            lst.append(Filter(criteria=obj))
    lst.sort(key=lambda x: x.name)
    return lst


# def store_filter_list(engine, lst):
#     class_name_ids = omniscript.get_class_name_ids()
#     filters = ET.Element('filters')
#     for fltr in lst:
#         obj = ET.SubElement(filters, 'filterobj',
#                             {'clsid':str(class_name_ids['Filter'])})
#         fltr._store(obj)
#     return filters
