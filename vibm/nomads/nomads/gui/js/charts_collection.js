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
    $( "td[role='chart']" ).html( $("input[name='chart-type' checked]").val() );
});

$("[role=button-get-data]").on("click", function(event) {
    //find("td[id='status']").removeClass().addClass("bg-success");
    //which_name = $( "#new-name" ).val();

    //$( "#tbl-names #ip-" + arr_num[num_names_add] ).text( which_name );

    //num_names_add += 1;

    console.log("external_mode = " + external_mode);

    alert("Data Games");
});