console.log("Going to Draw an Impressive ORGANIZATION Chart");

function draw_organization( freq_mins, observations ) { //} server, from_time, to_time, is_up ) {
    google.charts.load("current", {packages: ["timeline"]});
    google.charts.setOnLoadCallback(initialize);

    // *** These are COLLECT arrays
    //var _up_observations = up_observations;
    //var _down_observations = down_observations;

    //var _server = _up_observations[0].server_id;
    //var _from = _up_observations

    var _freq_mins      = freq_mins;
    var _observations   = observations;

    var server_status_timeline;

    function initialize() {
        server_status_timeline = pattern_recognition(_freq_mins, _observations);
        drawChart();
    }

    function drawChart() {