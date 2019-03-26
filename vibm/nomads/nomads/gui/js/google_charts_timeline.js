function draw_timeline(server, a, b, is_up) {
    google.charts.load("current", {packages: ["timeline"]});
    google.charts.setOnLoadCallback(drawChart);

    _server = server;
    _from = a;
    _to = b;
    _is_up = is_up;

    function drawChart() {
        console.log("Hello from Other Module ... " + text);
    }
}

