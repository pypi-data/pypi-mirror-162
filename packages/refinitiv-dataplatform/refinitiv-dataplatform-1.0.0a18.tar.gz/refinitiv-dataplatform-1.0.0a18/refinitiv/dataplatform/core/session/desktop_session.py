# coding: utf-8

__all__ = ["DesktopSession"]

import logging
import socket
from typing import Optional, Iterable

import httpx
from appdirs import *

from refinitiv.dataplatform.tools._common import urljoin, make_counter, cached_property
from refinitiv.dataplatform import __version__, DesktopSessionError
from refinitiv.dataplatform import configure
from refinitiv.dataplatform.delivery.stream.omm_stream_connection import (
    OMMStreamConnection,
)
from .session import Session

#   service discovery handler
from .stream_service_discovery.stream_service_discovery_handler import (
    DesktopStreamServiceDiscoveryHandler,
)
from .stream_service_discovery.stream_connection_configuration import (
    DesktopStreamConnectionConfiguration,
)


class DesktopSession(Session):
    __inst_count = make_counter()

    class Params(Session.Params):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    @cached_property
    def name(self):
        return f"session.desktop.{DesktopSession.__inst_count()}"

    def __init__(self, app_key, on_state=None, on_event=None, **kwargs):
        super().__init__(
            app_key=app_key,
            on_state=on_state,
            on_event=on_event,
            **kwargs,
        )
        from os import getenv

        self._port = None
        self._timeout = self.http_request_timeout_secs

        #   a mapping the stream connection status
        self._streaming_connection_name_to_status = {}

        #   uuid is retrieved in CODEBOOK environment, it's used for DP-PROXY to manage multi-user mode
        self._uuid = getenv("REFINITIV_AAA_USER_ID")

        # Identify base url
        self._dp_proxy_base_url = getenv("DP_PROXY_BASE_URL")
        if self._dp_proxy_base_url:
            self._base_url = self._dp_proxy_base_url
        else:
            self._base_url = configure.get_str(
                configure.keys.desktop_base_uri(self._session_name)
            )

    def _get_base_url(self) -> str:
        return self._base_url

    def _get_udf_url(self) -> str:
        """
        Returns the scripting proxy url.
        """
        desktop_platform_paths = configure.get(
            configure.keys.desktop_platform_paths(self._session_name)
        )
        udf_path = desktop_platform_paths.get_str("udf")
        url = urljoin(self._base_url, udf_path)
        return url

    def _get_handshake_url(self) -> str:
        handshake_path = configure.get_str(
            configure.keys.desktop_handshake_url(self._session_name)
        )
        handshake_url = urljoin(self._base_url, handshake_path)
        return handshake_url

    def _get_rdp_url_root(self) -> str:
        # url = configure.get_str(configure.keys.desktop_base_uri(self._session_name))
        platform_paths = configure.get(
            configure.keys.desktop_platform_paths(self._session_name)
        )
        rdp_path = platform_paths.get_str("rdp")
        rdp_url = urljoin(self._base_url, rdp_path)
        return rdp_url

    def _get_http_session(self) -> httpx.AsyncClient:
        """
        Returns the scripting proxy http session for requests.
        """
        return self._http_session

    def set_timeout(self, timeout: float):
        """
        Set the timeout for requests.
        """
        self._timeout = timeout

    def get_timeout(self) -> float:
        """
        Returns the timeout for requests.
        """
        return self._timeout

    def set_port_number(self, port_number: str, logger=None):
        """
        Set the port number to reach Desktop API proxy.
        """
        self._port = port_number
        self._base_url = _update_port_in_url(self._base_url, port_number)

        if logger:
            logger.info(f"Set Proxy port number to {self._port}")

    def get_port_number(self) -> str:
        """
        Returns the port number
        """
        return self._port

    def is_session_logged(self, name: str = None) -> bool:
        """ note that currently the desktop session support only 1 websocket connection """
        name = name or "pricing"
        assert name in self._stream_connection_name_to_stream_connection_dict
        return self._stream_connection_name_to_stream_connection_dict[name].ready.done()

    ############################################################
    #   multi-websockets support

    def _get_stream_status(self, stream_connection_name: str):
        """this method is designed for getting a status of given stream service.

        Parameters
        ----------
            a enum of stream service
        Returns
        -------
        enum
            status of stream service.
        """
        return self._streaming_connection_name_to_status.get(stream_connection_name)

    def _set_stream_status(self, stream_connection_name: str, stream_status):
        """set status of given stream service

        Parameters
        ----------
        streaming_connection
            a service name of stream
        stream_status
            a status enum of stream
        -------
        """
        self._streaming_connection_name_to_status[
            stream_connection_name
        ] = stream_status

    async def _get_stream_connection_configuration(self, stream_connection_name: str):
        """
        This method is designed to retrieve the stream connection configuration.

        Parameters
        ----------
        stream_connection_name
            a name of stream connection in the config file i.e. "streaming/pricing/main"

        Returns
        -------
        obj
            a stream connection configuration object

        Raises
        -------
        EnvError
            if the given stream_connection_name is invalid.
        """
        #       discovery endpoint
        streaming_connection_discovery_endpoint_url = (
            self._session.get_streaming_discovery_endpoint_url(stream_connection_name)
        )

        #       protocols
        streaming_connection_supported_protocols = (
            self._session.get_streaming_protocols(stream_connection_name)
        )
        self._session.debug(
            f"          {stream_connection_name} supported protocol are {streaming_connection_supported_protocols}"
        )

        #   request the WebSocket endpoint from discovery service
        service_discovery_handler = DesktopStreamServiceDiscoveryHandler(
            self, streaming_connection_discovery_endpoint_url
        )
        stream_service_information = (
            await service_discovery_handler.get_stream_service_information(
                stream_connection_name
            )
        )

        #   build the stream connection configuration
        stream_connection_configuration = DesktopStreamConnectionConfiguration(
            self, stream_service_information, streaming_connection_supported_protocols
        )

        #   done
        return stream_connection_configuration

    async def _create_and_start_stream_connection(
        self, stream_connection_name: str, connection_protocol_name: str
    ):
        """This method is designed to construct the stream connection from given stream service
                and start the connection as a separated thread

        Parameters
        ----------
        stream_connection_name
            a unique name of the stream connection in the config file.
        i.e. "streaming/pricing/main"

        connection_protocol_name
            a name of connection protocol i.e. OMM or RDP or etc.

        Returns
        -------
        obj
            a created stream connection object

        Raises
        -------
        EnvError
            if the given connection_protocol_name is invalid.
        """

        #   call parent class function
        return await Session._create_and_start_stream_connection(
            self, stream_connection_name, connection_protocol_name
        )

    ##################################################
    #   OMM login message for each kind of session ie. desktop, platform or deployed platform

    def get_omm_login_message_key_data(self):
        """return the login message for OMM 'key' section"""
        return {
            "Elements": {
                "AppKey": self.app_key,
                "ApplicationId": self._dacs_params.dacs_application_id,
                "Position": self._dacs_params.dacs_position,
                "Authorization": f"Bearer {self._session._access_token}",
            }
        }

    def get_rdp_login_message(self, stream_id):
        """return the login message for RDP"""
        return {
            "method": "Auth",
            "streamID": f"{stream_id:d}",
            "appKey": self.app_key,
            "authorization": f"Bearer {self._access_token}",
        }

    #######################################
    #  methods to open and close session  #
    #######################################
    def open(self):
        if self._state in [Session.State.Pending, Session.State.Open]:
            # session is already opened or is opening
            return self._state

        # call Session.open() based on open_async() => _init_streaming_config will be called later
        return super(DesktopSession, self).open()

    def close(self):
        return super(DesktopSession, self).close()

    ############################################
    #  methods to open asynchronously session  #
    ############################################
    async def open_async(self):
        def close_state(msg):
            self._state = Session.State.Closed
            self._on_event(Session.EventCode.SessionAuthenticationFailed, msg)
            self._on_state(self._state, "Session is closed.")

        if self._state in [Session.State.Pending, Session.State.Open]:
            # session is already opened or is opening
            return self._state

        error = None

        try:
            if not self._dp_proxy_base_url:
                # Identify port number to update base url
                port_number = await self.identify_scripting_proxy_port()
                self.set_port_number(port_number)

            handshake_url = self._get_handshake_url()
            await self.handshake(handshake_url)
        except DesktopSessionError as e:
            self.error(e.message)
            error = e

        if not error:
            self.info(f"Application ID: {self.app_key}")
            self._state = Session.State.Open
            self._on_state(self._state, "Session is opened.")

        not self._dp_proxy_base_url and not self._port and close_state(
            "Eikon is not running"
        )
        error and close_state(error.message)
        await super(DesktopSession, self).open_async()
        return self._state

    @staticmethod
    def read_firstline_in_file(filename, logger=None):
        try:
            f = open(filename)
            first_line = f.readline()
            f.close()
            return first_line
        except IOError as e:
            if logger:
                logger.error(f"I/O error({e.errno}): {e.strerror}")
            return ""

    async def identify_scripting_proxy_port(self):
        """
        Returns the port used by the Scripting Proxy stored in a configuration file.
        """
        import platform
        import os

        port = None
        path = []
        app_names = ["Data API Proxy", "Eikon API proxy", "Eikon Scripting Proxy"]
        for app_author in ["Refinitiv", "Thomson Reuters"]:
            if platform.system() == "Linux":
                path = path + [
                    user_config_dir(app_name, app_author, roaming=True)
                    for app_name in app_names
                    if os.path.isdir(
                        user_config_dir(app_name, app_author, roaming=True)
                    )
                ]
            else:
                path = path + [
                    user_data_dir(app_name, app_author, roaming=True)
                    for app_name in app_names
                    if os.path.isdir(user_data_dir(app_name, app_author, roaming=True))
                ]

        if len(path):
            port_in_use_file = os.path.join(path[0], ".portInUse")

            # Test if ".portInUse" file exists
            if os.path.exists(port_in_use_file):
                # First test to read .portInUse file
                first_line = self.read_firstline_in_file(port_in_use_file)
                if first_line != "":
                    saved_port = first_line.strip()
                    test_proxy_url = _update_port_in_url(self._base_url, saved_port)
                    test_proxy_result = await self.check_port(test_proxy_url)
                    if test_proxy_result:
                        port = saved_port
                        self.debug(f"Port {port} was retrieved from .portInUse file")
                    else:
                        self.info(
                            f"Retrieved port {saved_port} value from .portIntUse isn't valid."
                        )

        if port is None:
            self.info(
                "Warning: file .portInUse was not found. Try to fallback to default port number."
            )
            port = await self.get_port_number_from_range(
                ("9000", "9060"), self._base_url
            )

        if port is None:
            self.error(
                "Error: no proxy address identified.\nCheck if Desktop is running."
            )
            return None

        return port

    async def get_port_number_from_range(
        self, ports: Iterable[str], url: str
    ) -> Optional[str]:
        for port_number in ports:
            self.info(f"Try defaulting to port {port_number}...")
            test_proxy_url = _update_port_in_url(url, port_number)
            test_proxy_result = await self.check_port(test_proxy_url)
            if test_proxy_result:
                self.info(f"Default proxy port {port_number} was successfully checked")
                return port_number
            self.debug(f"Default proxy port #{port_number} failed")
        return None

    async def check_port(self, url: str, timeout=None) -> bool:
        #   set default timeout
        timeout = timeout if timeout is not None else self._timeout
        url = urljoin(url, "/api/status")

        try:
            response = await self._http_request_async(
                url=url,
                method="GET",
                timeout=timeout,
            )

            self.info(
                f"Checking proxy url {url} response : {response.status_code} - {response.text}"
            )
            return True
        except (socket.timeout, httpx.ConnectTimeout):
            self.log(logging.INFO, f"Timeout on checking proxy url {url}")
        except ConnectionError as e:
            self.log(
                logging.INFO, f"Connexion Error on checking proxy url {url} : {e!r}"
            )
        except Exception as e:
            self.debug(f"Error on checking proxy url {url} : {e!r}")
        return False

    async def handshake(self, url, timeout=None):
        #   set default timeout
        timeout = timeout if timeout is not None else self._timeout

        self.info(f"Try to handshake on url {url}...")
        try:
            # DAPI for E4 - API Proxy - Handshake
            _body = {
                "AppKey": self.app_key,
                "AppScope": "trapi",
                "ApiVersion": "1",
                "LibraryName": "RDP Python Library",
                "LibraryVersion": __version__,
            }
            if self._uuid:
                # add uuid for DP-PROXY multi user mode
                _body.update({"Uuid": self._uuid})

            _headers = {"Content-Type": "application/json"}

            response = None
            try:
                response = await self._http_request_async(
                    url=url,
                    method="POST",
                    headers=_headers,
                    json=_body,
                    timeout=timeout,
                )

                self.info(f"Response : {response.status_code} - {response.text}")
            except Exception as e:
                self.log(1, f"HTTP request failed: {e!r}")

            if response:
                if response.status_code == httpx.codes.OK:
                    result = response.json()
                    self._access_token = result.get("access_token")
                elif response.status_code == httpx.codes.BAD_REQUEST:
                    self.error(
                        f"Status code {response.status_code}: "
                        f"Bad request on handshake url {url} : {response.text}"
                    )
                    key_is_incorrect_msg = (
                        f"Status code {response.status_code}: App key is incorrect"
                    )
                    self._on_event(
                        Session.EventCode.SessionAuthenticationFailed,
                        key_is_incorrect_msg,
                    )
                    raise DesktopSessionError(1, key_is_incorrect_msg)
                else:
                    self.debug(
                        f"Response {response.status_code} on handshake url {url} : {response.text}"
                    )

        except (socket.timeout, httpx.ConnectTimeout):
            raise DesktopSessionError(1, f"Timeout on handshake url {url}")
        except Exception as e:
            raise DesktopSessionError(1, f"Error on handshake url {url} : {e!r}")
        except DesktopSessionError as e:
            raise e

    ############################
    # methods for HTTP request #
    ############################
    async def http_request_async(
        self,
        url: str,
        method=None,
        headers=None,
        data=None,
        params=None,
        json=None,
        closure=None,
        auth=None,
        loop=None,
        **kwargs,
    ):
        return await self._http_request_async(
            url,
            method=method,
            headers=headers,
            data=data,
            params=params,
            json=json,
            closure=closure,
            auth=auth,
            loop=loop,
            **kwargs,
        )


def _update_port_in_url(url, port):
    try:
        protocol, path, default_port = url.split(":")
    except ValueError:
        protocol, path, *_ = url.split(":")

    if port is not None:
        retval = ":".join([protocol, path, str(port)])
    else:
        retval = url

    return retval
