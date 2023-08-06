"""OmniScript class.
"""
#Copyright (c) LiveAction, Inc. 2022. All rights reserved.
#Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
#Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

# pylint: disable-msg=w0614

VERSION = "3.0"
MIN_PYTHON = "3.8"

import logging
import os
import urllib3
import xml.etree.ElementTree as ET

from .invariant import \
    OMNI_FLAG_NO_HTTPS_WARNINGS, \
    WIRELESS_BAND_ALL, \
    WIRELESS_BAND_GENERIC, \
    WIRELESS_BAND_B, \
    WIRELESS_BAND_A, \
    WIRELESS_BAND_G, \
    WIRELESS_BAND_N, \
    WIRELESS_BAND_TURBOA, \
    WIRELESS_BAND_TURBOG, \
    WIRELESS_BAND_SUPERG, \
    WIRELESS_BAND_LICENSEDA1MHZ, \
    WIRELESS_BAND_LICENSEDA5MHZ, \
    WIRELESS_BAND_LICENSEDA10MHZ, \
    WIRELESS_BAND_LICENSEDA15MHZ, \
    WIRELESS_BAND_LICENSEDA20MHZ, \
    WIRELESS_BAND_PRIMARYAC0, \
    WIRELESS_BAND_PRIMARYAC1, \
    WIRELESS_BAND_PRIMARYAC2, \
    WIRELESS_BAND_PRIMARYAC3, \
    WIRELESS_BAND_UNKNOWN5, \
    WIRELESS_BAND_UNKNOWN6, \
    WIRELESS_BAND_UNKNOWN7, \
    WIRELESS_BAND_UNKNOWN8, \
    WIRELESS_BAND_UNKNOWN9, \
    WIRELESS_BAND_N20MHZ, \
    WIRELESS_BAND_N40MHZ, \
    WIRELESS_BAND_N40MHZLOW, \
    WIRELESS_BAND_N40MHZHIGH

from .omniengine import OmniEngine
from .omniid import OmniId
from .omniengine import find_capture, find_capture_template

# Dictionary of OmniId (GUID) to class name.
_id_class_names = None

# Dictionary of class name to OmniId (GUID).
_class_name_ids = None

# Dictionary of country codes to names.
_co_code_names = None

# Dictionary of country names to codes.
_co_name_codes = None

# Dictionary of OmniId (GUID) to expert description.
_id_expert_names = None

# Dictionary of OmniId (GUID) to statistics and other names.
# Names are not unique, so a reverse dictionary cannont be built.
_id_stat_names = None

# Dictionary of ProtoSpec Ids and protocol names and short names.
_id_protocol_names = None
_id_protocol_short_names = None

# Dictionary of short names to ProtoSpec Ids.
_protocol_short_name_ids = None

# Dictionary of OmniId (GUID) to graph names.
_id_graph_names = {}

# Dictionary of wireless band names.
_wireless_band_id_names = {
    WIRELESS_BAND_ALL: 'All',
    WIRELESS_BAND_GENERIC: 'Generic',
    WIRELESS_BAND_B: 'b',
    WIRELESS_BAND_A: 'a',
    WIRELESS_BAND_G: 'g',
    WIRELESS_BAND_N: 'n',
    WIRELESS_BAND_TURBOA: 'Turbo-a',
    WIRELESS_BAND_TURBOG: 'Turbo-g',
    WIRELESS_BAND_SUPERG: 'Super-g',
    WIRELESS_BAND_LICENSEDA1MHZ: 'Licensed a 1 MHz',
    WIRELESS_BAND_LICENSEDA5MHZ: 'Licensed a 5 MHz',
    WIRELESS_BAND_LICENSEDA10MHZ: 'Licensed a 10 MHz',
    WIRELESS_BAND_LICENSEDA15MHZ: 'Licensed a 15 MHz',
    WIRELESS_BAND_LICENSEDA20MHZ: 'Licensed a 20 MHz',
    WIRELESS_BAND_PRIMARYAC0: 'Primary ac 0',
    WIRELESS_BAND_PRIMARYAC1: 'Primary ac 1',
    WIRELESS_BAND_PRIMARYAC2: 'Primary ac 2',
    WIRELESS_BAND_PRIMARYAC3: 'Primary ac 3',
    WIRELESS_BAND_UNKNOWN5: 'Unknown 5',
    WIRELESS_BAND_UNKNOWN6: 'Unknown 6',
    WIRELESS_BAND_UNKNOWN7: 'Unknown 7',
    WIRELESS_BAND_UNKNOWN8: 'Unknown 8',
    WIRELESS_BAND_UNKNOWN9: 'Unknown 9',
    WIRELESS_BAND_N20MHZ: 'n 20 MHz',
    WIRELESS_BAND_N40MHZ: 'n 40 MHz',
    WIRELESS_BAND_N40MHZLOW: 'n 40 MHz Low',
    WIRELESS_BAND_N40MHZHIGH: 'n 40 MHz High'
}


def _add_spec(spec, id_protocol_names, id_protocol_short_names):
    spec_type = spec.get('Type')
    if spec_type is not None:
        for sub_spec in spec.iter('PSpec'):
            id = sub_spec.find('PSpecID')
            if id is not None:
                name = sub_spec.attrib['Name']
                index = int(id.text)
                id_protocol_names[index] = name
                sname = sub_spec.find('SName')
                id_protocol_short_names[index] = sname.text \
                    if sname is not None else name
    else:
        id = spec.find('PSpecID')
        if id is not None:
            name = spec.attrib['Name']
            index = int(id.text)
            id_protocol_names[index] = name
            sname = spec.find('SName')
            id_protocol_short_names[index] = sname.text \
                if sname is not None else name


def _load_class_ids():
    id_class_names = {}
    _dirname = os.path.dirname(__file__)
    with open(os.path.join(_dirname, 'data', '_class_ids.txt'), 'r') as clsdct:
        for line in clsdct:
          if len(line) > 0:
              k, v = line.split(' ', 1)
              id_class_names[OmniId(k)] = v.strip()
    return id_class_names


def _load_co_code_names():
    co_code_names = {}
    co_code_names['Unknown'] = 'Unknown'
    co_code_names['Private'] = 'Private Network'
    co_code_names['Multicast'] = 'Multicast'
    _dirname = os.path.dirname(__file__)
    with open(os.path.join(_dirname, 'data', '_co_codes.txt'), 'r') as codct:
        for line in codct:
            if len(line) > 0:
              if ':' in line:
                tup = line.split(':', 1)[0]
              else:
                tup = line
              code, name = tup.strip().split('\t', 1)
              if code not in co_code_names.keys():
                co_code_names[code] = name.strip()
    return co_code_names


def _load_expert_names():
    id_expert_names = {}
    _dirname = os.path.dirname(__file__)
    experts = ET.parse(os.path.join(_dirname, 'data', 'expertdescriptions.xml'))
    root = experts.getroot()
    _tag = root.tag
    namespace = ''
    if _tag[0] == '{':
        namespace = _tag[:_tag.find('}')+1]
    for expert in root.iter(namespace+'problem'):
        guid = expert.find(namespace+'guid')
        if guid is not None:
            name = expert.find(namespace+'name')
            if name is not None:
                id_expert_names[OmniId(guid.text.strip())] = name.text.strip()
    return id_expert_names


def _load_pspecs():
    id_protocol_names = {}
    id_protocol_short_names = {}
    _dirname = os.path.dirname(__file__)
    pspecs = ET.parse(os.path.join(_dirname, 'data', 'pspecs.xml'))
    root = pspecs.getroot()
    for pspec in root.iter('PSpec'):
        _add_spec(pspec, id_protocol_names, id_protocol_short_names)
    return id_protocol_names, id_protocol_short_names


def _load_stat_ids():
    id_stat_names = {}
    _dirname = os.path.dirname(__file__)
    with open(os.path.join(_dirname, 'data', '_stat_ids.txt'), 'r') as statdct:
        for line in statdct:
            if len(line) > 0:
                k, v = line.split(' ', 1)
                id_stat_names[OmniId(k)] = v.strip()
    return id_stat_names


def get_class_name_ids():
    """Returns a dictionary with the key being the string name of a class
    and the value the :class:`OmniId <omniscript.omniid.OmniId>` GUID of the class.
    """
    global _class_name_ids
    if _class_name_ids is None:
        id_names = get_id_class_names()
        if id_names is not None:
            _class_name_ids = dict((v,k) for k,v in id_names.items())
    return _class_name_ids


def get_country_code_names():
    """Returns a dictionary with the key being the integer country code and
    the value the string name of the country.
    """
    global _co_code_names
    if _co_code_names is None:
        _co_code_names = _load_co_code_names()
    return _co_code_names


def get_country_name_codes():
    """Returns a dictionary with the key being the string country name and
    the value the integer country code.
    """
    global _co_name_codes
    if _co_name_codes is None:
        code_names = get_country_code_names()
        if code_names is not None:
            _co_name_codes = dict((v,k) for k,v in code_names.iteritems())
    return _co_name_codes


def get_id_class_names():
    """Returns a dictionary with the key being the 
    :class:`OmniId <omniscript.omniid.OmniId>` GUID of a class
    and the value the string name of the class.
    """
    global _id_class_names
    if _id_class_names is None:
        _id_class_names = _load_class_ids()
    return _id_class_names


def get_id_expert_names():
    """Returns a dictionary with the key being the 
    :class:`OmniId <omniscript.omniid.OmniId>` GUID of a class
    and the value the string name of the expert.
    """
    global _id_expert_names
    if _id_expert_names is None:
        _id_expert_names = _load_expert_names()
    return _id_expert_names


def get_id_graph_names():
    """Returns a dictionary with the key being the
    :class:`OmniId <omniscript.omniid.OmniId>` GUID of a class
    and the value the string name of the class.
    """
    return _id_graph_names


def get_id_protocol_names():
    """Returns a dictionary with the key being the integer protospec id of
    a protocol and the value the string name of the protocol.
    """
    global _id_protocol_names
    global _id_protocol_short_names
    if _id_protocol_names is None:
        _id_protocol_names, _id_protocol_short_names = _load_pspecs()
    return _id_protocol_names


def get_id_protocol_short_names():
    """Returns a dictionary with the key being the integer protospec id of
    a protocol and the value the string short name of the protocol.
    """
    global _id_protocol_names
    global _id_protocol_short_names
    if _id_protocol_short_names is None:
        _id_protocol_names, _id_protocol_short_names = _load_pspecs()
    return _id_protocol_short_names


def get_id_stat_names():
    """Returns a dictionary with the key being the
    :class:`OmniId <omniscript.omniid.OmniId>` GUID of
    a statistic and the value the string name of the statstic.
    And the Access Control List descriptions.
    """
    global _id_stat_names
    if _id_stat_names is None:
        _id_stat_names = _load_stat_ids()
    return _id_stat_names


def get_protocol_short_name_ids():
    """Returns a dictionary with the key being the string short name of
    a protocol and the value the :class:`OmniId <omniscript.omniid.OmniId>`
    GUID of the protocol.
    """
    global _protocol_short_name_ids
    if _protocol_short_name_ids is None:
        id_names = get_id_protocol_short_names()
        _protocol_short_name_ids = dict((v,k) for k,v in id_names.items())
    return _protocol_short_name_ids


def get_wireless_band_id_names():
    """Returns a dictionary with the names of the wireless bands."""
    # global _wireless_band_id_names
    return _wireless_band_id_names


class LogFormatter(logging.Formatter):
    _all_levels = [
        logging.CRITICAL,
        logging.ERROR,
        logging.WARNING,
        logging.INFO,
        logging.DEBUG]
    levels = [logging.CRITICAL, logging.ERROR, logging.INFO, logging.DEBUG]
    width = 8

    def __str__(self):
        return 'Logging object'

    def format(self, record):
        """Return RCapture sytle logging string."""
        msg = record.msg % record.args
        return f'{record.name}: {record.levelname.ljust(self.width)} - {msg}'


class OmniScript(object):
    """The OmniScript class is used to connect to an OmniEngine."""

    def __init__(self, verbose=logging.INFO, flags=OMNI_FLAG_NO_HTTPS_WARNINGS):
        if flags & OMNI_FLAG_NO_HTTPS_WARNINGS:
            urllib3.disable_warnings()

        # Logging
        self.logger = logging.getLogger('OmniScript')
        self.logger.setLevel(verbose)
        self._console_logger = logging.StreamHandler()
        self._console_logger.setLevel(verbose)
        self._console_formatter = LogFormatter()
        self._console_logger.setFormatter(self._console_formatter)
        if len(self.logger.handlers) == 0:
            self.logger.addHandler(self._console_logger)
        self._file_logger = None
        self.set_logging_level(verbose)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __str__(self):
        return 'OmniScript'

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def connect(self, host = 'localhost', port = 80, auth = 'Default',
                domain = '', user = '', password = '', timeout = 30000):
        """Estabilish a connection to an OmniEngine.

        Args:
            host (str): the IP Address or name of the system hosting
            the OmniEngine.
            port (int): the IP Port of the OmniEngine.
            auth (str): the authorization type: Default or Third Party.
            domain (str): the domain of the user's account.
            user (str): the name of the user's account.
            password (str): the password of the user's account.
            timeout (int): the timeout in milliseconds. Default is
            30 seconds.

        Returns:
            An
            :class:`OmniEngine <omniscript.omniengine.OmniEngine>`
            object.
        """
        try:
            engine = self.create_engine(host, port)
            if engine:
                engine.login(user, password)
        except RuntimeError:
            self.logger.error('Engine is off-line or inaccessible.')
            return None
        return engine

    def create_engine(self, host='localhost', port=443):
        return OmniEngine(self, host, port)

    def critical(self, msg, *args, **kwargs):
        """Log a critical message."""
        self.logger.critical(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Log an error message."""
        self.logger.error(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Log a informational message."""
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        """Log a debugging message."""
        self.logger.debug(msg, *args, **kwargs)

    def set_log_file(self, filename, mode='a'):
        """Start logging to a file."""
        self._file_logger = logging.FileHandler(filename, mode)
        self._file_logger.setLevel(self._console_logger.level)
        # self._file_logger.setFormatter(self._file_formatter)
        self.logger.addHandler(self._file_logger)

    def set_logging_level(self, verbose):
        """Set the logging level: logging.CRITICAL to logging.DEBUG.
        """
        self.logger.setLevel(verbose)
        self._console_logger.setLevel(verbose)
        if self._file_logger:
            self._file_logger.setLevel(verbose)
