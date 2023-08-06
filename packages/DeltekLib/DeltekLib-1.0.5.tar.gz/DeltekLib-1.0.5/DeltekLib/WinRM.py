# Deltek Python Library
# Copyright 2021

from typing import Optional, List

import winrm
from robot.api import logger
from robot.utils import ConnectionCache


class WinRM(object):
    """
    Deltek Windows Remote Management Library

    ==Dependencies==
    | robotframework | http://robotframework.org |
    | pywinrm | https:// pypi.python.org/pypi/pywinrm |
    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self) -> None:
        """ Init method. """
        self._session: Optional[winrm.Session] = None
        self._cache = ConnectionCache('No sessions created')

    def create_session(
            self,
            alias: str,
            hostname: str,
            user: str,
            password: str,
            transport: Optional[str] = 'basic',
            server_cert_validation: Optional[str] = 'validate'
    ) -> int:
        """
        Creates a session with windows host.

        :param alias: robot framework alias to identify the session
        :param hostname: windows hostname (not IP)
        :param user: user name
        :param password: account password
        :param transport: basic, ntlm
        :param server_cert_validation: validate, ignore
        :return: Session index

        *Example:*
        | Create Session  |  server  |  windows-host |  Administrator  |  1234567890 |
        """

        logger.debug(f'Connecting using : hostname={hostname}, user={user}, password={password} ')
        self._session = winrm.Session(hostname,
                                      auth=(user, password),
                                      transport=transport,
                                      server_cert_validation=server_cert_validation)
        return self._cache.register(self._session, alias)

    def run_cmd(
            self,
            alias: str,
            command: str,
            params: List[str] = None
    ) -> winrm.Response:
        """
        Executes a command on remote machine.

        :param alias: robot framework alias to identify the session
        :param command: windows command
        :param params: lists of command's parameters
        :return: Result object with methods: status_code, std_out, std_err.

        *Example:*
        | ${params}=  | Create List  |  "/all" |
        | ${result}=  |  Run Cmd  |  server  |  ipconfig  |  ${params} |
        | Log  |  ${result.status_code} |
        | Log  |  ${result.std_out} |
        | Log  |  ${result.std_err} |
        =>
        | 0
        | Windows IP Configuration
        |    Host Name . . . . . . . . . . . . : WINDOWS-HOST
        |    Primary Dns Suffix  . . . . . . . :
        |    Node Type . . . . . . . . . . . . : Hybrid
        |    IP Routing Enabled. . . . . . . . : No
        |    WINS Proxy Enabled. . . . . . . . : No
        |
        """

        if params is not None:
            log_cmd = f'{command} {" ".join(params)}'
        else:
            log_cmd = command
        logger.info(f'Run command on server with alias "{alias}": {log_cmd}')
        self._session = self._cache.switch(alias)
        result = self._session.run_cmd(command, params)
        return result

    def run_ps(
            self,
            alias: str,
            script: str
    ) -> winrm.Response:
        """
        Run power shell script on remote machine.

        :param alias: robot framework alias to identify the session
        :param script: power shell script
        :return: Result object with methods: status_code, std_out, std_err.

        *Example:*

        | ${result}=  |  Run Ps  |  server  |  get-process iexplore|select -exp ws|measure-object -sum|select -exp Sum |
        | Log  |  ${result.status_code} |
        | Log  |  ${result.std_out} |
        | Log  |  ${result.std_err} |
        =>
        | 0
        | 56987648
        |
        """

        logger.info(f'Run power shell script on server with alias "{alias}": {script}')
        self._session = self._cache.switch(alias)
        result = self._session.run_ps(script)
        return result

    def delete_all_sessions(self) -> None:
        """ Removes all sessions with windows hosts"""
        self._cache.empty_cache()
