import threading
import uuid

from flask import Flask, render_template, request, jsonify

import sys

import logging

sys.path.append('..')  # Allow importing from ../proxy_dispatcher

from proxy_dispatcher.dispatcher import MitMInstance


logging.basicConfig(stream=sys.stdout, level=logging.INFO)

app = Flask(__name__)

app.template_folder = "./templates"

# CONFIG
PORT_RANGE = list(range(8000, 8101))  # Allowed ports: 8000-8100
ADDON_PATH = "../proxy_dispatcher/refresh_token_parser.py"

# Structure:
# {
#    <port>: MitMInstance
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

    live_proxies[port] = proxy_instance
    proxy_instance.dispatch(False)

    return f"{port=}<br>{creds=}"


@app.route("/api/v1/check/<int:pk_port>", methods=["POST"])
def check_proxy_status(pk_port: int):
    # Check that a proxy is live on the port:
    if pk_port not in live_proxies:
        return "Proxy not found", 404

    return jsonify(live_proxies[pk_port].status)


if __name__ == '__main__':
    threading.Thread(target=lambda: app.run()).start()
    instance = MitMInstance(
        instance_uuid=uuid.uuid4().hex,
        port=max(free_ports) + 1,
        creds={"username": "admin", "password": "password"},
        metadata="Manual instance",
        addon_path=ADDON_PATH
    )
    instance.dispatch(blocking=True)
