import abc
import logging
import sys

from refinitiv.dataplatform import configure
from refinitiv.dataplatform.errors import PlatformSessionError
from .authentication_token_handler_thread import AuthenticationTokenHandlerThread
from .session import Session
from .stream_service_discovery.stream_connection_configuration import (
    RealtimeDistributionSystemConnectionConfiguration,
)
from .stream_service_discovery.stream_service_discovery_handler import (
    StreamServiceInformation,
    PlatformStreamServiceDiscoveryHandler,
)
from ...tools._common import parse_url, get_scheme_port


class PlatformConnection(abc.ABC):
    def __init__(self, session):
        self._session = session

        self.log = session.log
        self.debug = session.debug

        #   a mapping the stream connection status
        #       the key is the tuple of connection name and connection type (OMM, RDP, etc.)
        self.streaming_connection_name_and_connection_type_to_status = {}

    @abc.abstractmethod
    def get_omm_login_message_key_data(self):
        pass

    @abc.abstractmethod
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
        pass

    @abc.abstractmethod
    async def get_stream_connection_configuration(self, stream_connection_name: str):
        """this function extract the realtime distribution system information from config file.
                note that the connection_name is a name of the session. default session name is "default-session"

        Parameters
        ----------
        stream_connection_name
            a unique name of the stream connection in the config file.
        i.e. "streaming/pricing/main"

        Returns
        -------
        obj
            the stream connection configuration of the given session and stream connection name
        """
        pass

    @abc.abstractmethod
    async def waiting_for_stream_ready(self, open_state):
        pass

    @abc.abstractmethod
    def open(self):
        pass

    @abc.abstractmethod
    def authorize(self, first_time_authorize=True):
        pass

    @abc.abstractmethod
    def close(self):
        pass

    def get_stream_status(self, streaming_connection_name):
        return self.streaming_connection_name_and_connection_type_to_status.get(
            streaming_connection_name, Session.EventCode.StreamDisconnected
        )

    def set_stream_status(self, streaming_connection_name, stream_status):
        self.streaming_connection_name_and_connection_type_to_status[
            streaming_connection_name
        ] = stream_status


class RefinitivDataConnection(PlatformConnection):
    def __init__(self, session):
        super().__init__(session)

        #   authentication token handler
        self._authentication_token_handler_thread = None

    def get_omm_login_message_key_data(self):
        return {
            "NameType": "AuthnToken",
            "Elements": {
                "AuthenticationToken": self._session._access_token,
                "ApplicationId": self._session._dacs_params.dacs_application_id,
                "Position": self._session._dacs_params.dacs_position,
            },
        }

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
        return await self._session._http_request_async(
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

    async def get_stream_connection_configuration(self, stream_connection_name: str):
        """this function extract the realtime distribution system information from config file.
                note that the connection_name is a name of the session. default session name is "default-session"

        Parameters
        ----------
        stream_connection_name
            a unique name of the stream connection in the config file.
        i.e. "streaming/pricing/main"

        Returns
        -------
        obj
            the stream connection configuration of the given session and stream connection name
        """

        #   two ways of specific stream connection are discovery endpoint and WebSocket URL

        #       WebSocket url
        streaming_connection_endpoint_websocket_url = (
            self._session.get_streaming_websocket_endpoint_url(stream_connection_name)
        )
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

        #   check for valid path for stream discovery endpoint
        if streaming_connection_endpoint_websocket_url is not None:
            #   override discovery endpoint by specific WebSocket endpoint url
            self._session.debug(
                f"override streaming by WebSocket endpoint url : {streaming_connection_endpoint_websocket_url}"
            )

            #   build the stream service information and stream connection configuration

            #       parse the WebSocket url and build stream service information
            result = parse_url(
                streaming_connection_endpoint_websocket_url
            )
            path = result.path
            host = result.hostname

            if not result.hostname and result.path:
                path = ""
                host = result.path

            scheme = result.scheme
            port = result.port

            scheme, port = get_scheme_port(scheme, port)

            stream_service_information = StreamServiceInformation(
                scheme=scheme,
                host=host or "",
                port=port,
                path=path or "",
                data_formats=["unknown"],
                location=None,
            )

            #   build the stream connection configuration
            return RealtimeDistributionSystemConnectionConfiguration(
                self._session,
                [
                    stream_service_information,
                ],
                streaming_connection_supported_protocols,
            )

        elif streaming_connection_discovery_endpoint_url is not None:
            #   valid stream discovery endpoint url
            self._session.debug(
                f"using discovery endpoint url : {streaming_connection_discovery_endpoint_url}"
            )

            #   request the WebSocket endpoint from discovery service
            service_discovery_handler = PlatformStreamServiceDiscoveryHandler(
                self._session, streaming_connection_discovery_endpoint_url
            )
            stream_service_information = (
                await service_discovery_handler.get_stream_service_information(
                    stream_connection_name
                )
            )

            #   build the stream connection configuration
            return RealtimeDistributionSystemConnectionConfiguration(
                self._session,
                stream_service_information,
                streaming_connection_supported_protocols,
            )

        else:
            #   error
            raise ValueError(
                "ERROR!!! streaming connection needed by specific url and path in endpoint section or specific WebSocket url."
            )

    async def waiting_for_stream_ready(self, open_state):
        pass

    def _initialize_authentication_handler_thread(self):
        self._authentication_token_handler_thread = AuthenticationTokenHandlerThread(
            self._session,
            self._session._grant,
            self._session.authentication_token_endpoint_url,
            server_mode=self._session.server_mode,
            take_exclusive_sign_on_control=self._session._take_signon_control,
        )

    def open(self):
        #   build the token handler for this platform session
        self._initialize_authentication_handler_thread()

        #   call authorize for do an authentication mechanism to the RDP platform by another thread
        self.authorize(first_time_authorize=True)

    def authorize(self, first_time_authorize=False):
        """do an authentication by calling a method in AuthenticationTokenHandlerThread."""

        #   do authentication until successful when the server mode is enable
        while True:

            #   request a authentication token and wait for it
            is_authorize_failed = False
            try:
                self._authentication_token_handler_thread.authorize()
            except:
                #   error occur when request an authorization

                #   check the sever-mode is enabled or not?
                if not self._session.server_mode:
                    #   do nothing because the server-mode is disabled
                    self._session.error(
                        f"ERROR!!! failed to request an authorization to platform.\n"
                        f"Unexpected error {sys.exc_info()[0]}.\n"
                        "(server-mode is disbled)"
                    )

                    raise PlatformSessionError(
                        -1,
                        "ERROR!!! Authentication handler failed to request a access token.\n"
                        f"{sys.exc_info()[0]}.",
                    )

                else:
                    #   retry again
                    self._session.warning(
                        "WARNING!!! retrying after failed to request an authorization to platorm.\n"
                        f"Unexpected error {sys.exc_info()[0]}.\n"
                        "(server-mode is enabled)"
                    )
                    is_authorize_failed = True

            self._session.debug(
                f"               waiting for authorize is ready.........."
            )
            self._authentication_token_handler_thread.wait_for_authorize_ready()

            #   check the request a new authentication success or not?
            if (
                is_authorize_failed
                or self._authentication_token_handler_thread.is_error()
            ):
                #   failed to request with 401 error code on the first time.
                #       this means we might suppile the wrong username or password.
                if (
                    first_time_authorize
                    and self._session._last_event_code
                    == Session.EventCode.SessionAuthenticationFailed
                ):
                    #   failed to request an authorized in the thread loop
                    raise PlatformSessionError(-1, self._session._last_event_message)
                if not self._session.server_mode:
                    #   do nothing because the server-mode is disabled
                    self._session.error(
                        "ERROR!!! CANNOT authorize to RDP authentication endpoint.\n"
                        f"Unexpected error {self._authentication_token_handler_thread.last_exception}.\n"
                        "(server-mode is disbled)"
                    )

                    #   raise the error
                    raise PlatformSessionError(
                        -1,
                        "ERROR!!! Authentication handler failed to request a access token.\n"
                        f"{self._authentication_token_handler_thread.last_exception}",
                    )

                else:
                    self._session.warning(
                        "WARNING!!! retring after authentication token thread failed.\n"
                        f"Unexpected error {self._authentication_token_handler_thread.last_exception}."
                    )

                    #   stop and close the current authentication handler thread
                    try:
                        self._authentication_token_handler_thread.stop()
                    except:
                        #   possible the authentication token handler thread cannot stop properly
                        self._session.warning(
                            "WARNING!!! CANNOT properly stop authentication token handler thread .\n"
                            f"Unexpected error {sys.exc_info()[0]}."
                        )

                    #   re-initialize the authentication handler
                    self._initialize_authentication_handler_thread()

            else:
                #   successfully request an authorization
                self._session.debug(
                    "Successfully request an authorization by authentication token handler thread."
                )
                break

    def close(self):
        self.log(logging.DEBUG, "Close platform session...")
        #   stop the authentication thread
        self._authentication_token_handler_thread.stop()
        return super().close()


class DeployedConnection(PlatformConnection):
    """this class is designed for a connection to the realtime distribution system (aka. deployed platform or TREP)"""

    def __init__(self, session):
        super().__init__(session)
        self.streaming_connection_name_and_connection_type_to_status[
            self._session._deployed_platform_connection_name
        ] = Session.EventCode.StreamDisconnected

    def get_omm_login_message_key_data(self):
        return {
            "Name": self._session._dacs_params.deployed_platform_username,
            "Elements": {
                "ApplicationId": self._session._dacs_params.dacs_application_id,
                "Position": self._session._dacs_params.dacs_position,
            },
        }

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
        raise PlatformSessionError(
            -1,
            "Error!!! Platform session cannot connect to refinitiv dataplatform. "
            "Please check or provide the access right.",
        )

    async def get_stream_connection_configuration(self, stream_connection_name: str):
        """this function extract the realtime distribution system information from config file.
                note that the connection_name is a name of the session. default session name is "default-session"

        Parameters
        ----------
        stream_connection_name
            a unique name of the stream connection in the config file.
        i.e. "streaming/pricing/main"

        Returns
        -------
        obj
            the stream connection configuration of the given session and stream connection name
        """
        assert stream_connection_name.startswith("streaming/pricing")

        #   get the realtime distribution system information from config file
        if self._session._deployed_platform_host is None:
            #   read from config file.
            realtime_distribution_system_url_key = f"{configure.keys.platform_realtime_distribution_system(self._session._session_name)}.url"
            realtime_distribution_system_url = configure.get_str(
                realtime_distribution_system_url_key
            )
            self._session.debug(
                f"using the Refinitiv realtime url at {realtime_distribution_system_url}"
            )

            #   construct host for host name and port
            result = parse_url(
                realtime_distribution_system_url
            )
            scheme = result.scheme

            if "." in scheme:
                host = scheme
                port = result.path
                try:
                    port = int(port)
                except ValueError:
                    port = ""

                scheme = ""

            else:
                host = result.hostname or result.netloc or result.path
                port = result.port

            scheme, port = get_scheme_port(scheme, port)

            self._session.debug(
                f"      realtime_distribution_system scheme   = {scheme}"
            )
            self._session.debug(
                f"      realtime_distribution_system endpoint = {host}"
            )
            self._session.debug(
                f"      realtime_distribution_system port     = {port}"
            )

            #   build the StreamServiceInformation
            stream_service_information = StreamServiceInformation(
                scheme=scheme,
                host=host or "",
                port=port,
                path="",
                data_formats=["tr_json2"],
                location="",
            )
        else:
            #   use the hostname and port parameter from session
            url = self._session._deployed_platform_host
            result = parse_url(url)
            scheme = result.scheme

            if "." in scheme:
                host = scheme
                port = result.path
                try:
                    port = int(port)
                except ValueError:
                    port = ""

                scheme = ""

            else:
                host = result.hostname or result.netloc or result.path
                port = result.port

            scheme, port = get_scheme_port(scheme, port)

            #   build the StreamServiceInformation
            stream_service_information = StreamServiceInformation(
                scheme=scheme,
                host=host or "",
                port=port,
                path="",
                data_formats=["tr_json2"],
                location="",
            )

        #   build the stream connection configuration
        #       note it has only one realtime distribution.
        return RealtimeDistributionSystemConnectionConfiguration(
            self._session,
            [
                stream_service_information,
            ],
            [
                "OMM",
            ],
        )

    async def waiting_for_stream_ready(self, open_state):
        self.debug("waiting for deployed platform streaming ready.")

        #   do waiting for deployed platform session
        await self._session.wait_for_streaming(
            "streaming/pricing/main", "OMM"
        ) and open_state()

    def open(self):
        super().open()

    def authorize(self, first_time_authorize=True):
        pass

    def close(self):
        self.log(logging.DEBUG, "Close platform session...")
        super().close()


class RefinitivDataAndDeployedConnection(DeployedConnection, RefinitivDataConnection):
    def __init__(self, session):
        DeployedConnection.__init__(self, session)
        RefinitivDataConnection.__init__(self, session)

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
        return await RefinitivDataConnection.http_request_async(
            self,
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

    async def get_stream_connection_configuration(self, stream_connection_name: str):
        """this function extract the realtime distribution system information from config file.
                note that the connection_name is a name of the session. default session name is "default-session"

        Parameters
        ----------
        stream_connection_name
            a unique name of the stream connection in the config file.
        i.e. "streaming/pricing/main"

        Returns
        -------
        obj
            the stream connection configuration of the given session and stream connection name
        """

        #   check this is streaming/pricing or not?
        if stream_connection_name.startswith("streaming/pricing/main"):
            #   using the realtime distribution system
            return await DeployedConnection.get_stream_connection_configuration(
                self, stream_connection_name
            )
        else:
            #   using the platform streaming
            return await RefinitivDataConnection.get_stream_connection_configuration(
                self, stream_connection_name
            )

    def open(self):
        RefinitivDataConnection.open(self)

    def authorize(self, first_time_authorize=True):
        RefinitivDataConnection.authorize(self, first_time_authorize)

    def close(self):
        RefinitivDataConnection.close(self)
