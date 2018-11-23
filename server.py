from flask import Flask, request
from lights import set_lights

app = Flask(__name__, static_folder='', static_url_path='')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/set', methods=['POST'])
def set():
    set_lights(request.form['mode'], float(request.form['interval']))
    return 'Lights set to {}: {}s'.format(request.form['mode'], request.form['interval'])