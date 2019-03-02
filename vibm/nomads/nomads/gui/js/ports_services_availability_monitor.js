function appendTable4ServersAvailability( data ) {
  var ref = $("#myTable");
  //console.log(ref.val());

  //ref.append("<div><div class='small-border'><label></label></div>");
  //ref.append("<h1 class='ping-response'>"+msg+"</h1></div>");
  ref.append(
    '<table class="table table-dark table-striped table-bordered mt-3" id="my_table"> \
            <thead class="thead-light"> \
            <tr> \
                <th scope="col">IP</th> \
                <th scope="col">DNS</th> \
                <th scope="col">Bytes</th> \
                <th scope="col">TTL</th> \
                <th scope="col">Time</th> \
                <th scope="col">Min</th> \
                <th scope="col">Avg</th> \
                <th scope="col">Max</th> \
                <th scope="col">Transm</th> \
                <th scope="col">Recv</th> \
                <th scope="col">Loss</th> \
                <th scope="col">Status</th> \
            </tr> \
            </thead> \
            <tbody> \
                <tr scope="row"> \
                    <td>' + data["ip"] + '</td> \
                    <td>' + data["dns"] + '</td> \
                    <td>' + data["bytes"] + '</td> \
                    <td>' + data["ttl"] + '</td> \
                    <td>' + data["time_ms"] + '</td> \
                    <td>' + data["min"] + '</td> \
                    <td>' + data["avg"] + '</td> \
                    <td>' + data["max"] + '</td> \
                    <td>' + data["transmitted"] + '</td> \
                    <td>' + data["received"] + '</td> \
                    <td>' + data["loss"] + '</td> \
                    <td id="status" class="bg-danger"></td> \
                </tr> \
            </tbody> \
        </table>'
  )

  if ( data["status"] == 'UP!' ) {
    $("#my_table tr").find("td[id='status']").removeClass().addClass("bg-success");
  }

}

function callRobot4PingIP(ping_ip) {
  var robot_ip = $("#robot-ip").val();
  
  if (robot_ip == "local") {
    robot_ip = "http://127.0.0.1:5000/";
  } else if (robot_ip == "other") {
    robot_ip = $("#other-ip").val();
    //alert( robot_ip );
  } else {
    robot_ip = "http://" + robot_ip 
    robot_ip += ".dyndns.org:5000/";
  }
  
  url = robot_ip + "ping_ip_or_dns";
  console.log("Robot IP ... " + url);

  ping_ip = $("#ping-ip").val();
  //alert( ping_ip );
  console.log("Ping-IP is ..." + ping_ip);
  console.log(' href => ' + window.location.href);
  console.log(' host => ' + window.location.host);
  console.log(' hostname => ' + window.location.hostname);

  data = { "ping-ip": ping_ip }

  $.get( 
    url,
    data,
    function(data) {
      //if (data.toUpperCase() === "UP!") {
        // Host is Up - Ping OK 
        console.log( data["ip"] + " ... " + data["dns"] + " ... " + data["status"] );
        appendTable4ServersAvailability( data );
          //data["ip"] + ", " + data["dns"] + ", " + data["status"] + ": " + 
          //"bytes=" + data["bytes"] + ", icmp=" + data["icmp_seq"] + ", ttl=" + data["ttl"] + ", time_ms=" + data["time_ms"]);
      //}
    } 
  );
}

function onPingIP() {
  // Find the main-division and clear the current contents 
  // Use jquery framework ... 
  $("#header-availability").empty().text("External Monitoring of VLAB");
  
  var output = $("#myTable");
  output.empty();

  output.append(
    '<h6><span class="label label-info">Enter name of server to ping:</span></h6>');
  
  output.append(
    '<div class="input-group input-group-sm mb-2">\
      <input type="text" id="ping-ip" class="form-control" value="vlab1.dyndns.org">\
      <div class="input-group-append mb-4">\
        <button id="try-ping" class="btn btn-primary ml-1 mr-2">Try</button>\
        <input id="reset-ping" class="btn btn-danger" type="reset" value="Reset" disabled>\
      </div>\
    </div>');
  
  $( "#try-ping" ).click(function() {
    $("#try-ping").empty().text("OK!");
    $("#try-ping").addClass("btn-success");

    $("#reset-ping").removeAttr("disabled");

    callRobot4PingIP();
  });

  $( "#reset-ping" ).click( function() {
    $("#myTable").empty();
    $("#try-ping").text("Try");

    $("#ping-host").prop("checked", false);
  });
}


/*
Display Available Ports/ Services Over the Past XX Hours. 
*/
function display_open_ports() {
    if (monitoType.myValue == "None") {
      alert("Please Define Monitoring Type !");
    } else if (reportFreq.myValue == "None") {
      alert("Please Define Reports History !");
    }
  
    if (monitoType.myValue != "External") {
      alert("Only for External Monitoring Available !")
    }
  
    var conv=[{
      'type': 'external',
      'frequency': 'day',
      'entity': 'port'
    }];
  
    var s = JSON.stringify(conv);
    $.ajax({
      type: 'GET',
      contentType: 'application/json',
      data: s,
      dataType: 'json',
      url: 'http://127.0.0.1:5000/get_open_ports',
      success: function(e) {
        console.log(e);
      },
      error: function(error) {
        console.log(error);
      } 
    });
  }
  
/*
(function() {
    //d3.csv("gui/data/data.csv").then( function(data) {
    //    console.log( data[0] );

    var _data;
    d3.csv("gui/data/data.csv").then( function(data) {           
           //d3.select("#output").text(
           //     rows[0].Name + " " +
           //     rows[0].Surname + " " +
           //     "is " + rows[0].Age + " years old")
           console.log(data);

           columns = ["robot", "vlabID", "port", "service", "status"];

           //data[0] = ["miltos", "vimplis", "49"];
           //data[1] = ["kimonakos", "vimplis", "8"];

           var table = d3.select("#myTable").append("table");
           var thead = table.append("thead");
           var tbody = table.append("tbody");

           thead.append("tr").selectAll("th").data(columns).enter().append("th").text(
               function(column) {
                   return column
               }
           )
           .attr("class", "aClass")
           .style("color", "red");
           

           var rows = tbody.selectAll("tr")
                .data(data)
                .enter()
                .append("tr");

           var cells = rows.selectAll("td")
                .data( function(row) {
                    return columns.map( 
                        function(column) {
                            console.log(column);
                            return {column: column, value: row[column]};
                        });
                })
                .enter()
                .append("td")
                .text( function(d) {
                    return d.value;
                });
    });
       
    //d3.select("#output").text(_data[0].Age + " years old");
       //;
      //}).then( function(error, rows) {
      //    d3.select("#output")
      //        .text(
      //            rows[0].Name + " " +
      //            rows[0].Surname + " " +
      //            "is " + rows[0].Age + " years old")
      //});
}()); */