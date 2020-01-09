document.addEventListener("contextmenu", function(e) {
    e.preventDefault();
}, false);

document.getElementById("sensor-1-status").onmousedown = function(event) {
    if (event.which == 3) {
        event.preventDefault();
        
        if (confirm("Do you really want to Toggle Sensor State ?")) {
            // Proceed with Sensor State Toggle
            $.ajax({
                type: "POST",
                url: "mqtt/publish_state",
                dataType: "json",
                data: JSON.stringnify("lamp"),
                contentType: "application/json;charset=UTF-8",
                success: function(data) {
                    console.log(data);
                }
            })
        }
        else {
            // Do nothing !
            conmsole.log("Do Nothing with Toggle State")
        }
    }
}