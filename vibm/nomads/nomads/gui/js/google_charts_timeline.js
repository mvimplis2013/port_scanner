if (typeof collect === 'function') {
    console.log( "COLLECT library is loaded and can be used" )
} else {
    // return
    throw "COLLECT library not installed and need to abort the PATTERN recognition processing !";
} // EndOf LODASH existance check up

if (typeof dateFns === 'object') {
    console.log( "DATE-FNS library is loaded and can be used" )
} else {
    // return
    throw "DATE-FNS library not installed and need to abort the PATTERN recognition processing !";
} // EndOf LODASH existance check up

function pattern_recognition(freq_mins, data) {
    console.log( "..." + data);

    // Two different arrays for UP and DOWN observations
    const total       = collect( data );
    const length      = total.count();

    const first_n     = total.chunk( length-1 );
    const last_n      = total.slice( 1 );

    // Difference 
    diff_values       = last_n.diff(first_n);
    
    // Must read this and next record and decide whether continuous being in UP state 
    for (i=0; i<records_length; i++) {
        row = data[i];
      
        //console.log("Observation-Datetine = " + i + " / " + row.observation_datetime + " / " + row.is_up + " / " + row.server_id);
    
        server_id = row.server_id;
        is_up = row.is_up;
        observation_datetime = row.observation_datetime;
    
        if (is_up == 1) {
            // This is an UP server observation
            up_array.push( observation_datetime );
        } else if (is_up == 0) {
            down_array.push( observation_datetime );
        } 
    }
    
    console.log( "Number of server-UP/ DOWN observations are ..." + up_array.all().length + "/ " + down_array.all().length);
    
    return { "up_array": up_array, "down_array": down_array };
}

function draw_timeline( freq_mins, observations ) { //} server, from_time, to_time, is_up ) {
    google.charts.load("current", {packages: ["timeline"]});
    google.charts.setOnLoadCallback(initialize);

    //var _server     = server;
    //var _from       = from_time;
    //var _to         = to_time;
    //var _is_up      = is_up;

    // *** These are COLLECT arrays
    //var _up_observations = up_observations;
    //var _down_observations = down_observations;

    //var _server = _up_observations[0].server_id;
    //var _from = _up_observations

    var _freq_mins      = freq_mins;
    var _observations   = observations;

    function initialize() {
        pattern_recognition(_freq_mins, _observations);
        drawChart();
    }

    function drawChart() {
        /*console.log("Ready to draw a timeline for ... '" + _server + "' / " + _from + " - " + _to + " {" + _is_up + "}");

        var container = document.getElementById("chart-container");
        
        var chart = new google.visualization.Timeline(container);
        
        var dataTable = new google.visualization.DataTable();

        dataTable.addColumn({ type: 'string', id: 'Server-Name' });
        dataTable.addColumn({ type: 'string', id: 'Up & Running' });
        dataTable.addColumn({ type: 'date', id: 'Start' });
        dataTable.addColumn({ type: 'date', id: 'End' });

        dataTable.addRows([
            [ 'Server-1', "OK", new Date(2019, 3, 26), new Date(2019, 4, 28) ],
            [ 'Server-2', "OK", new Date(2019, 4, 30), new Date(2019, 6, 20) ]
        ]);

        chart.draw( dataTable );*/
    }
}

