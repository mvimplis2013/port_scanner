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
            [{v:'VLAB3', f:"vlab3<div style='color:red; font-style:italic'>Austria DC</div>"}, "", "Main DataCenter"],
            [{v:'VLAB1', f:"vlab1<div style='color:red; font-style:italic'>Athens Vrilissia</div>"}, "", "Small DataCenter"],
            [{v:'VLAB2', f:"vlab1<div style='color:red; font-style:italic'>Athens Cholargos</div>"}, "", "EMail DataCenter"],
            ["serverA", "VLAB3", "Server for Monitoring"],
            ["Container-GUI", "serverA", "Python Flask & JavaScript"],
            ["External-Robot", "serverA", "Python3"],
            ["Internal-Agent", "serverA", "Responds to Forwarded Msgs"],
            ["serverB", "VLAB3", "Supporting Utilies"],
            ["MariaDB", "serverB", "Permanent Storage"],
            ["RabbitMQ", "serverB", "Message-Exchange & RPC"],
        ]);

        $("#chart-div").css('opacity', 0.4);

        var chart = new google.visualization.OrgChart( document.getElementById("chart-div") );

        chart.draw(data, {allowHtml:true});
    }
}

draw_organization();