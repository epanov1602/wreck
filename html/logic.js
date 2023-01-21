function log(msg) {
    const logWindow = document.getElementById('logWindow');
    if (logWindow.innerHTML.split("\n").length > 20)
	logWindow.innerHTML = "";
    logWindow.innerHTML += (msg + "\n");
}

// how to connect to the command interface and create window.sendCommand(...) function
function connectToCommands() {
    const commandUrl = document.location.href.replace('https:', 'wss:').replace('http:', 'ws:') + '/api/control';
    log("Connecting to command interface at " + commandUrl);

    const commandConnection = new WebSocket(commandUrl);
    commandConnection.addEventListener('open', function (event) {
	log("Command websocket connected");
    });
    commandConnection.addEventListener('message', function (event) {
	log(event.data);
    });
    commandConnection.addEventListener('close', function (event) {
	log("Command connection websocket close");
    });
    commandConnection.addEventListener('error', function (event) {
	log("Command connection websocket error");
    });

    // now we can create window.sendCommand(...) function
    window.sendCommand = function(cmd) {
	if ( commandConnection.readyState == WebSocket.OPEN ) {
	    commandConnection.send(cmd);
	} else {
	    log("Command connection websocket is not open (" + commandConnection.readyState.toString() + ")");
	}
    }
}


// how to connect to camera and display video using JMuxer
function connectToCamera() {
    var cameraUrl = document.location.href.replace('https:', 'wss:').replace('http:', 'ws:') + '/rpicam/ws/';
    var jmuxer = new JMuxer({
        node: 'player',
        mode: 'video',
        flushingTime: 0,
        fps: 30,
        debug: false
    });
    log("Connecting to camera at " + cameraUrl);

    var cameraConnection = new WebSocket(cameraUrl);
    cameraConnection.binaryType = 'arraybuffer';
    cameraConnection.addEventListener('open', function (event) {
	log("Camera websocket connected");
    });
    cameraConnection.addEventListener('close', function (event) {
	log("Camera websocket close");
    });
    cameraConnection.addEventListener('error', function (event) {
	log("Camera websocket error");
    });
    cameraConnection.addEventListener('message', function (event) {
        var bytes = new Uint8Array(event.data);
        var update = { video: bytes, };
        jmuxer.feed(update);
    });
}



// finally, the map logic
window.map = null;
window.mark = null;
window.mapTrajectory = []
window.mapsAPIConnected = false;


// what to do when Google Maps API is connected
window.onMapsAPIConnected = function() {
    window.mapsAPIConnected = true;
    log("Google Maps API connected");
};

function redrawMap(point) {
    // if Google Maps API is not connected, we cannot proceed with this point
    if ( !window.mapsAPIConnected ) {
	log(" - GPS point before connected to Google Maps: " + JSON.stringify(point));
	return;
    }

    // if we received an invalid point, we cannot proceed either
    var lat = point.lat;
    var lng = point.lng;
    if ( !lat ) {
	log(" - invalid GPS point: " + JSON.stringify(point));
	return;
    }

    // if the map was not yet created, create it now
    if ( window.map === null ) {
	window.map  = new google.maps.Map(document.getElementById('mapCanvas'), {center:{lat:lat,lng:lng},zoom:12});
	window.mark = new google.maps.Marker({position:{lat:lat, lng:lng}, map:window.map});
    }

    // center around new gps and put marker there
    window.map.setCenter({lat:lat, lng:lng, alt:0});
    window.mark.setPosition({lat:lat, lng:lng, alt:0});

    // make a blue poly line that connects this point to the previous points
    window.mapTrajectory.push(new google.maps.LatLng(lat, lng));
    var trajectoryLine = new google.maps.Polyline({
	path: window.mapTrajectory,
	geodesic: true,
	strokeColor: '#2E10FF'
    });
    trajectoryLine.setMap(window.map);
};

function connectToGPS() {
    const gpsUrl = (window.location.protocol == "https:" ? "wss:" : "ws:") + '//' + window.location.hostname + '/api/gps'
    log("Connecting to GPS at " + gpsUrl);

    const gpsConnection = new WebSocket(gpsUrl);
    gpsConnection.addEventListener('open', function (event) {
	log("GPS websocket connected");
    });
    gpsConnection.addEventListener('close', function (event) {
	log("GPS websocket closed");
    });
    gpsConnection.addEventListener('error', function (event) {
	log("GPS websocket errored");
    });

    gpsConnection.addEventListener('message', function (event) {
	const point = JSON.parse(event.data);
	redrawMap(point);
    });
}
