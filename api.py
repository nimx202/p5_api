from flask import Flask, request, jsonify
from multiprocessing import Process, current_process
import logging
import json
import os

app = Flask(__name__)

app.config['SERVER_TYPE'] = 'HTTP'

last_received_coordinates = {"EMPTY": "EMPTY"}

@app.route('/', methods=['POST'])
def receive_coordinates():
    try:
        data = request.json
        if data and all(key in data for key in ["degree", "yCoordinate"]):
            global last_received_coordinates
            last_received_coordinates = {"degree": data["degree"], "yCoordinate": data["yCoordinate"]}
            with open('last_received_coordinates.json', 'w') as file:
                json.dump(last_received_coordinates, file)
    except Exception as e:
        logging.error("Error: %s", str(e))
    return 'OK'

@app.route('/coordinates', methods=['GET'])
def get_coordinates():
    try:
        server_type = app.config.get('SERVER_TYPE', 'HTTP')
        if server_type == 'HTTP':
            with open('last_received_coordinates.json', 'r') as file:
                last_received_coordinates = json.load(file)
            degree = int(round(last_received_coordinates.get("degree", 0)))
            y_coordinate = int(round(last_received_coordinates.get("yCoordinate", 0)))
            motor_speed = y_coordinate
        else:
            degree = int(round(last_received_coordinates.get("degree", 0)))
            y_coordinate = int(round(last_received_coordinates.get("motorSpeed", 0)))
            motor_speed = y_coordinate
        response = {"degree": degree, "motorSpeed": motor_speed}
        return jsonify(response)
    except Exception as e:
        logging.error("Error: %s", str(e))
        return jsonify({"degree": 0, "motorSpeed": 0})

@app.route('/status', methods=['GET'])
def get_status():
    return 'OK'

def run_app(port, use_ssl=False):
    logging.basicConfig(filename='app.log', level=logging.DEBUG)
    if use_ssl:
        context = ('C:/Certbot/live/p1.nimx.me/fullchain.pem', 'C:\Certbot\live\p1.nimx.me/privkey.pem')
    else:
        context = None
    app.config['SERVER_TYPE'] = 'HTTPS' if 'https_process' in current_process().name else 'HTTP'
    @app.before_request
    def log_request_info():
        logging.debug('Headers: %s', request.headers)
        logging.debug('Body: %s', request.get_data())
    app.run(host='0.0.0.0', port=port, ssl_context=context, debug=False, threaded=True)

if __name__ == "__main__":
    https_process = Process(target=run_app, kwargs={'port': 5000, 'use_ssl': True})
    https_process.name = 'https_process'
    https_process.start()
    http_process = Process(target=run_app, kwargs={'port': 5001, 'use_ssl': False})
    http_process.name = 'http_process'
    http_process.start()
    https_process.join()
    http_process.join()
