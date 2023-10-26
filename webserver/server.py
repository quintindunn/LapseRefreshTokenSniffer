from flask import Flask, render_template, request, redirect, url_for

import sys
sys.path.append('..')  # Allow importing from ../proxy_dispatcher


app = Flask(__name__)

app.template_folder = "./templates"

# Structure:
# {
#    <IP>: [<PROXY_UUID>, <PROXY_UUID>]
# }
live_proxies = {}


@app.route("/")
def index():
    return render_template(template_name_or_list="index.html")


@app.route("/proxy", methods=["POST"])
def proxy():
    print('create_proxy')

    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(debug=True)
