function log(msg) {
    const logWindow = document.getElementById('logWindow');
    if (logWindow.innerHTML.split("\n").length > 8)
	logWindow.innerHTML = "";
    logWindow.innerHTML += (msg + "\n");
}

wsUrl = 'ws://' + window.location.hostname + '/api/control'
log(wsUrl);

const connection = new WebSocket(wsUrl);

connection.addEventListener('open', function (event) {
    log("connected");
});

connection.addEventListener('message', function (event) {
    log(event.data);
});

connection.addEventListener('close', function (event) {
    log("websocket close");
});

connection.addEventListener('error', function (event) {
    log("websocket error");
});

function sendCommand(cmd) {
    if ( connection.readyState == WebSocket.OPEN ) {
	connection.send(cmd);
    } else {
	log("connection is not open (" + connection.readyState.toString() + ")");
    }
}

function refreshIframe(id) {
    var iframe = document.getElementById(id);
    iframe.src = iframe.src;
}
