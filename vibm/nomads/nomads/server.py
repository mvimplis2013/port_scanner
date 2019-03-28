from flask import Flask, render_template, request, jsonify, Response, json
import os

from nomads.utils import ping_host, ping_host_full_response, scan_vlab_open_ports_now
from nomads.backend.utils.back_logger import nomads_logger

from nomads.config_data_taxi import ConfigDataTaxi

try: 
    from ..backend.datastore.database_manager import DatabaseManager
except (ImportError, ValueError):
    from nomads.backend.datastore.database_manager import DatabaseManager

try: 
    from ..backend.datastore.ping_response_table import PingResponseTable
except: 
    from nomads.backend.datastore.ping_response_table import PingResponseTable

from datetime import datetime, timedelta 

project_root = os.path.dirname(__file__)
template_path = os.path.join(project_root, "templates")
static_path = os.path.join(project_root, "gui")

app = Flask( __name__, template_folder=template_path, static_folder=static_path)

@app.cli.command()
def deploy():
 pass

@app.route('/')
def index():
    """ return '<h1>Hello World!</h1>' """
    """ return render_template("index2.html") """
    return render_template("index.html")

@app.route('/user/<name>')
def user(name):
    return '<h1>Hello {}!</h1>'.format(name)

@app.route('/reconfigure', methods=['POST'])
def reconfigure_robot():
    return "404"

@app.route('/get_open_ports', methods=['GET'])
def get_ports():
    return "123"

@app.route('/ping_ip_or_dns', methods=['GET'])
def ping_ip_or_dns():
    ip = request.args.get("ping-ip")
    #print("!!! WELCOME ROBERT BERGER ING ... YOU JUST SEND ME A PING REQUEST FOR VLAB ... %s" % ip)
    
    simple_ping = ping_host(ip).upper()
    #print("Server Simple Ping -> %s" % simple_ping )

    if (  simple_ping.upper() == "UP!" ):
        data = ping_host_full_response(ip)
    else:
        data = {}

    data["status"] = simple_ping

    return jsonify( data )

@app.route('/scan-ports', methods=['GET'])
def scan_ports():
    vlab_target = request.args.get("vlab-target")

    response = scan_vlab_open_ports_now( vlab_target )

    #response = [{ 
    #    "Port": "22/tcp", "State": "open", "Service":"ssh"}, { 
    #    "Port": "443/tcp", "State": "open", "Service": "https"}, { 
    #    "Port": "5555/tcp", "State": "open", "Service": "freeciv"}]

    #print( "--> %s" % response["open-ports"])
    #return jsonify( response["open-ports"] )
    return jsonify( response )
    
@app.route('/alarms-outages-nodes', methods=['GET'])
def get_alarms_outages_nodes_graphs():
    return render_template("alarms_outages_nodes.html")

@app.route('/admin/edit_config', methods=['GET', 'POST'])
def edit_monitoring_configuration():
    return render_template("edit_config.html")

@app.route('/admin/post_new_config_data', methods=['POST'])
def handle_new_config_data():
    new_ips = request.get_json().get("new-ips")
    new_names = request.get_json().get("new-names")
    new_range = request.get_json().get("new-range")

    print( "new-ips = %s ... new-names = %s ... new-range = %s" % (new_ips, new_names, new_range) )

    taxi = ConfigDataTaxi( new_ips, new_names, new_range )
    taxi.take_new_data_to_store()
    
    print("Message Received from Capital")
    return "123"

""" 
***********************************
 Get VLAB IP-Ping & Port-Scan Data 
***********************************
"""
@app.route('/reports/external/get-ip-data', methods=['GET'])
def get_ip_data_for_period():
    print("**** Inside Get-IP-Data on Server ***")

    time_range = request.args.get("time-range")
    #time_range = request.get_json().get("time-range")

    print("Client Requested Time Range is: %s" % time_range)

    [_from, _to] = translate_time_ranges( time_range )

    if _from is None:
        # Select all records from database ping-responses
        ping_responses = collect_all_ping_records()
    else:
        ping_responses = collect_ping_records_for_period(_from, _to)

    return ping_responses

@app.route('/reports/external/get-ip-and-port-data', methods=['GET'])
def get_ip_and_port_data_for_period():
    print("**** Inside Get-PORT-Data on Server ***")
    return "PORT"

@app.route('/reports/external/charts_collection', methods=['GET'])
def display_available_graphs():
    return render_template("base.html")

"""
Internal server function that translates the UI time-ranges into date-times appropriate for SQL queries.
"""
def translate_time_ranges( time_range ):
    _to = datetime.now()
        
    if 'all' in time_range.lower():
        # Return ALL stored records
        print("I will the MAXIMUM time window .. All records returned")
        _from = None
    elif 'one hour' in time_range.lower():
        # One(1) Hour
        _from = _to - timedelta(hours=1, minutes=0)
    else: 
        # Default time window
        print("I will use the DEFAULT time window ... 12 Hours Back !")
        _from = _to - timedelta(hours=12, minutes=0)

    return [_from, _to]

"""
 Internal server function that queries datastore for all available data that fits a specific time window
"""
def collect_ping_records_for_period( _from, _to ):
    print("+++ Inside Collect Ping Data +++")

    #db_manager = DatabaseManager()
    #db_manager.establish_connection() 

    #response_table = PingResponseTable( db_manager._connection )
    records_found = PingResponseTable.collect_data_for_period( _from, _to )

    print("+++ Finished Collecting Ping Data +++")
    
    #db_manager.close_connection()

    return records_found

def collect_all_ping_records():
    nomads_logger.debug("+++ Inside Collect ALL Ping Data +++")

    records_found = PingResponseTable.get_all_records()

    for i in range(6):
        nomads_logger.debug( records_found[i] )

    nomads_logger.debug("+++ Finished Collecting ALL Ping Data +++")
    
    return jsonify( records_found )
    #return Response( json.dumps( records_found ), mimetype="application/json")
