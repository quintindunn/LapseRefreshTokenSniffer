def log_output(access_token: str, refresh_token: str, user_id: str):
    print(f"Access Token: {access_token}")
    print(f"Refresh Token: {refresh_token}")
    print(f"User Id: {user_id}")


class ParseRefreshToken:
    def __init__(self):
        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self.user_id: str | None = None

    def response(self, flow):
        if flow.request.url == "https://auth.production.journal-api.lapse.app/verify" \
                and flow.response.status_code == 200:
            json = flow.response.json()

            self.access_token = json.get("accessToken", "").strip()
            self.refresh_token = json.get("refreshToken", "").strip()
            self.user_id = json.get("userId", "").strip()

            log_output(self.access_token, self.refresh_token, self.user_id)


addons = [ParseRefreshToken()]
