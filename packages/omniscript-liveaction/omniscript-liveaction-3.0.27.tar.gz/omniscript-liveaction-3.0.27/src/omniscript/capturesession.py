"""CaptureSession class.
"""
#Copyright (c) LiveAction, Inc. 2022. All rights reserved.
#Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
#Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import six

from .omniid import OmniId
# from omnidatatable import OmniDataTable
from .omnierror import OmniError
from .peektime import PeekTime


class CaptureSession(object):
    """Information about a Capture Session."""

    adapter_address = ''
    """The Ethernet address of the adapter."""

    adapter_name = ''
    """The name of the adapter."""

    capture_flags = 0
    """The status flags of the capture."""

    capture_id = None
    """The Id (GUID/UUID) of the Capture that created the file as a
    :class:`OmniId <omniscript.omniid.OmniId>` object.
    """

    alt_capture_id = None
    """The Id (GUID/UUID) of the Capture that created the file as a
    :class:`OmniId <omniscript.omniid.OmniId>` object.
    """

    capture_state = 0
    """The statw of the capture."""

    capture_type = 0
    """The type of the capture."""

    capture_units = 0
    """The measurment units of the capture."""

    dropped_packet_count = 0
    """The number of dropped packets."""

    link_speed = 0
    """The link speed of the adapter."""

    media_type = 0
    """The Media Type of the adapter."""

    media_sub_type = 0
    """The Media Sub Type of the adapter."""

    name = ''
    """The name of the file."""

    owner = ''
    """The owner of the session."""

    packet_count = 0
    """The number of packets in the file."""

    session_id = 0
    """The session's numeric (integer) identifier."""

    session_start_time = None
    """The timestamp of when the session was started as
    :class:`PeekTime <omniscript.peektime.PeekTime>`.
    """

    start_time = None
    """The timestamp of the first packet in the file as
    :class:`PeekTime <omniscript.peektime.PeekTime>`.
    """

    storage_units = 0
    """The number of storage units used by the session."""

    stop_time = None
    """The timestamp of the last packet in the file as
    :class:`PeekTime <omniscript.peektime.PeekTime>`.
    """

    total_byte_count = 0
    """The total number of bytes in the session."""

    total_dropped_packet_count = 0
    """The total number of packets dropped in the session."""

    total_packet_count = 0
    """The total number of packets in the session."""

    _capture_session_prop_dict = {
        'AdapterAddr': 'adapter_address',
        'AdapterName': 'adapter_name',
        'CaptureFlags': 'capture_flags',
        'CaptureID': 'alt_capture_id',
        'CaptureGUID': 'capture_id',
        'CaptureState': 'capture_state',
        'CaptureType': 'capture_type',
        'CaptureUnits': 'capture_units',
        'DroppedCount': 'dropped_packet_count',
        'LinkSpeed': 'link_speed',
        'MediaType': 'media_type',
        'MediaSubType': 'media_sub_type',
        'Name': 'name',
        'Owner': 'owner',
        'PacketCount': 'packet_count',
        'SessionID': 'session_id',
        'SessionStartTimestamp': 'session_start_time',
        'StartTimestamp': 'start_time',
        'StorageUnits': 'storage_units',
        'StopTimestamp': 'stop_time',
        'TotalByteCount': 'total_byte_count',
        'TotalDroppedCount': 'total_dropped_packet_count',
        'TotalPacketCount': 'total_packet_count'
        }

    def __init__(self, props):
        self.adapter_address = CaptureSession.adapter_address
        self.adapter_name = CaptureSession.adapter_name
        self.capture_flags = CaptureSession.capture_flags
        self.capture_id = CaptureSession.capture_id
        self.capture_state = CaptureSession.capture_state
        self.capture_type = CaptureSession.capture_type
        self.capture_units = CaptureSession.capture_units
        self.dropped_packet_count = CaptureSession.dropped_packet_count
        self.link_speed = CaptureSession.link_speed
        self.media_type = CaptureSession.media_type
        self.media_sub_type = CaptureSession.media_sub_type
        self.name = CaptureSession.name
        self.owner = CaptureSession.owner
        self.packet_count = CaptureSession.packet_count
        self.session_id = CaptureSession.session_id
        self.session_start_time = CaptureSession.session_start_time
        self.start_time = CaptureSession.start_time
        self.storage_units = CaptureSession.storage_units
        self.stop_time = CaptureSession.stop_time
        self.total_byte_count = CaptureSession.total_byte_count
        self.total_dropped_packet_count = \
            CaptureSession.total_dropped_packet_count
        self.total_packet_count = CaptureSession.total_packet_count
        self._load(props)

    def __str__(self):
        return f'CaptureSession: {self.name}' if self.name else 'CaptureSession'

    def _load(self, props):
        """Load the CaptureSession information from the row of an
        :class:`OmniDataTable <omniscript.omnidatatabel.OmniDataTable>`.
        """
        if isinstance(props, dict):
            for k,v in props.items():
                a = CaptureSession._capture_session_prop_dict.get(k)
                if a is not None and hasattr(self, a):
                    if isinstance(getattr(self, a), six.string_types):
                        setattr(self, a, v if v else '')
                    elif isinstance(getattr(self, a), int):
                        setattr(self, a, int(v) if v else 0)
                    elif getattr(self, a) is None:
                        if a == 'capture_id' or a == 'alt_capture_id':
                            setattr(self, a, OmniId(v))
                        elif (a == 'session_start_time'
                              or a == 'start_time'
                              or a == 'stop_time'):
                            setattr(self, a, PeekTime(v))


def _create_capture_session_list(props):
    """Create a List of CaptureSession objects from a Dictionary."""
    lst = None
    if isinstance(props, dict):
        rows = props.get('rows')
        if isinstance(rows, list):
            lst = []
            for r in rows:
                cs = CaptureSession(r)
                lst.append(cs)
        lst.sort(key=lambda x: x.name)
    return lst
