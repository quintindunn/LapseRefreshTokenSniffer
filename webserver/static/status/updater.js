const proxy_username = document.getElementById("p-username").value;
const proxy_password = document.getElementById("p-password").value;

const endpoint = document.getElementById("endpoint").value;

const output = document.getElementById("proxy-results");
const end_warning = document.getElementById("end-warning");

function update() {
    let XHR = new XMLHttpRequest()

    XHR.open("POST", endpoint);
    XHR.setRequestHeader("authorization", `${proxy_username}:${proxy_password}`)
    XHR.onload = () => {
        if (XHR.status === 200) {
            output.innerText = XHR.responseText;
        }
        else if (XHR.status === 404) {
            clearInterval(interval);
            warn_over();
        }
    }
    XHR.send()
}

function warn_over() {
    end_warning.style.display = "block";
}

let interval = setInterval(update, 1000);