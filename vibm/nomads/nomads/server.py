from flask import Flask, render_template
import os

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
