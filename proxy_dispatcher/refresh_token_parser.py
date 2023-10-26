# Author: Quintin Dunn
# Date: 10/26/23

# Import MitMProxy for type hinting, but if it cannot find it just use the str "HTTPFlow" as typing isn't functional.
try:
    from mitmproxy.http import HTTPFlow
except ImportError:
    HTTPFlow = "HTTPFlow"


def log_output(access_token: str, refresh_token: str, user_id: str, port: int):
    print(f"Refresh Token: {refresh_token}", end="\n\n")
    print(f"Port: {port}", end="\n\n")
    print(f"Access Token: {access_token}", end="\n\n")
    print(f"User Id: {user_id}", end="\n\n")


class ParseRefreshToken:
    def __init__(self):
        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self.user_id: str | None = None

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
