google.charts.load("current", {packages: ["timeline"]});
google.charts.setOnLoadCallback(draw_timeline)

function draw_timeline() {
    console.log("Hello from Other Module ... " + text);
}