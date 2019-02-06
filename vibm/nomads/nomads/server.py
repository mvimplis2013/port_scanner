from flask import Flask

app = Flask( __name__ )

@app.cli.command()
def deploy():
 pass

@app.route('/')
def index():
    return '<h1>Hello World!</h1>'

@app.route('/user/<name>')
def user(name):
    return '<h1>Hello {}!</h1>'.format(name)

@app.route('/reconfigure', methods=['POST'])
def reconfigure_robot():
    print("Received configure-again request")
    return 404
