from flask import Flask, render_template, request, jsonify
import os

from nomads.utils import ping_host, ping_host_full_response, scan_vlab_open_ports_now

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

    simple_ping = ping_host(ip).upper()
    print("Server Simple Ping -> %s" % simple_ping )

    if (  simple_ping.upper() == "UP!" ):
        data = ping_host_full_response(ip)
    else:
        data = {}

    data["status"] = simple_ping

    return jsonify( data )

@app.route('/scan-ports', methods=['GET'])
def scan_ports():
    vlab_target = request.args.get("vlab-target")

    #return scan_vlab_open_ports_now( vlab_target )

    response = [{ 
        "Port": "22/tcp", "State": "open", "Service":"ssh"}, { 
        "Port": "443/tcp", "State": "open", "Service": "https"}, { 
        "Port": "5555/tcp", "State": "open", "Service": "freeciv"}]

    return jsonify(response)

@app.route('/alarms-outages-nodes', methods=['GET'])
def get_alarms_outages_nodes_graphs():
    return render_template("alarms_outages_nodes.html")