# Author: Quintin Dunn
# Date: 10/26/23
# Description: Dispatching script for creating a proxy in a nonblocking way.

import logging
import os
import pathlib
import signal
import subprocess
import sys
import threading
import uuid

import psutil

logger = logging.getLogger("dispatcher.py")

# MitMDump exe
MITMDUMP = "mitmdump"


class MitMInstance:
    def __init__(self, instance_uuid, port, creds, metadata=None, addon_path="mitmdump", generator_ip="127.0.0.1"):
        if metadata is None:
            metadata = {}

        self.uuid = instance_uuid
        self.creds = creds
        self.port = port
        self.metadata = metadata
        self.addon_path = addon_path
        self.generator_ip = generator_ip

        self.status = {}

        self.proc = None
        self.thread = None

        self.alive = True

    def _dispatcher(self):
        """
        Starts the MitMDump process.
        :return:
        """
        logger.info(f"Starting MitMDump instance {self.port=} {self.uuid=} {self.creds=} {self.metadata=}".
                    replace("self.", ""))

        # Add the credentials to the command if the proxy uses a username and password for authentication
        if self.creds:
            basic_auth = f"{self.creds['username']}:{self.creds['password']}"
            command_suffix = ["--proxyauth", basic_auth, "--set", f"creds={basic_auth}"]
        else:
            command_suffix = []

        # Setup command for mitmdump, ignore appattest as if it goes through the proxy it will refuse the connection.
        command = [MITMDUMP,
                   "-q",
                   "-p", str(self.port),
                   "-s", self.addon_path,
                   "--ignore-hosts", "register.appattest.apple.com"
                   ] + command_suffix
        self.proc = subprocess.Popen(command, stdout=sys.stdout, stdin=subprocess.PIPE, shell=True)
        self.proc.wait()

        logger.info(f"MitMDump instance {self.uuid=} completed!".
                    replace("self.", ""))

    def dispatch(self, blocking=False):
        """
        Starts a new instance of MitMDump with the refresh_token_parser.py addon.
        :param blocking: If True, the instance will start in the main thread, otherwise it will start in a different
        thread
        :return:
        """
        if blocking:
            self._dispatcher()
            return

        self.thread = threading.Thread(target=self._dispatcher, daemon=True)
        self.thread.start()

    def kill(self):
        for proc in psutil.process_iter():
            for conns in proc.connections(kind='inet'):
                if conns.laddr.port == self.port:
                    try:
                        proc.send_signal(signal.SIGTERM)
                    except psutil.NoSuchProcess:
                        pass
                    finally:
                        self.metadata['live'] = False

                    return


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    addon_path = str(pathlib.Path(os.getcwd()) / "refresh_token_parser.py")

    instance = MitMInstance(
        instance_uuid=uuid.uuid4().hex,
        port=8004,
        creds={"username": "username", "password": "password"},
        metadata="Manual instance",
        addon_path=addon_path
    )

    instance.dispatch(False)

    input()