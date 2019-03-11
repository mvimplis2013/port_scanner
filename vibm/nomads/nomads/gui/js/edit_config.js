num_ips_add = 0;
num_names_add = 0;

arr_num = ["one", "two", "three"];

// CONSTANTS
EMPTY = "...";
MAX_NUM_ROWS = 3;

ROBOT_IP = "http://" + location.hostname + ":5000/";

RPC_NEW_CONFIG = "admin/post_new_config_data";

// **** Save New IP *** 
$("#btn-ip-save").on("click", function(event) {
    //find("td[id='status']").removeClass().addClass("bg-success");
    which_ip = $( "#new-ip" ).val();

    $( "#tbl-ips #ip-" + arr_num[num_ips_add] ).text( which_ip );

    num_ips_add += 1;
});

// *** Save New Name ***
$("#btn-name-save").on("click", function(event) {
    //find("td[id='status']").removeClass().addClass("bg-success");
    which_name = $( "#new-name" ).val();

    $( "#tbl-names #ip-" + arr_num[num_names_add] ).text( which_name );

    num_names_add += 1;
});

// *** Post New IPs to Server *** 
function callRobot4SpecificIPs( arr_ips, arr_names ) {
    // Which Server 
    var robot_ip = ROBOT_IP;
    
    // Which Remote Function 
    my_url = robot_ip + RPC_NEW_CONFIG;
    console.log("Robot IP ... " + my_url);
    console.log("location = " + location.hostname);
  
    my_data = JSON.stringify({ 
        "new-ips": arr_ips,
        "new-names": arr_names
    });

    console.log( "Data is .. " + my_data );
  
    $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",  
        url: my_url,
        data: my_data,
        success: function(data) {
            //if (data.toUpperCase() === "UP!") {
            // Host is Up - Ping OK 
            console.log( data );
            //appendTable4ServersAvailability( data );
            //data["ip"] + ", " + data["dns"] + ", " + data["status"] + ": " + 
            //"bytes=" + data["bytes"] + ", icmp=" + data["icmp_seq"] + ", ttl=" + data["ttl"] + ", time_ms=" + data["time_ms"]);
        //}
        }, 
        dataType: "json"
    });
}
  
// **************************************
// *** POST ALL CONFIG DATA TO SERVER ***
// **************************************
$("#btn-send-to-server").on("click", function(event) {
    //alert("Hello");
    
    // --> Check Table IPs
    arr_ips = [];
    for (i=0; i<MAX_NUM_ROWS; i++) {
        // * Read the Requested IPs
        
        //console.log("Help.." + i);
        
        new_ip = $( "#tbl-ips #ip-" + arr_num[i] ).text();
        
        if ( new_ip !== "..." ) {
            arr_ips.push( new_ip );
        }
    }

    // console.log( arr_ips );

    // --> Check Table Names
    arr_names = [];
    for (i=0; i<MAX_NUM_ROWS; i++) {
        // * Read the Requested Names
        
        //console.log("Help.." + i);
        
        new_name = $( "#tbl-names #ip-" + arr_num[i] ).text(); 
        
        if ( new_name !== "..." ) { 
            arr_names.push( new_name );     
        }   
    }

    callRobot4SpecificIPs( arr_ips, arr_names );
});
