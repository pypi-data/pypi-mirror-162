"""FileInformation class.
"""
#Copyright (c) LiveAction, Inc. 2022. All rights reserved.
#Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
#Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import xml.etree.ElementTree as ET

import omniscript

from .invariant import FILE_FLAGS_FOLDER
from .peektime import PeekTime


class FileInformation(object):
    """Information about a file.
    """

    flags = 0
    """The attribute flags of the file may be checked against the
    FILE FLAGS constants.
    """

    modified = None
    """The date and time, as
    :class:`PeekTime <omniscript.peektime.PeekTime>`,
    that the file was last modified."""

    name = ''
    """The fully qualified name of the file."""

    size = 0
    """The size of the file in bytes."""

    #XML Tags
    _json_partial_path = 'PartialPath'
    _json_file_name = 'FileName'
    _json_status = 'Status'
    _json_size = 'FileSize'
    _json_time_zone_bias = 'TimeZoneBias'
    _json_media_type = 'MediaType'
    _json_media_subtype = 'MediaSubType'
    _json_link_speed = 'LinkSpeed'
    _json_count = 'PacketCount'
    _json_session_start_time = 'SessionStartTime'
    _json_session_end_time = 'SessionEndTime'
    _json_capture_name = 'CaptureName'
    _json_capture_id = 'CaptureID'
    _json_file_index = 'FileIndex'
    _json_adapter_name = 'AdapterName'
    _json_adapter_address = 'AdapterAddr'
    _json_owner = 'Owner'

    _tag_root_name = "file"
    _tag_flags = "attr"
    _tag_modified = "mod"
    _tag_name = "name"
    _tag_size = "size"

    def __init__(self, name='', flags=0, props=None):
        self.flags = flags
        self.modified = FileInformation.modified
        self.name = name
        self.size = FileInformation.size
        self._load(props)

    def _load(self, props):
        """Load the File Informaiont from a dictionary."""
        if isinstance(props, dict):
            self.modified = props.get(FileInformation._json_session_end_time)
            self.name = props.get(FileInformation._json_file_name)
            v = props.get(FileInformation._json_size)
            self.size = int(v) if v else 0

    def __str__(self):
        return f'FileInformation: {self.name}'

    def is_folder(self):
        """Returns True if the information is for a folder."""
        return (self.flags & FILE_FLAGS_FOLDER) != 0


def _create_file_information_list(props):
    lst = []
    if isinstance(props, dict):
        rows = props['rows']
        if isinstance(rows, list):
            for row in rows:
                lst.append(FileInformation(props=row))
    return lst


def file_information_list_to_file_list(fil):
    """Transform a list of
    :class:`FileInformation <omniscript.fileinformation.FileInformation>`
    into a list of strings of fully qualified file names.
    """
    fl = []
    path = ''
    for f in fil:
        if f.is_folder():
            path = f.name
        else:
            fl.append(path + f.name)
    return fl
