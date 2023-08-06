"""Packet class.
"""
#Copyright (c) LiveAction, Inc. 2022. All rights reserved.
#Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
#Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import omniscript

from .omnierror import OmniError
from .peektime import PeekTime
from .readstream import ReadStream

# from .omniscript import get_id_protocol_names


class Packet(object):
    """The Packet class has packet information.
    The 
    :func:`get_packets() 
    <omniscript.capture.Capture.get_packets>`
    function returns a list of Packet objects.

    Packet number vs index: the packet number, which starts at 0, is a
    counter of the packets as they are captured. When a packet is
    captured the packet counter becomes the packet number of the packet
    and then the packet counter is incremented.
    The packet index is the index into the list of packets called the
    packet buffer.
    The first index in the packet buffer is 0. The first packet in the
    packet buffer, index 0, always contains the packet with the lowest
    packet number.
    
    A capture buffer can only hold a finite number of packets. Once
    the buffer  has filled and a new packet is captured then the
    first packet in the packet buffer (index 0) is deleted makeing what
    was the second packet (index 1) into the first packet (index 0).
    And the newly captured packet becomes the last packet in the buffer.

    The first_packet attribute of a
    :class:`Capture <omniscript.capture.Capture>`
    is the packet number of the first packet in the capture buffer.
    """

    application = None
    """The packet's application."""

    data = None
    """The packet data."""

    flags = 0
    """The packet's flags."""

    flow_id = 0
    """The id of the flow the packet belongs to.
    If there is no flow id then zero (0).
    """

    index = -1
    """The packet's index into the capture buffer."""

    number = -1
    """The packet's number starting from when the capture starts."""

    packet_length = 0
    """The total length of the packet."""

    proto_spec = 0
    """The packet's ProtoSpec."""

    status = 0
    """The packet's status."""

    timestamp = None
    """The packet's timestamp as
    :class:`PeekTime <omniscript.peektime.PeekTime>`.
    """

    def __init__(self, number, data=None):
        self.number = number if number > 0 else Packet.number
        self.application = Packet.application
        self.data = Packet.data
        self.packet_length = Packet.packet_length
        self.flags = Packet.flags
        self.flow_id = Packet.flow_id
        self.packet_length = Packet.packet_length
        self.proto_spec = Packet.proto_spec
        self.status = Packet.status
        self.timestamp = None
        self.data = Packet.data
        self._load_data(data)

    def __str__(self):
        return f'Packet: {self.index}'

    @property
    def id(self):
        """The packet's identifier. (Read Only)"""
        return self.number

    @property
    def name(self):
        """The packet's number. (Read Only)"""
        return self.number

    def _load(self, props):
        if not props:
            return
        # self.index = stream.read_uint()
        # self.number = self.index
        # self.timestamp = PeekTime(stream.read_ulong())
        # self.proto_spec = stream.read_uint()
        # self.flags = stream.read_uint()
        # self.status = stream.read_uint()
        # self.packet_length = stream.read_ushort()
        # slice_length = stream.read_ushort()
        # info_block = (stream.read_uint() != 0)
        # self.application = stream.read(8).strip('\0')
        # if version > 1:
        #     self.flow_id = stream.read_uint()
        # if info_block:
        #     # read the media info block.
        #     pass
        # if slice_length > 0:
        #     self.data = stream.read(slice_length)
        # else:
        #     self.data = stream.read(self.packet_length)

    def _load_data(self, data):
        if not data:
            return
        self.data = data
        self.packet_length = len(self.data)

    def data_length(self):
        """The number of bytes in the packet."""
        if self.data is not None:
            return len(self.data)
        return 0

    def is_sliced(self):
        """Is the packet sliced."""
        if self.data is None:
            return False
        return len(self.data) < self.packet_length

    def protocol_name(self):
        """The protocol name of the packet."""
        protocol_id_names = omniscript.get_id_protocol_names()
        if self.proto_spec & 0x0FFFF:
            return protocol_id_names[self.proto_spec & 0x0FFFF]
        return 'Unknown'


# def _create_packet_list(data, first=0):
#     try:
#         omniscript._parse_command_response(data)
#     except omniscript.OmniError as oe:
#         raise oe
#     except:
#         # Only errors are parseable.
#         # But ET.parse(data) will throw an exception
#         #   catch the exception and process the success.
#         pass

#     lst = []
#     stream = ReadStream(data)
#     stream.read_uint()      # universal_count
#     stream.read_ushort()    # magic
#     version = stream.read_ushort()
#     packet_count = stream.read_uint()
#     for _ in range(packet_count):
#         pkt = Packet(stream, first, version)
#         lst.append(pkt)
#     return lst
