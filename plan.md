# What needs to be done:

## Option 1:
Tracking of clients independently via domain connected through. This will allow us to generate every user their own uuid, and make them connect to a proxy with an address similar to `28f4551786424761bd2376cacecc9b0a.lapsetokensniffer.quintindev.com:8008`. Once they get the response from the `/verify` we can then redirect traffic on the proxy from `lapsetokensniffer.quintindev.com:80` to a dynamically rendered page from the proxy, which contains the `refresh token`, `access token`, and `user id`.

## Option 2:
Create an endpoint on a server I own, say `/generaterefresh`, when a user goes to this endpoint and solves a captcha in the backend it spins up a docker container that allows a randomly generated port through, (port forward all ports within some range). Also generate credentials to stop port scanner attacks. In the docker container start a new instance of MitMProxy with the addon [refresh_token_parser.py](https://github.com/quintindunn/LapseRefreshTokenSniffer/blob/main/refresh_token_parser.py). In the addon, rework the `log_output` function to send a HTTP request to the same server with the `/generaterefresh` endpoint. In the backend link the sessions and display the content. This stops us from needing to track which client is which on the proxy, and leaves a simpler to manage backend.
