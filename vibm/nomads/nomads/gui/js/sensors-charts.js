document.addEventListener("contextmenu", function(e) {
    e.preventDefault();
}, false);

document.getElementById("sensor-1-status").onmousedown = function(event) {
    if (event.which == 3) {
        event.preventDefault();
        confirm("DO you really want to Toggle Sensor State ?");
    }
}