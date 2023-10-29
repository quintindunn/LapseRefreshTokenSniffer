import json
import os
import threading
import time
import uuid

import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for

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


def verify_authorization(req: request, port: int) -> None | tuple[str, int]:
    # Check that a proxy is live on the port:
    if port not in live_proxies:
        return "Proxy not found", 404

    proxy = live_proxies[port]

    basic_auth_client = req.headers.get("authorization", "")

    # Try body auth
    if basic_auth_client == "":
        basic_auth_client = req.args.get("authorization")

    # Setup creds to be in basic format
    usr, pwd = proxy.creds['username'], proxy.creds['password']
    basic_auth_proxy = f"{usr}:{pwd}"

    if basic_auth_client != basic_auth_proxy:
        return f"Invalid credentials", 403


@app.route("/")
def index():
    return render_template(template_name_or_list="index.html")


@app.route("/proxy", methods=["POST"])
def gen_proxy():
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
    """
    Returns the status attribute of a proxy
    :param pk_port: port of the proxy
    :return: json of the proxy status attribute
    """
    verify = verify_authorization(request, pk_port)
    if verify:
        return verify

    return json.dumps(live_proxies[pk_port].status, indent=2)


@app.route("/api/v1/status/<int:pk_port>", methods=["POST"])
def update_proxy_creds(pk_port: int):
    """
    Internal endpoint, updates the status of a proxy
    :param pk_port: port of the proxy
    :return: redirect to /api/v1/check/<int:pk_port>
    """
    verify = verify_authorization(request, pk_port)
    if verify:
        return verify

    proxy: MitMInstance = live_proxies[pk_port]
    proxy.status.update(request.json)

    return check_proxy_status(pk_port=pk_port)


@app.route("/proxy/status/<int:pk_port>")
def proxy_status_frontend(pk_port: int):
    verify = verify_authorization(request, pk_port)
    if verify:
        return verify
    ctx = {
        'creds': request.args.get("authorization").split(":")
    }
    return render_template("status.html", **ctx)


if __name__ == '__main__':
    threading.Thread(target=lambda: app.run()).start()
    instance = MitMInstance(
        instance_uuid=uuid.uuid4().hex,
        port=max(free_ports) + 1,
        creds={"username": "admin", "password": "password"},
        metadata="Manual instance",
        addon_path=ADDON_PATH
    )

    # For testing
    r = requests.post("http://127.0.0.1:5000/proxy")
    r.raise_for_status()
    r = requests.post("http://127.0.0.1:5000/api/v1/status/8100", headers={"authorization": "username:password"},
                      json=json.loads(os.getenv("payload")))
    r.raise_for_status()
    instance.dispatch(blocking=True)
