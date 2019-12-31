function render_results_table() {
    var ref = $("#myTable");

    ref.append(//'<div id="table-ports" class="container"> \
        '<table class="table table-dark table-striped table-bordered" id="my_table"> \
            <thead class="thead-light"> \
            <tr> \
                <th scope="col">Port</th> \
                <th scope="col">State</th> \
                <th scope="col">Service</th> \
            </tr> \
            </thead> \
            <tbody> \
                <tr scope="row"> \
                    <td>Default</td> \
                    <td>Default</td> \
                    <td>Default</td> \
                </tr> \
            </tbody> \
        </table>' //  \</div>'
        );
}

function onScanPorts() {
    $("#header-availability").empty().text("External Monitoring for Open Ports");
  
    var output = $("#myTable");
    output.empty();

    output.append("<p class='happy'>Select VLAB for Scanning:</p>");
    
    output.append(
        '<div class="input-group input-group-sm mb-2">\
            <input type="text" id="vlab-target" class="form-control" value="vlab1.dyndns.org">\
            <div class="input-group-append">\
                <button id="try" class="btn btn-primary">Try</button>\
            </div>\
        </div>');  

    $( "#try" ).click( function() {
        $("#try").empty().text("OK!");
        $("#try").addClass("btn-success")
        
        callRobot4PortScan();
    }); 
}

function callRobot4PortScan() {
    var robot_ip = $("#robot-ip").val();
  
    if (robot_ip == "local") {
        robot_ip = "http://127.0.0.1:5000/";
    } else {
        robot_ip = "http://" + robot_ip 
        robot_ip += ".dyndns.org:5000/";
    }
  
    url = robot_ip + "scan-ports";
    
    console.log( url );

    vlab_target = $("#vlab-target").val();
    data = { "vlab-target": vlab_target }

    $.ajax(
        {
            async: false,
            type: 'GET', 
            url,
            data,
            success: function( data ) {
                render_results_table();

                //response = $.parseJSON(data);
                console.log( data );
                
                $(function() {
                    $.each(data, function(i, item) {
                        console.log(i + " --> " + item.Port + ", " + item.State + ", " + item.Service);
                        
                        $("#my_table > tbody").append( 
                            '<tr>' + 
                                '<td>' + item.Port + '</td>' +  
                                '<td>' + item.State + '</td>' +
                                '<td>' + item.Service + '</td>' +
                            '</tr>');
                    })
                })
            }
        }
    );
}
