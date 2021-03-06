ROBOT_URL = "http://" + location.hostname + ":5000/"
RPC_GET_VLAB_PING_DATA = "reports/external/get-ip-data"
RPC_GET_VLAB_PORT_DATA = "reports/external/get-ip-and-port-data"

METHOD = "GET"
CONTENT_TYPE = "application/json; charset=utf-8"

google.charts.load("current", {"packages": ["bar"]});
google.charts.setOnLoadCallback(drawChart);

function drawChart( server_id, _from, _to, _is_up ) {
    //var data = google.visualization.arrayToDataTable([
    //    ["Year", "Sales", "Expenses", "Profit"], 
    //    ["2014", 1000, 400, 200],
    //    ["2015", 1170, 460, 250],
    //    ["2016", 660, 1120, 300],
    //    ["2017", 1030, 540, 350]
    //]);

    var result = dateFns.addMinutes(new Date(2014, 6, 10, 12, 0), 30);
    console.log("New Date is ..." + result);

    var data = google.visualization.arrayToDataTable([
        ["Server-ID", "From", "To", "is-UP"],
        [server_id, _from, _to, is_up]
    ]);

    var options = {
        chart: {
            title: "Company Performance",
            subtitle: "Sales, Expenses, and Profit: 2014-2017",
        }, 
        bars: "horizontal",
        hAxis: {
            format: 'decimal'
        },
        height: 400,
        colors: ["#1b9e77", "#d95f02", "#7570b3"]
    };

    var chart = new google.charts.Bar( document.getElementById( "chart_div" ));

    chart.draw(data, google.charts.Bar.convertOptions(options));

    /*var btns = document.getElementById("btn-group");

    btns.onClick = function(e) {
        if (e.target.tagName === "BUTTON") {
            options.hAxis.format = e.target.id === "none" ? "" : e.target.id; 

            chart.draw(data, google.charts.Bar.convertOptions(options));
        }
    }*/
}

$("[data-toggle=sidebar-colapse]").click( function() {
    SidebarCollapse();
});

$("[data-toggle=sidebar-colapse]").click( function() {
    SidebarCollapse();
});

/* 
 ** Define External Mode Ping or Scan 
 */
$("#ping-ip").on("click", function (e) {
    $("td[role='monitoring']").html("Ping-IP");
});

$("#scan-ports").on("click", function (e) {
    $("td[role='monitoring']").html("Scan-Ports");
});

/**  
 * Define Chart Type -- An increasing number of Graphs is supported.
 */
$("input[name='chart-type'").on("click", function (e) {
    //console.log("Hi");
    $("td[role='chart']").html($("input[name='chart-type']:checked").val());
});

/**  
 * Define Time Range -- Select time period of displayed performance data.
 */
$("input[name='time-range'").on("click", function (e) {
    //console.log("Hi");
    $("td[role='duration']").html($("input[name='time-range']:checked").val());
});

/** *********************************************************************************************************
 *   Press the button to get data from server. There are two options for requested vlab performance data set
 *   Either the whole data set is retrieved for the entire time range and interesting pieces are extracted on client.
 *   Or the backend datastore queries contain _from & _to parameters. 
 *   The whole data set enables an independent client operation in case of connection with server lost.
 *  *********************************************************************************************************  
 */
$("[role=button-get-data]").on("click", function (event) {
    //console.log("Get Ping Data Button Clicked !");
    
    // STEP 1: Create the RPC address
    rpc_url = ROBOT_URL;
    if ($("input[name='external-monitoring']:checked").val() == "ping-ip") {
        //console.log("Ready to Get PING Data");
        rpc_url += RPC_GET_VLAB_PING_DATA;
    } else if ($("input[name='external-monitoring']:checked").val() == "scan-ports") {
        //console.log("Ready to get the Open PORTS Data");
        rpc_url += RPC_GET_VLAB_PORT_DATA;
    } else {
        throw "No RPC for selected Monitoring-Type !";
    }

    //console.log( "***" + rpc_url );

    // STEP 2: Chart Type to Render
    chart_type = $("input[name='chart-type']:checked").val();
    console.log("Requested Chart Type is: " + chart_type);

    // STEP 3: Time Range of Requested Data
    time_range = $("input[name='time-range']:checked").val();
    console.log("Time Range for Data/ From-To: " + time_range);

    // STEP 4: Prepare the data to send to server 
    _data = { 
        "time-range": time_range
    };

    var deferred_data = new jQuery.Deferred();

    // *********************************************************************
    // ******    STEP 4: Make AJAX Request from Client to Server     *******
    // *********************************************************************
    $.ajax({
        method: METHOD,
        //url: "http://vlab3.dyndns.org:5000/reports/external/get_performance_data",
        url: rpc_url,
        contentType: CONTENT_TYPE,
        data: _data
    }).done(function (data) {
        // *** HOW OFTEN SERVERS-PING HAPPENS ? ***
        _freq_mins = data.freq_mins
        // *** PING RESPONSES ***
        _data = data.records_found
        
        records_length = _data.length;
        console.log("Contacted server for VLAB performance data ... Freq-Mins = " + _freq_mins + " #" + records_length);
        
        $("div[role='statistics'").css("color", "yellow");

        //drawChart(1, from_to.from, from_to.to, "true");
        draw_timeline( _freq_mins, _data );

        //alert("success");
    }).fail(function() {
        alert("error");
    });
});