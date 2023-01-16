    // our logic for the Map page

    window.map = null;
    window.mark = null;
    window.lineCoords = []
    window.mapsAPIConnected = false;

    window.onMapsAPIConnected = function() {
	window.mapsAPIConnected = true;
	log("Google Maps API connected");
    };

    function redraw(point) {
	// if Google Maps API is not connected, we cannot proceed with this point
	if ( !window.mapsAPIConnected ) {
	    log("received coordinates before connected to Google Maps, point: " + JSON.stringify(point));
	    return;
	}

	// if we received an invalid point, we cannot proceed either
	var lat = point.lat;
	var lng = point.lng;
	if ( !lat ) {
	    log("received an invalid point: " + JSON.stringify(point));
	    return;
	}

	// if the map was not yet created, create it now
	if ( window.map === null ) {
	    window.map  = new google.maps.Map(document.getElementById('map-canvas'), {center:{lat:lat,lng:lng},zoom:12});
	    window.mark = new google.maps.Marker({position:{lat:lat, lng:lng}, map:window.map});
	}

	// center around new coordinates and put marker there
	window.map.setCenter({lat:lat, lng:lng, alt:0});
	window.mark.setPosition({lat:lat, lng:lng, alt:0});

	// make a blue poly line that connects this point to the previous points
	window.lineCoords.push(new google.maps.LatLng(lat, lng));
	var lineCoordinatesPath = new google.maps.Polyline({
	    path: window.lineCoords,
	    geodesic: true,
	    strokeColor: '#2E10FF'
	});
	lineCoordinatesPath.setMap(window.map);
    };

    function log(msg) {
	const logWindow = document.getElementById('log-window');
	if (logWindow.innerHTML.split("\n").length > 8)
	    logWindow.innerHTML = "";
	logWindow.innerHTML += (msg + "\n");
    }

    const coordinatesUrl = 'ws://' + window.location.hostname + '/api/coordinates'
    log("Connecting to coordinates API at URL " + coordinatesUrl);

    const connection = new WebSocket(coordinatesUrl);

    connection.addEventListener('open', function (event) {
	log("Connected to coordinates API");
    });

    connection.addEventListener('message', function (event) {
	point = JSON.parse(event.data);
	redraw(point)
    });

    connection.addEventListener('close', function (event) {
	log("Connection with coordinates API closed");
    });

    connection.addEventListener('error', function (event) {
	log("Connection with coordinates API errored");
    });
