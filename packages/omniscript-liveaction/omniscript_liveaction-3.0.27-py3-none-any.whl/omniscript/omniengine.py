"""OmniEngine class.
"""
#Copyright (c) LiveAction, Inc. 2022. All rights reserved.
#Copyright (c) Savvius, Inc. 2013-2019. All rights reserved.
#Copyright (c) WildPackets, Inc. 2013-2014. All rights reserved.

from curses import has_key
import imp
import os
import fileinput
import json
import re
import requests
import six
import time
import urllib3
import xml.etree.ElementTree as ET

from contextlib import closing

import omniscript

from .invariant import (BYTES_PER_MEGABYTE, BYTES_PER_GIGABYTE, ENGINE_FORMAT_JSON,
    ENGINE_FORMAT_HTML, ENGINE_FORMAT_PLAIN, ENGINE_FORMAT_TAG_STREAM, ENGINE_OP_GET,
    ENGINE_OP_POST, ENGINE_OP_PUT, ENGINE_OP_DELETE, ID_FLAG_NO_BRACES,
    OMNI_FLAG_NO_HTTPS_WARNINGS, OMNI_GET_LOG_MSGS)

from .capture import Capture
from .capturesession import CaptureSession
from .capturetemplate import CaptureTemplate
from .enginestatus import EngineStatus
from .eventlog import EventLog
from .filter import Filter
from .filternode import FilterNode
from .omnierror import OmniError
from .omniid import OmniId
from .peektime import PeekTime

from .adapter import _create_adapter_list, find_adapter, adapter_find_attributes
from .alarm import _create_alarm_list
from .analysismodule import _create_analysis_module_list
from .capture import _create_capture_list, find_capture
from .capturesession import _create_capture_session_list
from .capturetemplate import _create_capture_template_list, find_capture_template
from .fileinformation import _create_file_information_list
from .filter import _create_filter_list, find_filter

ENGINECONFIG = '/etc/omni/engineconfig.xml'
OMNI_CONF = '/etc/omni/omni.conf'
CTD_RATIO = 75

find_attributes = ['name', 'id']

_tag_results = 'results'


def _capture_id_list(captures):
    """Returns a list of OmniId."""
    capturelist = captures if isinstance(captures, list) else [captures]
    ids = []
    for c in capturelist:
        if isinstance(c, six.string_types):
            id = OmniId(c)
            if id != OmniId.null_id:
                ids.append(id)
        elif isinstance(c, OmniId):
            ids.append(c)
        elif isinstance(c, Capture):
            ids.append(c.id)
        else:
            raise TypeError("capture must be or contain a GUID.")
    return ids


def _capture_session_list(session):
    """Returns a list of session ids."""
    sessionlist = session if isinstance(session, list) else [session]
    lst = []
    for s in sessionlist:
        if isinstance(s, (int, six.string_types)):
            lst.append(int(s))
        elif isinstance(s, CaptureSession):
            lst.append(s.session_id)
        else:
            raise TypeError("session must be or contain an integer session id.")
    return lst


def _success(props):
    return isinstance(props, dict) and (_tag_results in props) and \
        isinstance(props[_tag_results], list) and \
        (len(props[_tag_results]) > 0) and (props[_tag_results][0] == 0)


def _almost_success(props):
    # Start Capture sometimes returns: {'returns': []}
    if isinstance(props, dict) and (_tag_results in props):
        return isinstance(props[_tag_results], list)
    return False


class OmniEngine(object):
    """The OmniEngine class provides access to an OmniEngie.
    The function
    :func:`create_engine() <omniscript.omniscript.OmniScript.create_engine>`
    returns an OmniEngine object.
    Then use the function
    :func:`login() <omniscript.omniscript.OmniEngine.login>`
    to enter user credentials to login to the engine.
    """

    logger = None
    """The logging object for the engine."""

    host = ''
    """The address of the host system."""

    port = 443
    """The port, https (443)."""

    timeout = 600000
    """The default timeout, in milliseconds, for issuing commands.
    The default is 10 minutes.
    """

    _omni = None
    """The parent OmniScript object of self."""

    _base_url = ""
    """The base URL for the REST API."""

    _session = None
    """The HTTP Session for the REST API."""

    _connected = False
    """Is the client connected and logged in?"""

    _filter_list = None
    """Cached Filter List: (
    :class:`Filter <omniscript.filter.Filter>`,
    :class:`PeekTime <omniscript.peektime.PeekTime>`).
    """

    _filter_timeout = 120 * 1000000000
    """The timeout, in nanoseconds, for refreshing the Filter List.
    Default 2 minutes.
    """

    def __init__(self, omni, host, port=443):
        self._omni = omni
        self.logger = omni.logger
        self.host = host if host else 'localhost'
        self.port = port if port else OmniEngine.port
        self.timeout = OmniEngine.timeout
        self._connected = False
        self._filter_list = None
        self._filter_timeout = OmniEngine._filter_timeout
        self._last_status = None

        # _base_url must end with a '/'.
        self._base_url = f'https://{self.host}:{self.port}/api/v1/'
        self._session = requests.Session()
        self._session.keep_alive = False

    def __str__(self):
        return f'OmniEngine: {self._last_status.name}' if self._last_status else 'OmniEngine'

    def _operate_url(self, operation, url, data=None):
        if operation == ENGINE_OP_GET:
            return self._session.get(url, verify=False)
        elif operation == ENGINE_OP_POST:
            return self._session.post(url, verify=False, data=data)
        elif operation == ENGINE_OP_PUT:
            return self._session.put(url, verify=False, data=data)
        elif operation == ENGINE_OP_DELETE:
            return self._session.delete(url, verify=False)
        else:
            return None

    def _retry_operate_url(self, operation, url, data=None):
        retries = 3
        resp = self._operate_url(operation, url, data)
        while (resp.status_code == 503) and (retries > 0):
            time.sleep(1)
            retries -= 1
            resp = self._operate_url(operation, url)
        return resp

    def _issue_command(self, command, operation=0, format=ENGINE_FORMAT_JSON):
        """Issue the command and return the response data.
        The OmniEngine object must have a connection to an OmniEngine. 

        Args:
            command (str): the command to issue.

        Returns:
            Success: response data or None on failure.
        """
        data = None
        if self.is_connected:
            if format == ENGINE_FORMAT_JSON:
                self._session.headers.update({'accept':'application/json'})
            elif format == ENGINE_FORMAT_PLAIN:
                self._session.headers.update({'accept':'text/plain'})
            elif format == ENGINE_FORMAT_HTML:
                self._session.headers.update({'accept':'text/html'})
            elif format == ENGINE_FORMAT_TAG_STREAM:
                self._session.headers.update(
                    {'accept':'application/octet-stream'})
            else:
                raise OmniError('Unrecognized format parameter.')

            url = self._base_url + command
            resp = self._retry_operate_url(operation, url)

            if format != ENGINE_FORMAT_JSON:
                self._session.headers.update({'accept':'application/json'})

            if resp is None:
                raise OmniError(f'REST API Command failed: Invalid operation.')                
            if resp.status_code == 200:
                if format == ENGINE_FORMAT_JSON:
                    data = json.loads(resp.text)
                elif format == ENGINE_FORMAT_TAG_STREAM:
                    data = resp.text.encode()
                else:
                    data = resp.text
            elif resp.status_code == 204:
                data = { 'results': [0] }
            elif resp.status_code == 503:
                # 503 - Service temporarily unavailable
                raise OmniError('REST API Command failed: ' \
                    f'{resp.status_code}: {resp.reason}.')
            else:
                raise OmniError(f'REST API Command failed: {resp.status_code}')
        return data

    def add_filter(self, omnifilter):
        """Add one to the engine's filter set.

        Args:
            omnifilter (str, Filter): the filter to add.
        """
        item = None
        if isinstance(omnifilter, six.string_types):
            item = Filter(criteria=omnifilter)
        elif isinstance(omnifilter, Filter):
            item = omnifilter
        else:
            raise TypeError("omnifilter must be or contain a Filter.")

        props = item._store()
        url = f'{self._base_url}filters/{item.id.format(ID_FLAG_NO_BRACES)}'
        resp = self._retry_operate_url(ENGINE_OP_PUT, url, data=props)
        if resp.status_code != 204:
            raise OmniError(f'REST API Command failed: {resp.status_code} {resp.reason}')
        return self.get_filter(item.id)

    def create_capture(self, template):
        """Create a new Capture from a
        :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
        object.
        
        Args:
            template(str or
            :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
            ): the capture template.

        Returns:
            A :class:`Capture <omniscript.capture.Capture>` 
            object of the new capture or None.
        """
        if isinstance(template, six.string_types):
            ct = template
        elif isinstance(template, CaptureTemplate):
            ct = template.store(self, True)
        url = f'{self._base_url}captures/'
        resp = self._retry_operate_url(ENGINE_OP_POST, url, data=ct)
        if resp.status_code != 200:
            return None
        props = json.loads(resp.text)
        if isinstance(props, dict):
            if 'id' in props:
                id = props['id']
                cl = self.get_capture_list()
                return find_capture(cl, id, 'id')
        return resp.text

    def delete_all_capture_sessions(self):
        """ Delete all the Capture Sessions from the engine.

        Note that 'Capture Sessions' are different from Captures.
        See the Details tab at the bottom of an OmniEngine's
        Forensics tab.
        """
        props = self._issue_command('capture-sessions/', ENGINE_OP_DELETE)
        if not _success(props):
            raise OmniError('Command failed: 0x80004005')

    def delete_all_filters(self):
        """ Delete all the Filters from the engine."""
        props = self._issue_command('filters/', ENGINE_OP_DELETE)
        if not _success(props):
            raise OmniError('Command failed: 0x80004005')

    def delete_capture(self, capture, retry=3):
        """Delete a Capture from the OmniEngine.

        Args:
            capture (str,
            :class:`OmniId <omniscript.omniid.OmniId>` or
            :class:`Capture <omniscript.capture.Capture>`
            ): the capture's id or a Capture object.
            Or a list of captures.
        """
        ids = _capture_id_list(capture)
        for id in ids:
            cmd = f'captures/{id.format(1)}'
            props = self._issue_command(cmd, ENGINE_OP_DELETE)
            if not _success(props):
                raise OmniError('Command failed: 0x80004005')

    def delete_capture_session(self, session):
        """Deletes Capture Sessions from the OmniEngine.

        Args:
            session (int, str,
            :class:`CaptureSession <omniscript.capturesession.CaptureSession>`
            ): the session's id or a CaptureSession object.
            Or a list of sessions.
        """
        ids = _capture_session_list(session)
        for id in ids:
            cmd = f'capture-sessions/{id}'
            props = self._issue_command(cmd, ENGINE_OP_DELETE)
            if not _success(props):
                raise OmniError('Command failed: 0x80004005')

    def delete_filter(self, omnifilter):
        """Delete a filter from the OmniEngine's filter set.

        Args:
            omnifilter (str,
            :class:`OmniId <omniscript.omniid.OmniId>` or
            :class:`Filter <omniscript.filter.Filter>`
            ): the id of the filter or a Filter object.
        """
        if not omnifilter:
            return
        idlist = []
        filterlist = omnifilter \
            if isinstance(omnifilter, list) else [omnifilter]
        for f in filterlist:
            if isinstance(f, Filter):
                idlist.append(f.id)
            elif isinstance(f, OmniId):
                idlist.append(f)
            elif isinstance(f, six.string_types):
                idlist.append(OmniId(f))
            elif f is not None:
                raise TypeError("omnifilter must be a Filter.")
        if idlist:
            fl = self.get_filter_list()
            for id in idlist:
                if find_filter(fl, id, 'id'):
                    cmd = f'filters/{id.format(ID_FLAG_NO_BRACES)}'
                    props = self._issue_command(cmd, ENGINE_OP_DELETE)
                    if not _success(props):
                        raise OmniError('Command failed: 0x80004005')

    def disconnect(self):
        """Disconnect from the OmniEngine"""
        return self.logout()

    def find_adapter(self, value, attrib = adapter_find_attributes[0]):
        """Find an :class:`Adapter <omniscript.adapter.Adapter>`
        in the OmniEngine's list of adapters.

        Args:
            value (str or :class:`Adapter <omniscript.adapter.Adapter>`
            ): the search key.
            attrib ('name' or 'id'): what attribute to search on.

        Returns:
            An :class:`Adapter <omniscript.adapter.Adapter>`
            object of the adapter.

        Note:
            If value is an :class:`Adapter <omniscript.adapter.Adapter>`,
            then the search is performed on the Adapter's id.
        """
        adapters = self.get_adapter_list()
        return find_adapter(adapters, value, attrib)

    def find_capture(self, value, attrib = find_attributes[0]):
        """Find an :class:`Capture <omniscript.capture.Capture>`
        in the OmniEngine's list of captures.

        Args:
            value (str or :class:`Capture <omniscript.capture.Capture>`
            ): the search key.
            attrib ('name' or 'id'): what attribute to search on.

        Returns:
            An :class:`Capture <omniscript.capture.Capture>`
            object of the capture.

        Note:
            If value is an :class:`Capture <omniscript.capture.Capture>`,
            then the search is performed on the Capture's id.
        """
        captures = self.get_capture_list()
        return find_capture(captures, value, attrib)

    def find_filter(self, value, attrib = find_attributes[0]):
        """Find a :class:`Filter <omniscript.filter.Filter>`
        in the OmniEngine's filter set.

        Args:
            value (str or :class:`Filter <omniscript.filter.Filter>`
            ): the search key.
            attrib ('name' or 'id'): what attribute to search on.

        Returns:
            A :class:`Filter <omniscript.filter.Filter>` object
            of the filter or None.
        """
        filters = self.get_filter_list()
        return omniscript.find_filter(filters, value, attrib)

    def get_adapter_list(self):
        """Get the OmniEngine's list of
        :class:`Adapter <omniscript.adapter.Adapter>`.
        
        Returns:
            A list of
            :class:`Adapter <omniscript.adapter.Adapter>`
            objects.
        """
        props = self._issue_command('adapters/')
        if props:
            return _create_adapter_list(self, props)
        return None

    def get_alarm_list(self):
        """Get the OmniEngine's list of alarms.
        
        Returns:
            A list of :class:`Alarm <omniscript.alarm.Alarm>` objects.
        """
        props = self._issue_command('alarms/')
        if props:
            return _create_alarm_list(props)
        return None

    def get_analysis_module_list(self):
        """Get the OmniEngine's list of Analysis Modules.

        Returns:
            A list of
            :class:`AnalysisModule <omniscript.analysismodule.AnalysisModule>`
            objects.
        """
        props = self._issue_command('capabilities/')
        if props and 'pluginsInfo' in props:
            return _create_analysis_module_list(self, props.get('pluginsInfo'))
        return None

    def get_capture_list(self):
        """Get the OmniEngine's list of
        :class:`Capture <omniscript.capture.Capture>`.
        
        Returns:
            A list of
            :class:`Capture <omniscript.capture.Capture>`
            objects.
        """
        props = self._issue_command('captures/')
        if props:
            return _create_capture_list(self, props)
        return None

    def get_capture_session_list(self):
        """Get the OmniEngine's list of
        :class:`CaptureSession <omniscript.capturesession.CaptureSession>`.
        
        Returns:
            A list of
            :class:`CaptureSession <omniscript.capturesession.CaptureSession>`
            objects.
        """
        props = self._issue_command('capture-sessions/')
        if props:
            return _create_capture_session_list(props)
        return None

    def get_capture_template_list(self):
        """Get the OmniEngine's list of
        :class:`CaptureTemplates <omniscript.capturetemplate.CaptureTemplate>`.
        
        Returns:
            A list of
            :class:`Capture <omniscript.capturetemplate.CaptureTemplate>`
            objects.
        """
        props = self._issue_command('capture-templates/')
        if props:
            return _create_capture_template_list(self, props)
        return None

    def get_capture_template(self, capture):
        """Get the Capture Template of an existing capture.

        Returns:
            A :class:`CaptureTemplate <omniscript.capturetemplate.CaptureTemplate>`
            object.
        """
        if isinstance(capture, Capture):
            id = capture.id
        else:
            id = OmniId(capture)
        cmd = f'captures/{id.format(ID_FLAG_NO_BRACES)}/options/'
        props = self._issue_command(cmd)
        return CaptureTemplate(props=props, engine=self) if props else None

    def get_ctd_storage(self):
        # TODO - Remove, part of initial omni script support.
        data_drives = []
        try:
            # determine data drives
            with open(ENGINECONFIG, 'r') as config:
                tree = ET.parse(config)
                node = tree.find('.//network-settings')
                drives = node.attrib.get('data-root-path').split(';')
                for drive in drives:
                    if drive and os.path.exists(drive):
                        data_drives.append(drive)
        except (ET.ParseError, EnvironmentError, AttributeError) as err:
            print(f'Could not retrieve data drives from {ENGINECONFIG}, ' \
                'using /var/lib/omni/data')

        if not data_drives:
            data_drives.append('/var/lib/omni/data')

        # determine free and used space among all data drives
        total_storage = 0
        for drive in set(data_drives):
            try:
                stat = os.statvfs(drive)
                total_storage += (stat.f_bfree * stat.f_bsize)
            except OSError as err:
                raise

        # determine reserved disk space, use value from conf file if defined
        reserved_disk_space = 10 * BYTES_PER_GIGABYTE
        try:
            with closing(fileinput.FileInput(OMNI_CONF)) as infile:
                for line in infile:
                    match = re.match(r'^\s*reserveddiskspace\s*(\d+)', line)
                    if match:
                        reserved_disk_space = \
                            int(match.group(1)) * BYTES_PER_MEGABYTE
                        break
        except EnvironmentError as err:
            print(f'Reserveddiskspace not defined in {OMNI_CONF}, ' \
                f'using default {reserved_disk_space}')

        # forensic search reserve is 3% of total space, minimum of 5G
        # and maximum of 1T
        reserved_forensic_space = (total_storage * 3) / 100
        reserved_forensic_space = max(
            reserved_forensic_space, 5 * BYTES_PER_GIGABYTE)
        reserved_forensic_space = min(
            reserved_forensic_space, 1024 * BYTES_PER_GIGABYTE)

        try:
            with closing(fileinput.FileInput(OMNI_CONF)) as infile:
                for line in infile:
                    # use value from conf file if defined
                    match = re.match( \
                        r'^\s*forensicsearchdiskspace\s*(\d+)', line)
                    if match:
                        reserved_forensic_space = \
                            int(match.group(1)) * BYTES_PER_MEGABYTE
        except EnvironmentError as err:
            print('Could not read forensicsearchdiskspace from ' \
                f'{OMNI_CONF}: {err}')

        # calculate available storage
        total_storage = 0 if (total_storage <= reserved_disk_space) else (
            total_storage - reserved_disk_space)
        total_storage = 0 if (total_storage <= reserved_forensic_space) else (
            total_storage - reserved_forensic_space)

         # determine ctd file size
        ctd_file_size = 1073741824

        keep_last_files_count = total_storage / ctd_file_size
        keep_last_files_count = (keep_last_files_count * CTD_RATIO) / 100

        return (total_storage, ctd_file_size, keep_last_files_count)
    
    def get_event_log(self, first=0, count=0, capture=None, query=None):
        """Get the OmniEngine's Event Log.

        Args:
            first (int): the index of the first entry to retrieve.
            count (int): the maximum number of entries to retrieve.
            capture (OmniId, str, Capture, CaptureSession): 
            Get entries for just this 'capture'.
            query (str): only entries whos message contains query.

        Returns:
            A :class:`EventLog <omniscript.eventlog.EventLog>` object.
        """
        if isinstance(capture, OmniId):
            _context_id = capture
        elif isinstance(capture, six.string_types):
            _context_id = OmniId(capture)
        elif isinstance(capture, Capture):
            _context_id = capture.id
        elif isinstance(capture, CaptureSession):
            _context_id = capture.capture_id
        else:
            _context_id = None

        args = [
            f'limit={count}',
            f'offset={first}',
            'informational=true',
            'major=true',
            'minor=true',
            'severe=true',
            'messages=true',
            'sourceKey=0'
        ]

        if _context_id:
            args.append(f'contextId={_context_id}')
        if query:
            args.append(f'search={query}')

        props = self._issue_command(f'events/?{"&".join(args)}')
        if props:
            return EventLog(self, props, _context_id, query)
        return None

    def get_file_list(self, path='', mask = "*", recursive=True, folders=False, from_data=True):
        """Get a list of files and their attributes.
        
        Args:
            path (str): The path of the file list to get Default is
            the Data Folder.
            mask (str): The wild-card mask. Default is '*'.
            recursive(bool) : If true then the files of sub-folders
            are included.
            folders(bool) : if true then the folders are included.
            from_data(bool) : if true then 'path' is under the engine'
            data folder.

        Returns:
            A list of
            :class:`FileInformation <omniscript.fileinformation.FileInformation>`
            objects.
        """
        props = self._issue_command('files-list/')
        return _create_file_information_list(props)
    
    def get_filter(self, omnifilter):
        """Get :class:`Filter <omniscript.filter.Filter>` from the engine.
        
        Args:
            omnifilter (str, id, Filter): id of the Filter
        Returns:
            A  :class:`Filter <omniscript.filter.Filter>` object.
        """
        if isinstance(omnifilter, Filter):
            id = omnifilter.id
        elif isinstance(omnifilter, OmniId):
            id = omnifilter
        elif isinstance(omnifilter, six.string_types):
            id = OmniId(omnifilter)
        elif omnifilter is not None:
            raise TypeError("omnifilter must be an OmniId.")
        else:
            return None

        cmd = f'filters/{id.format(ID_FLAG_NO_BRACES)}'
        props = self._issue_command(cmd)
        filter_list = _create_filter_list(props)
        return filter_list[0] if filter_list else None

    def get_filter_list(self, refresh=True):
        """Get the OmniEngine's :class:`Filter <omniscript.filter.Filter>`
        set.
        
        Args:
            refresh(bool): If True will force a refresh, else refresh
                           if the timeout has expired.
        Returns:
            A list of
            :class:`Filter <omniscript.filter.Filter>`
            objects.
        """
        do_refresh = refresh
        if not refresh and self._filter_list:
            delta_time = PeekTime() - self._filter_list[1]
            do_refresh = delta_time.value > self._filter_timeout
        if not self._filter_list or do_refresh:
            props = self._issue_command('filters/')
            filter_list = _create_filter_list(props)
            self._filter_list = (filter_list, PeekTime())
        return self._filter_list[0]

    def get_session_token(self):
        if 'authorization' in self._session.headers:
            token = self._session.headers['authorization']
            if len(token) > 11:
                return token[11:]
        return None

    def get_status(self):
        data = self._issue_command('status/')
        self._last_status = EngineStatus(self, data)
        return self._last_status

    def get_version(self):
        """Get the OmniEngine's version string.
        
        Returns:
            The OmniEngine's version as a string.
        """
        props = self._issue_command('version/')
        if isinstance(props, dict):
            if 'engineVersion' in props:
                return props['engineVersion']
        return None

    def is_connected(self):
        """Get the connection status of the OmniEngine object.
        
        Returns:
            True if OmniEngine object is connected to an OmniEngine,
            otherwise False.
        """
        return self._connected

    def login(self, user, password, session_token=None):
        """Login and connect to the OmniEngine"""
        try:
            if session_token:
                token = ("authToken: "
                    + session_token.decode('utf-8')).encode('utf-8')
                self._session.headers.update({'authorization':token})
                status_url = f'{self._base_url}status/'
                resp = self._session.get(status_url, verify=False)
                if resp.status_code == 200:
                    self._connected = True
                    return True
            url = f'{self._base_url}login/'
            cred_dict = {
                'username': user,
                'password': password,
                'client': 'OmniScript',
                'attempt': 0
                }
            credentials = json.dumps(cred_dict)
            self._session.headers.update({'accept':'application/json'})
            self._session.headers.update({'Content-Type':'application/json'})
            resp = self._session.post(url, verify=False, data=credentials)
            if (resp is None) or (resp.status_code != 200):
                self.logger.debug('Could not login. Retrying')
                retry = True
                while retry and (cred_dict['attempts'] < 6) \
                        and (resp.status_code != 200):
                    cred_dict['attempts'] += 1
                    self.logger.debug(f'Attempt No: {cred_dict["attempts"]}')
                    credentials = json.dumps(cred_dict)
                    time.sleep(5)
                    resp = self._session.post(url, verify=False, data=credentials)
                    if resp.status_code == 200:
                        self.logger.debug(f'Retry Succeeded after {cred_dict["attempts"]} attempts.')
                        retry = False
                if cred_dict['attempts'] > 5:
                    if resp.status_code == 502:
                        self.logger.debug(f'Could not connect to engine. Please Check if engine is running and then retry. Response code : {resp.status_code}')
                    else:
                        self.logger.debug(f'Could not connect to engine. Response code : {resp.status_code}')
                    return False
            resp_data = json.loads(resp.text)
            token = ("authToken: " + resp_data['authToken']).encode('utf-8')
            self._session.headers.update({"authorization":token})
            self._connected = True
        except Exception as e:
            self.logger.debug(f'Exception while loggin in. {e}')
        return self._connected

    def logout(self):
        """logout and disconnect from the OmniEngine"""
        self._connected = False
        errors = []
        if 'authorization' not in self._session.headers:
            return errors
        url = f'{self._base_url}logout/'
        token = self._session.headers['authorization'].decode('utf-8')
        data = "{\"authToken\":\"" + token + "\"}"
        try:
            resp = self._session.post(url, verify=False, data=data)
        except Exception as e:
            errors.extend(['Exception while logging out'])
            self.logger.debug('Exception while logging out')
        return errors

    def start_capture(self, capture, retry=3):
        """Signal a Capture, or list of Captures, to begin
        capturing packets.

        Args:
            capture (str,
            :class:`OmniId <omniscript.omniid.OmniId>` or
            :class:`Capture <omniscript.capture.Capture>`
            ): the capture's id or a Capture object.
            Or a list of captures.
        """
        ids = _capture_id_list(capture)
        for id in ids:
            command = f'running-captures/{id.format(1)}/'
            props = self._issue_command(command, ENGINE_OP_POST)
            if not _almost_success(props):
                raise OmniError('Command failed: 0x80004005')

    def stop_capture(self, capture, retry=3):
        """Signal a Capture, or list of Captures, to
        stop capturing packets.

        Args:
            capture (str,
            :class:`OmniId <omniscript.omniid.OmniId>` or
            :class:`Capture <omniscript.capture.Capture>`
            ): the capture's id or a Capture object.
            Or a list of captures.
        """
        ids = _capture_id_list(capture)
        for id in ids:
            command = f'running-captures/{id.format(1)}/'
            props = self._issue_command(command, ENGINE_OP_DELETE)
            if not _almost_success(props):
                raise OmniError('Command failed: 0x80004005')

    def set_filter_list_timeout(self, timeout):
        """Set the Filter List refresh timeout in seconds."""
        self._filter_timeout = int(timeout) * 1000000000    # to nanoseconds.
