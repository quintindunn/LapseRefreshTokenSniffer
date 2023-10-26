# Author: Quintin Dunn
# Date: 10/26/23
# Description: Dispatching script for creating a proxy in a nonblocking way.

import logging
import os
import pathlib
import subprocess
import sys
import threading
import uuid

logger = logging.getLogger("dispatcher.py")

# MitMDump exe
MITMDUMP = "mitmdump"


class MitMInstance:
    def __init__(self, instance_uuid, port, creds, metadata="", addon_path="mitmdump"):
        self.uuid = instance_uuid
        self.creds = creds
        self.port = port
        self.metadata = metadata
        self.addon_path = addon_path

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

        command = [MITMDUMP, "-p", str(self.port), "-s", self.addon_path, "-q"]

        self.proc = subprocess.Popen(command, stdout=sys.stdout, shell=True)
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

    instance = MitMInstance(
        instance_uuid=uuid.uuid4().hex,
        port=8005,
        creds={"username": "username", "password": "password"},
        metadata="Manual instance",
        addon_path=addon_path
    )

    # At least one instance that's blocking is required. Currently unsure why, a non-blocking workaround would be better
    instance.dispatch(True)
