NEXT_OBSERVATION_THRESHOLD_MINS = 2

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

function pattern_recognition(freq_mins, observations) {
    //console.log( "..." + observations[10].observation_datetime);
    
    const _observations  = collect( observations );
    const _datetimes     = _observations.pluck( "observation_datetime" );

    //console.log( "..." + _datetimes.all() );

    // Two different arrays for UP and DOWN observations
    const parse_all  = collect();
    
    _datetimes.each( (item) => {
        // console.log("Item is ... " + item);
        
        // Check whether a valid date
        d_item = dateFns.parse(item);
        if (dateFns.isDate( d_item ) === false) {
            throw "Not a Datetime to Handle Observation ..." + item;
        }

        // Store the DATE value
        parse_all.push(d_item);
        
        //my_time = dateFns.getTime(item);
        //parse_all.push(my_time);
        //console.log("Time is ... " + my_time);        
    });

    const length      = parse_all.count();
    const first_n     = parse_all.chunk( length-1 ).get(0);
    const last_n      = parse_all.slice( 1 );

    // Difference ... NEED TO USE THE DATE LIBRARY AND TRANSFORM FROM STRING TO DATES
    var number_of_periods = 0;    
    var glasses_on = false;
    const measurementTimes = collect();

    const server_status_timeline = collect();
    for (i=0; i<first_n.count(); i++) {
        var c = first_n.get(i);
        var n = last_n.get(i);

        //console.log("Now & Next are ..." + c + " --- " + typeof c);

        if (dateFns.isDate(c) !== true || dateFns.isDate(n) !== true) {
            throw "This and Next ... Problem with Dates !";
        }

        var time_diff = dateFns.differenceInMinutes( n, c );

        // The current and next observation have the same server-status ?
        var p1 = _observations.get(i);
        var p2 = _observations.get(i+1);

        // When sparity is big ... 2 x sampling-freq 
        thresh = NEXT_OBSERVATION_THRESHOLD_MINS * freq_mins;

        if ( time_diff > freq_mins && time_diff > thresh ) {
            // CAUTION : Sparce Consecutive Observation ... time taken GreaterThan Normal Frequency
            console.log("CAUTION : Sparce Consecutive Observations : \n" + 
                "Curr Measurement Time is ..." + p1.observation_datetime + "\n" +
                "Next Measurement Time is ..." + p2.observation_datetime + "\n" + 
                "Time Difference VS Sampling Frequency is ..." + time_diff + " > " + freq_mins); 

            continue;
        } 

        if (p1.is_up === p2.is_up) {
            // Server status is same ... now VS next
            if (glasses_on === false) {
                number_of_periods += 1;
                glasses_on = true;

                console.log("Entering a new Server Operation Window #" + number_of_periods);
            }

            measurementTimes.push( c, n );
        } else if (p1.is_up === true && p2.is_up === false) {
            // Suddent server status change ... Was UP and Now is Down
            console.log("Found that server state was Up and went Down");
            // Finished inspecting a time period
            glasses_on = false;

            // *** Finish with current period measurements ***
            measurementTimes.push( c );
            var min = measurementTimes.min();
            var max = measurementTimes.max();
            
            server_status_timeline.push({
                "period-id": number_of_periods,
                "from": min,
                "to": max
            });

            // New sampling time array
            
            measurementTimes = collect();
        } else { //if (p1.is_up === false && p2.is_up === true) {
            // Suddent server status change ... Was Down and Now is UP
            console.log("Found that server state was Down and went Up");

            // Starting inspecting new time period
            number_of_periods += 1;
            glasses_on = true;

            // *** Finish with current period measurements ***
            measurementTimes.push( n );

            var min = measurementTimes.min();
            var max = measurementTimes.max();
            
            server_status_timeline.push({
                "period_id": number_of_periods,
                "from": min,
                "to": max
            });            
        }
    }

    console.log("Number of Server State Change Found ..." + number_of_periods);
    measurementTimes.each( (item) => {
        console.log("Details of Server Operation Time-Period:\n" + 
            "Period-ID: " + item.get("period-id"));
    });
    
    // Must read this and next record and decide whether continuous being in UP state 
    /*for (i=0; i<records_length; i++) {
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
    
    return { "up_array": up_array, "down_array": down_array };*/
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

