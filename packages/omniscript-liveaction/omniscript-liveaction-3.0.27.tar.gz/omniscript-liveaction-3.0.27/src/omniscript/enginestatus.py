"""EngineStatus class.
"""
#Copyright (c) LiveAction, Inc. 2022. All rights reserved.
#Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
#Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

import six

from .invariant import BYTES_PER_KILOBYTE, KILOBYTES_PER_MEGABYTE, \
    KILOBYTES_PER_GIGABYTE, KILOBYTES_PER_TERABYTE

from .peektime import PeekTime


_engine_prop_dict = {
    'adapterCount' : 'adapter_count',
    'address' : 'address',
    'alarmCount' : 'alarm_count',
    'alarmsModificationTime' : 'alarm_modification_time',
    'captureInfo' : 'capture_info',
    'captures' : 'capture_count',
    'captureSessionCount' : 'capture_session_count',
    'cpuCount' : 'cpu_count',
    'cpuType' : 'cpu_type',
    'customSettings' : 'custom_settings',
    'dataDriveFormat' : 'data_drive_format',
    'dataFolder' : 'data_folder',
    'decryptionKeyCount': 'decryption_key_count',
    'diskReservedSpace' : 'disk_reserved_space',
    'enginesModificationTime' : 'modification_time',
    'engineType' : 'engine_type',
    'fileCount' : 'file_count',
    'fileVersion' : 'file_version',
    'filterCount' : 'filter_count',
    'filtersModificationTime' : 'filters_modification_time',
    'forensicSearches' : 'forensic_search_count',
    'forensicSearchReservedSpace' : 'forensic_search_reserved_space',
    'graphCount' : 'graph_count',
    'hardwareProfileCount' : 'hardware_profile_count',
    'hardwareType' : 'hardware_type',
    'hostName' : 'host',
    'ipmiAddr' : 'ipmi_address',
    'licensed' : 'is_licensed',
    'licenseExpirationDate' : 'license_expiration_date',
    'licenseExpired' : 'is_license_expired',
    'licenseType' : 'license_type',
    'logTotalCount' : 'log_total_count',
    'memoryAvailablePhysical' : 'memory_available_physical',
    'memoryTotalPhysical' : 'memory_total_physical',
    'name' : 'name',
    'nameCount' : 'name_table_count',
    'namesModificationTime' : 'names_modification_time',
    'nativeProtospecsEnabled' : 'is_native_protospecs_enabled',
    'notificationCount' : 'notification_count',
    'notificationsModificationTime' : 'notifications_modification_time',
    'operatingSystem' : 'operating_system',
    'os' : 'os',
    'platform' : 'platform',
    'productVersion' : 'product_version',
    'protocolTranslationCount' : 'protocol_translation_count',
    'protospecsVersion' : 'protospecs_version',
    'securityEventsTotalCount' : 'security_events_total_count',
    'serialNumber' : 'serial_number',
    'storageTotal' : 'storage_total',
    'storageUsed' : 'storage_used',
    'time' : 'time',
    'timeZoneBias' : 'time_zone_bias',
    'uptime' : 'uptime',
    'userDomain' : 'user_domain',
    'userId' : 'user_id',
    'userName' : 'user_name'
    }


def _parse_prop(a, v):
    result = None
    if a == 'storage_free_space':
        result = []
        for i in v.split(';'):
            k, v = i.strip(' ').split(' ', 1)
            # 69.4 GB -> 74,517,053,440 bytes
            cnt, unt, fs = v.split(' ', 2)
            cnt = float(cnt) * BYTES_PER_KILOBYTE       # 1.23 -> 1230.0
            cnt = int(cnt)                              # -> 1230 kB
            if unt == 'MB':
                cnt = cnt * KILOBYTES_PER_MEGABYTE
            elif unt == 'GB':
                cnt = cnt * KILOBYTES_PER_GIGABYTE
            elif unt == 'TB':
                cnt = cnt * KILOBYTES_PER_TERABYTE
            result.append([k, cnt, fs])
    return result


class EngineStatus(object):
    """The Status of an
    :class:`OmniEngine <omniscript.omniengine.OmniEngine>`
    object.
    """

    adapter_count = 0
    """The number of adapters on the system."""

    address = ''
    """The OmniEngine's IP Address or host name."""

    alarm_count = 0
    """The number of alarms configured on the OmniEngine."""

    alarm_modification_time = None
    """The time, as 
    :class:`PeekTime <omniscript.peektime.PeekTime>`, 
    of the last modification to the alarms."""

    capture_info = {}
    """Information about the captures."""

    capture_count = 0
    """The number of Captures created on the OmniEngine."""

    capture_session_count = 0
    """The number of Capture Session on the OmniEngine."""

    cpu_count = 0
    """The number of CPUs on the OmniEngine."""

    cpu_type = ''
    """The model of CPU on the OmniEngine."""

    custom_settings = 0
    """The number of custom settings."""

    data_drive_format = ''
    """The format of the data drive."""

    data_folder = ''
    """The default data folder of the OmniEngine."""

    decryption_key_count = 0
    """The number of decryption keys."""

    disk_reserved_space = 0
    """The amount of space, in bytes, reserved for the
    Operation System.
    """

    engine_type = ''
    """The type of OmniEngine: OmniEngine Enterprise..."""

    file_count = 0
    """The number of Packet files in the OmniEngine's database."""

    file_version = ''
    """The File Version property of the OmniEngine."""

    filter_count = 0
    """The number of Filters on the OmniEngine."""

    filters_modification_time = None
    """The last time, as a 
    :class:`PeekTime <omniscript.peektime.PeekTime>`, 
    the Filters where modified."""

    forensic_search_count = 0
    """The number of Forensic Searches on the OmniEngine."""

    forensic_search_reserved_space = 0
    """The amount of disk space, in bytes, reserved for
    Forensice Searches.
    """

    graph_count = 0
    """The number of Graphs on the OmniEngine."""

    hardware_profile_count = 0
    """The number of hardware profiles on the OmniEngine."""

    hardware_type = ''
    """The hardware type name."""

    host = ''
    """The IP Address or name of the OmniEngine's host system."""

    ipmi_address = ''
    """The IPMI IP Address."""

    is_license_expired = True
    """Has the OmniEngine's license xpired?"""

    is_licensed = False
    """Is the engine licensed?"""

    is_nativeProtospecsEnabled = False
    """Are the Native Protospecs Enabled?"""

    license_expiration_date = None
    """The date, as 
    :class:`PeekTime <omniscript.peektime.PeekTime>`, 
    the OmniEngine's license expires."""

    license_type = 0
    """The index of the OmniEngines license type."""

    log_total_count = 0
    """The total number of Log entires in the OmniEngine Event Log."""

    memory_available_physical = 0
    """The amount of physical memory in bytes available on
    the system.
    """

    memory_total_physical = 0
    """The amount of physical memory in bytes on the system."""

    modification_time = 0
    """The last time the OmniEngine was modified"""

    name = ''
    """The name of the OmniEngine."""

    name_table_count = 0
    """The number of Name Table entires (need to confirm) on the
    OmniEngine."""

    names_modification_time = None
    """The time, as 
    :class:`PeekTime <omniscript.peektime.PeekTime>`, 
    the Names Table was modified."""

    notification_count = 0
    """The number of Notifications on the OmniEngine."""

    notifications_modification_time = None
    """The last time, as 
    :class:`PeekTime <omniscript.peektime.PeekTime>`, 
    the Notifications were modified."""

    operating_system = ''
    """The full name of the Operating System that the OmniEngine is
    running on.
    """

    os = ''
    """The short name of the Operating System that the OmniEngine is
    running on: Windows or Linux.
    """

    platform = 'localhost'
    """The platform of the system, Windows only: x64, win32."""

    port = 0
    """The TCP Port of the connection to the host system."""

    product_version = ''
    """The Product Version property of the OmniEngine."""

    protocol_translation_count = 0
    """The number of Protocol Translations."""

    protospecs_version = ''
    """The OmniEngine's version as a dotted string of numbers."""

    security_events_total_count = 0
    """The total number of Events in the Security Log."""

    serial_number = ""
    """The OmniEngine's Serial Number as a string."""

    storage_available = 0
    """The amount of disk storage in bytes available on the system."""

    storage_total = 0
    """The total amount of disk storage in bytes on the system."""

    storage_used = 0
    """The amount of disk storage in bytes used on the system."""

    time = None
    """The current time, as
    :class:`PeekTime <omniscript.peektime.PeekTime>`,
    of day in UTC on the system."""

    time_zone_bias = 0
    """The time zone bias, in minutes, of the system."""

    uptime = 0
    """The number of nanoseconds the OmniEngine has been running."""

    user_domain = ''
    """The Domain of the User's account."""

    user_id = ''
    """The User's Id."""

    user_name = ''
    """The User's account name."""

    def __init__(self, engine, props=None):
        self._engine = engine
        self.logger = engine.logger

        self.adapter_count = EngineStatus.adapter_count
        self.alarm_count = EngineStatus.alarm_count
        self.capture_count = EngineStatus.capture_count
        self.capture_session_count = EngineStatus.capture_session_count
        self.cpu_count = EngineStatus.cpu_count
        self.cpu_type = EngineStatus.cpu_type
        self.data_folder = EngineStatus.data_folder
        self.decryption_key_count = EngineStatus.decryption_key_count
        self.engine_type = EngineStatus.engine_type
        self.file_count = EngineStatus.file_count
        self.file_version = EngineStatus.file_version
        self.filter_count = EngineStatus.filter_count
        self.filters_modification_time = EngineStatus.filters_modification_time
        self.forensic_search_count = EngineStatus.forensic_search_count
        self.graph_count = EngineStatus.graph_count
        self.hardware_profile_count = EngineStatus.hardware_profile_count
        self.hardware_type = EngineStatus.hardware_type
        self.host = EngineStatus.host
        self.log_total_count = EngineStatus.log_total_count
        self.memory_available_physical = EngineStatus.memory_available_physical
        self.memory_total_physical = EngineStatus.memory_total_physical
        self.name = EngineStatus.name
        self.name_table_count = EngineStatus.name_table_count
        self.notification_count = EngineStatus.notification_count
        self.operating_system = EngineStatus.operating_system
        self.os = EngineStatus.os
        self.platform = EngineStatus.platform
        self.port = EngineStatus.port
        self.product_version = EngineStatus.product_version
        self.storage_available = EngineStatus.storage_available
        self.storage_total = EngineStatus.storage_total
        self.storage_used = EngineStatus.storage_used
        self.time = EngineStatus.time
        self.time_zone_bias = EngineStatus.time_zone_bias
        self.uptime = EngineStatus.uptime
        #Set provided values
        self.host = engine.host
        self.port = engine.port
        #Parse the dictionary.
        self._load(props)

    def __str__(self):
        return f'EngineStatus: {self.name}'

    def _load(self, props):
        """Set attributes from a dictionary."""
        if isinstance(props, dict):
            for k,v in props.items():
                a = _engine_prop_dict.get(k)
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
                        setattr(self, a, PeekTime(v))
                    else:
                        setattr(self, a, v)
            self.cpu_type = ' '.join(self.cpu_type.split())
            if self.storage_total > self.storage_used:
                self.storage_available = self.storage_total - self.storage_used
            else:
                self.storage_available = 0

    def refresh(self):
        """Refresh the attributes of this object."""
        props = self._engine._issue_command("status/")
        if props:
            self.__init__(self._engine, props)
            return True
        return False
