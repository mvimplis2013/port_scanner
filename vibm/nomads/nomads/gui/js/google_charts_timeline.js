function draw_timeline( server, from_time, to_time, is_up ) {
    google.charts.load("current", {packages: ["timeline"]});
    google.charts.setOnLoadCallback(drawChart);

    var _server     = server;
    var _from       = from_time;
    var _to         = to_time;
    var _is_up      = is_up;

    function drawChart() {
        console.log("Ready to draw a timeline for ... '" + _server + "' / " + _from + " - " + _to + " {" + _is_up + "}");

        var container = document.getElementById("chart-container");
        
        var chart = new google.visualization.Timeline(container);
        
        var dataTable = new google.visualization.DataTable();

        dataTable.addColumn({ type: 'string', id: 'Server-Name' });
        dataTable.addColumn({ type: 'string', id: 'Up & Running' });
        dataTable.addColumn({ type: 'date', id: 'Start' });
        dataTable.addColumn({ type: 'date', id: 'End' });

        dataTable.addRows([
            [ 'Server-1', "OK", new Date(2019, 3, 26), new Date(2019, 3, 28) ]
        ]);

        chart.draw( dataTable );
    }
}

