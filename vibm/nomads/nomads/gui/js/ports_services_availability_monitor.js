function onPingIP() {
  // Find the main-division and clear the current contents 
  // Use jquery framework ... 
  $(".header-availability").empty().text("Ping IP Request/ Response Preview Screen");
  
  var output = $("#myTable");
  
  output.empty();

  output.append('<p class="happy">Enter IP to ping:</p>');
  output.append('<input type="text" id="ip"><label for="ip">miltos</label></input>');
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
       /*;
      }).then( function(error, rows) {
          d3.select("#output")
              .text(
                  rows[0].Name + " " +
                  rows[0].Surname + " " +
                  "is " + rows[0].Age + " years old")
      });*/
}());