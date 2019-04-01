console.log("Going to Draw an Impressive ORGANIZATION Chart");

CHART_TYPE = "orgchart"

function draw_organization() { //} server, from_time, to_time, is_up ) {
    google.charts.load("current", {packages: [CHART_TYPE]});
    google.charts.setOnLoadCallback(initialize);

    function initialize() {
        //server_status_timeline = pattern_recognition(_freq_mins, _observations);
        drawChart();
    }

    function drawChart() {
        var data = new google.visualization.DataTable();
        data.addColumn("string", "Name");
        data.addColumn("string", "Category");
        data.addColumn("string", "ToolTip");

        // For each organization chart box, provide the Name/ Category and ToolTip to show.
        data.addRows([
            [{v:'Mike', f:"Mike<div style='color:red; font-style:italic'>President</div>"}, "", "The President"],
            [{v:'Jim', f:"Jim<div style='color:red; font-style:italic'>Vice President</div>"}, "Mike", "VP"],
            ["Alice", "Mike", ""],
            ["Bob", "Jim", "Bob Sponge"],
            ["Carol", "Bob", ""],
        ]);

        $("#chart-div").css('opacity', 0.6);

        var chart = new google.visualization.OrgChart( document.getElementById("chart-div") );

        chart.draw(data, {allowHtml:true});
    }
}

draw_organization();