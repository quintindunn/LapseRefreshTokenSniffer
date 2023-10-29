const proxy_username = document.getElementById("p-username").value;
const proxy_password = document.getElementById("p-password").value;

const endpoint = document.getElementById("endpoint").value;

const output = document.getElementById("proxy-results");

function update() {
    let XHR = new XMLHttpRequest()

    XHR.open("POST", endpoint);
    XHR.setRequestHeader("authorization", `${proxy_username}:${proxy_password}`)
    XHR.onload = () => {
        if (XHR.status === 200) {
            output.innerText = XHR.responseText;
        }
    }
    XHR.send()
}

setInterval(update, 1000);