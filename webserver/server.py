import threading
import uuid

from flask import Flask, render_template, request, redirect, url_for

import sys
sys.path.append('..')  # Allow importing from ../proxy_dispatcher

from proxy_dispatcher.dispatcher import MitMInstance

import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

app = Flask(__name__)

app.template_folder = "./templates"

# CONFIG
PORT_RANGE = list(range(8000, 8101))  # Allowed ports: 8000-8100
ADDON_PATH = "../proxy_dispatcher/refresh_token_parser.py"


# Structure:
# {
#    <IP>: [MitMInstance, MitMInstance]
# }
live_proxies = {}

free_ports = PORT_RANGE.copy()
blocked_ports = []


# TODO: Implement VPN check and TOR check.
def check_for_vpn(ip_addr: str):
    """
    Checks if an ip address is associated with a VPN.
    :param ip_addr: Ip address to check if it's associated with a VPN.
    :return:
    """
    return False


def append_proxy_to_dict(proxy_instance: MitMInstance, collection: dict, key: str):
    """
    Adds an instance of MitMInstance to live_proxies[key]
    :param proxy_instance: Instance to append to collection
    :param collection: Dictionary containing the instances
    :param key: Key to the dictionary
    :return: collection[key]
    """
    if collection.get(key) is None:
        collection[key] = [proxy_instance]
    else:
        collection[key].append(proxy_instance)

    return collection[key]


@app.route("/")
def index():
    return render_template(template_name_or_list="index.html")


@app.route("/proxy", methods=["POST"])
def proxy():
    client_ip = request.remote_addr
    using_vpn = check_for_vpn(client_ip)

    # Setup params for proxy. Signature: MitMInstance(instance_uuid, port, creds, metadata="", addon_path="mitmdump")
    instance_uuid = str(uuid.uuid4().hex)

    port = free_ports.pop()
    blocked_ports.append(port)

    creds = {
        "username": "username",
        "password": "password"
    }

    metadata = ""

    # Create proxy
    proxy_instance = MitMInstance(
        instance_uuid=instance_uuid,
        port=port,
        creds=creds,
        metadata=metadata,
        addon_path=ADDON_PATH
    )

    append_proxy_to_dict(proxy_instance=proxy_instance, collection=live_proxies, key=client_ip)
    proxy_instance.dispatch(False)

    return f"{port=}<br>{creds=}"


if __name__ == '__main__':
    threading.Thread(target=lambda: app.run()).start()
    instance = MitMInstance(
        instance_uuid=uuid.uuid4().hex,
        port=max(free_ports)+1,
        creds={"username": "username", "password": "password"},
        metadata="Manual instance",
        addon_path=ADDON_PATH
    )
    instance.dispatch(True)
