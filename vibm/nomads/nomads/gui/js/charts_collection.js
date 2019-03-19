/*google.charts.load("current", {"packages": ["bar"]});
google.charts.setOnLoadCallback(drawChart);

function drawChart() {
    var data = google.visualization.arrayToDataTable([
        ["Year", "Sales", "Expenses", "Profit"], 
        ["2014", 1000, 400, 200],
        ["2015", 1170, 460, 250],
        ["2016", 660, 1120, 300],
        ["2017", 1030, 540, 350]
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

    var btns = document.getElementById("btn-group");

    btns.onClick = function(e) {
        if (e.target.tagName === "BUTTON") {
            options.hAxis.format = e.target.id === "none" ? "" : e.target.id; 

            chart.draw(data, google.charts.Bar.convertOptions(options));
        }
    }
}

$("[data-toggle=sidebar-colapse]").click( function() {
    SidebarCollapse();
});

$("[data-toggle=sidebar-colapse]").click( function() {
    SidebarCollapse();
});*/

/* 
** Define External Mode Ping or Scan 
*/
$("#ping-ip").on("click", function(e) {
    $("td[role='monitoring']").html( "Ping-IP" );
});

$("#scan-ports").on("click", function(e) {
    $("td[role='monitoring']").html( "Scan-Ports" );
});

/**  
 * Define Chart Type -- An increasing number of Graphs is supported.
*/
$( "input[name='chart-type'" ).on( "click", function(e) { 
    //console.log("Hi");
    $( "td[role='chart']" ).html( $("input[name='chart-type']:checked").val() );
});

/**  
 * Define Time Range -- Select time period of displayed performance data.
*/
$( "input[name='time-range'" ).on( "click", function(e) { 
    //console.log("Hi");
    $( "td[role='duration']" ).html( $("input[name='time-range']:checked").val() );
});

/** *********************************************************************************************************
 *   Press the button to get data from server. There are two options for requested vlab performance data set
 *   Either the whole data set is retrieved for the entire time range and interesting pieces are extracted on client.
 *   Or the backend datastore queries contain _from & _to parameters. 
 *   The whole data set enables an independent client operation in case of connection with server lost.
 *  *********************************************************************************************************  
 */
$("[role=button-get-data]").on( "click", function(event) {
    $.ajax( {
        url: "vlab3.dyndns.org:5000/reports/external/get_perfornance_data",
        success: function(data) {
            console.log("Contacted server for VAB performance data ... " + data)
        }
    });
});