"""Adapter class.
"""
#Copyright (c) LiveAction, Inc. 2022. All rights reserved.
#Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
#Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import six

# import omniscript
# import config

from .omniaddress import format_ethernet
from .omniid import OmniId

adapter_types = ['Network Interface Card', 'File Adapter', 'Plugin Adapter']

adapter_find_attributes = ['name', 'id', 'device_name']

_adapt_prop_dict = {
    'AdapterFeatures' : 'features',
    'AdapterType' : 'type',
    'address' : 'address',
    'channels' : 'channels',
    'clsid' : 'class_id',
    'defaultLinkSpeed' : 'default_link_speed',
    'description' : 'description',
    'DeviceName' : 'device_name',
    'flags' : 'flags',
    'identifier' : 'id',
    'ids' : 'ids',
    'InterfaceFeatures' : 'interface_features',
    'linkSpeed' : 'link_speed',
    'mediaSubType' : 'media_sub_type',
    'mediaType' : 'media_type',
    'ringBufferSize' : 'ring_buffer_size',
    'type' : 'type',
    'WildPacketsAPI' : 'wildpackets_api'
}


class Adapter(object):
    """The Adapter class has the attributes of an adapter.
    The 
    :func:`get_adapter_list() 
    <omniscript.omniengine.OmniEngine.get_adapter_list>`
    function returns a list of Adapter objects.
    """

    id = ''
    """The adapter's identifier, on Windows is a four digit code that
    is engine specific.
    """

    features = 0
    """Features of the adapter. Bit fields."""

    adapter_type = 0
    """The type of adapter. Any of the ADDRESS TYPE constants."""

    address = '00:00:00:00:00:00'
    """The Ethernet Address of the adapter."""

    class_id = None
    """The adapters Class Id as a GUID."""

    default_link_speed = 0
    """The adapter's default link speed in bits per second."""

    description = ''
    """The decscription/name of the adapter."""

    device_name = ''
    """The device name of the adapter: Broadcom, Intel..."""

    interface_features = 0
    """Interface Features of the adapter. Bit fields."""

    link_speed = 0
    """The link speed of the adapter in bits per second."""

    media_type = 0
    """The Media Type of the adapter."""

    media_sub_type = 0
    """The Media Sub Type of the adapter."""

    ring_buffer_size = 0
    """The size of the ring buffer in bytes."""

    type = 0
    """The type of adapter."""

    wildpackets_api = False
    """Does the adapter support the WildPackets' API."""

    def __init__(self, engine, props):
        self._engine = engine
        self.logger = engine.logger
        self._load(props)
        if self.description is None:
            self.description = ''

    def __repr__(self):
        return f'Adapter: {self.description}'

    def __str__(self):
        return f'Adapter: {self.description}'

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            if len(props) == 2:
                config = props['configuration']
                info = props['info']
            else:
                config = props
                info = None
            # Set attributes from the configuration (config) dictionary.
            if isinstance(config, dict):
                for k,v in config.items():
                    a = _adapt_prop_dict.get(k)
                    if a is not None and hasattr(self, a):
                        if isinstance(getattr(self, a), six.string_types):
                            setattr(self, a, v if v else '')
                        elif isinstance(getattr(self, a), int):
                            setattr(self, a, int(v) if v else 0)
                        elif isinstance(getattr(self, a), list):
                            setattr(self, a, v)
                        elif isinstance(getattr(self, a), dict):
                            setattr(self, a, v)
                        elif getattr(self, a) is None:
                            setattr(self, a, OmniId(v))
                        else:
                            setattr(self, a, v)
            # Set attributes from the information (info) dictionary.
            if isinstance(info, dict):
                for k,v in info.items():
                    a = _adapt_prop_dict.get(k)
                    if a is not None and hasattr(self, a):
                        if isinstance(getattr(self, a), six.string_types):
                            setattr(self, a, v if v else '')
                        elif isinstance(getattr(self, a), int):
                            setattr(self, a, int(v) if v else 0)
                        elif isinstance(getattr(self, a), list):
                            setattr(self, a, v)
                        elif isinstance(getattr(self, a), dict):
                            setattr(self, a, v)
                        elif getattr(self, a) is None:
                            setattr(self, a, OmniId(v))
                        else:
                            setattr(self, a, v)

    @property
    def name(self):
        """The name/description of the adapter. (Read Only)"""
        return self.description

    def rename(self, new_name):
        self._engine.rename_adapter(self.adapter_type, self.id, new_name)


def _create_adapter_list(engine, resp):
    lst = []
    adapters = resp['adapters']
    if adapters is not None:
        for props in adapters:
            lst.append(Adapter(engine, props))
    lst.sort(key=lambda x: x.description)
    return lst


def find_adapter(adapters, value, attrib=adapter_find_attributes[0]):
    """Finds an adapter in the list."""
    if (not adapters) or (attrib not in adapter_find_attributes):
        return None

    if len(adapters) == 0:
        return None

    if isinstance(value, Adapter):
        _value = value.id
        attrib = 'id'
    else:
        _value = value

    return next((i for i in adapters if getattr(i, attrib) == _value), None)
