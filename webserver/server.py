import datetime
import json
import random
import threading
import time
import uuid

from flask import Flask, render_template, request, jsonify, redirect, url_for

import sys

import logging

sys.path.append('..')  # Allow importing from ../proxy_dispatcher

from proxy_dispatcher.dispatcher import MitMInstance

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

app = Flask(__name__)

app.template_folder = "./templates"

# CONFIG
PORT_RANGE = list(range(8000, 8100))  # Allowed ports: 8000-8100
ADDON_PATH = "../proxy_dispatcher/refresh_token_parser.py"

PROXY_LIFETIME = 0.0625  # 10 minutes.

# Structure:
# {
#    <port>: MitMInstance
# }
live_proxies = {}

free_ports = PORT_RANGE.copy()

rented_proxy_ips = set()


# TODO: Implement VPN check and TOR check.
def check_for_vpn(ip_addr: str):
    """
    Checks if an ip address is associated with a VPN.
    :param ip_addr: Ip address to check if it's associated with a VPN.
    :return:
    """
    return False


def gen_proxy_password() -> str:
    """
    Generates a password for a proxy
    :return: Password for the proxy
    """
    base = uuid.uuid4().hex[:15]
    final = []
    for char in base:
        if random.randint(0, 1):
            char = char.upper()
        final.append(char)

    return ''.join(final)


def verify_authorization(req: request, port: int) -> None | tuple[str, int]:
    """
    Verifies that the request sent can authorize correctly for the given port.
    :param req: request
    :param port: port of proxy
    :return: None if the authentication passed, else a tuple with a valid return for the request.
    """
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
    """
    Endpoint to generate a new proxy.
    :return:
    """
    client_ip = request.remote_addr

    if client_ip in rented_proxy_ips:
        return "You already have an active proxy", 429

    using_vpn = check_for_vpn(client_ip)

    # Setup params for proxy. Signature: MitMInstance(instance_uuid, port, creds, metadata="", addon_path="mitmdump")
    instance_uuid = str(uuid.uuid4().hex)

    if len(free_ports) == 0:
        return "No free ports, please wait and try again later.", 503

    port = free_ports.pop()

    creds = {
        "username": f"{port}_{int(time.time())}",
        "password": gen_proxy_password()
    }

    metadata = ""

    # Create proxy
    proxy_instance = MitMInstance(
        instance_uuid=instance_uuid,
        port=port,
        creds=creds,
        metadata=metadata,
        addon_path=ADDON_PATH,
        generator_ip=client_ip
    )

    live_proxies[port] = proxy_instance

    rented_proxy_ips.add(client_ip)

    created = datetime.datetime.now()
    proxy_instance.metadata = {
        "created_at": created,
        "expires_at": created + datetime.timedelta(minutes=PROXY_LIFETIME),
        "live": True
    }
    proxy_instance.dispatch(False)

    basic_auth = f"{creds['username']}:{creds['password']}"
    return redirect(f"{url_for('proxy_status_frontend', pk_port=port)}?authorization={basic_auth}")


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
    """
    Route for the frontend to view the response of a proxy
    :param pk_port: port of the proxy
    :return:
    """
    verify = verify_authorization(request, pk_port)
    if verify:
        return verify
    ctx = {
        'creds': request.args.get("authorization").split(":"),
        'ip': request.server[0],
        'port': pk_port
    }
    return render_template("status.html", **ctx)


def proxy_manager():
    """
    Keeps track of the proxies and kills proxies that have reached eol.
    :return:
    """
    while True:
        remove = []
        for port, proxy in live_proxies.items():
            expires = proxy.metadata['expires_at']
            if proxy.proc is None or not proxy.metadata['live']:
                continue
            if (expires - datetime.datetime.now()).total_seconds() < 0:
                # kill the proxy as it has expired...
                print(f"Killing proxy at port {port}")
                proxy.kill()
                print(f"Proxy at port {port} killed!")
                remove.append(port)

                rented_proxy_ips.remove(proxy.generator_ip)

        for port in remove:
            del live_proxies[port]

            free_ports.append(port)

        time.sleep(2.5)


if __name__ == '__main__':
    threading.Thread(target=lambda: app.run()).start()
    threading.Thread(target=proxy_manager, daemon=True).start()
    instance = MitMInstance(
        instance_uuid=uuid.uuid4().hex,
        port=max(free_ports) + 1,
        creds={"username": "admin", "password": "password"},
        metadata="Manual instance",
        addon_path=ADDON_PATH
    )

    instance.dispatch(blocking=True)
