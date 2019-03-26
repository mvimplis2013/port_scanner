function draw_timeline( server, from_time, to_time, is_up ) {
    google.charts.load("current", {packages: ["timeline"]});
    google.charts.setOnLoadCallback(drawChart);

    var _server     = server;
    var _from       = from_time;
    var _to         = to_time;
    var _is_up      = is_up;

    function drawChart() {
        console.log("Ready to draw a timeline for ... '" + _server + "' / " + _from + " - " + _to + " {" + _is_up + "}");

        var container = document.getElementById("timeline-container");
        
        var chart = new google.visualization.Timeline(container); 
    }
}

