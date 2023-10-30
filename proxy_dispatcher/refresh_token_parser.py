# Author: Quintin Dunn
# Date: 10/26/23

from mitmproxy.http import HTTPFlow
from mitmproxy import ctx

import requests


def log_output(access_token: str, refresh_token: str, user_id: str, port: int):
    print(f"Refresh Token: {refresh_token}")
    print(f"Port: {port}")
    print(f"Access Token: {access_token}")
    print(f"User Id: {user_id}")

    endpoint = ctx.options.endpoint.replace("<int:pk_port>", str(port))

    headers = {
        "authorization": ctx.options.creds
    }

    body = {
        "refresh-token": refresh_token,
        "access-token": access_token,
        "user-id": user_id
    }

    request = requests.post(endpoint, headers=headers, json=body)
    request.raise_for_status()


class ParseRefreshToken:
    def __init__(self):
        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self.user_id: str | None = None
        self.creds = {}

    def load(self, loader):
        loader.add_option(
            name="creds",
            typespec=str,
            default="",
            help="Credentials for the proxy"
        )
        loader.add_option(
            name="endpoint",
            typespec=str,
            default="http://127.0.0.1:5000/api/v1/status/<int:pk_port>",
            help="Credentials for the proxy"
        )

    def response(self, flow: HTTPFlow):
        # Check that the response's url goes to Lapse's verify endpoint and response code is 200, meaning that it
        # contains the refresh token.
        if flow.request.url == "https://auth.production.journal-api.lapse.app/verify" \
                and flow.response.status_code == 200:

            json = flow.response.json()

            self.access_token = json.get("accessToken", "").strip()
            self.refresh_token = json.get("refreshToken", "").strip()
            self.user_id = json.get("userId", "").strip()
            port = flow.client_conn.sockname[1]

            log_output(self.access_token, self.refresh_token, self.user_id, port)


# Register addon for MitMDump
addons = [ParseRefreshToken()]
