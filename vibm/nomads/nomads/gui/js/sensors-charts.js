document.getElementById("sensor-1-status").onmousedown = function(event) {
    if (event.which == 3) {
        evenalert("Right Clicked");
        event.preventDefault();
    }
}