function draw_timeline() {
    google.charts.load("current", {packages: ["timeline"]});
    google.charts.setOnLoadCallback(init);

    console.log("Hello from Other Module ... " + text);
}

