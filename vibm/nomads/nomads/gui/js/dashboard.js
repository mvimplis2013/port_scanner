function hide() {
    alert("Hello World 2");
}

function list_all_vms() {
  entitiesL.innerText = "List of VMs:";
  $("entitiesL").css(
    "text-decoration", "underline"
  );

  var canvas = document.querySelector("canvas");
  var context = canvas.getContext("2d");
}

function list_all_services() {
  alert("Services Manager Ready !");
}

function play_external_monitoring() {
  alert("External Monitoring Client Ready !");
}

function configure_robot() {
  var conv=[{
    'input': 'hi',
    'topic': 'Greeting'
  }];

  var s = JSON.stringify(conv);

  $.ajax({
    type: 'POST',
    contentType: 'application/json',
    data: s,
    dataType: 'json',
    url: 'http://127.0.0.1:5000/reconfigure',
    success: function(e) {
      console.log(e);
    },
    error: function(error) {
      console.log(error);
    } 
  });
  
  robotResponse.value = "Re-Configuration Successful";
  
  robotResponse.style.color='green';
  robotResponse.style.fontSize="20px";
}

(function () {
    'use strict'
  
    feather.replace()
  
    // Graphs
    var ctx = document.getElementById('myChart')
    // eslint-disable-next-line no-unused-vars
    var myChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: [
          'Sunday',
          'Monday',
          'Tuesday',
          'Wednesday',
          'Thursday',
          'Friday',
          'Saturday'
        ],
        datasets: [{
          data: [
            15339,
            21345,
            18483,
            24003,
            23489,
            24092,
            12034
          ],
          lineTension: 0,
          backgroundColor: 'transparent',
          borderColor: '#007bff',
          borderWidth: 4,
          pointBackgroundColor: '#007bff'
        }]
      },
      options: {
        scales: {
          yAxes: [{
            ticks: {
              beginAtZero: false
            }
          }]
        },
        legend: {
          display: false
        }
      }
    })
  }())