from flask import Flask, request, jsonify
from multiprocessing import Process, current_process  # Add this import statement
import logging
import json
import os

app = Flask(__name__)

# Use a configuration variable to store the server type
app.config['SERVER_TYPE'] = 'HTTP'  # Default to HTTP

last_received_coordinates = {"EMPTY": "EMPTY"}  # Initialize with a default value

@app.route('/', methods=['POST'])
def receive_coordinates():
    try:
        data = request.json  # Assuming data is in JSON format
        if data and all(key in data for key in ["degree", "yCoordinate"]):
            # Update global variable with latest coordinates
            global last_received_coordinates
            last_received_coordinates = {"degree": data["degree"], "yCoordinate": data["yCoordinate"]}

            # Optionally, save the data to a file for reference
            with open('last_received_coordinates.json', 'w') as file:
                json.dump(last_received_coordinates, file)
    except Exception as e:
        logging.error("Error: %s", str(e))
    return 'OK'

@app.route('/coordinates', methods=['GET'])
def get_coordinates():
    try:
        # Check the server type
        server_type = app.config.get('SERVER_TYPE', 'HTTP')

        if server_type == 'HTTP':
            # If HTTP, read coordinates from the file
            with open('last_received_coordinates.json', 'r') as file:
                last_received_coordinates = json.load(file)

            # Extract individual coordinates
            degree = last_received_coordinates.get("degree", 0)
            y_coordinate = last_received_coordinates.get("yCoordinate", 0)

            # Use y_coordinate as motorSpeed
            motor_speed = int(y_coordinate)
        else:
            # If HTTPS, use the global variable
            degree = last_received_coordinates.get("degree", 0)
            y_coordinate = last_received_coordinates.get("yCoordinate", 0)

            # Use y_coordinate as motorSpeed
            motor_speed = int(y_coordinate)

        # Create a JSON array response
        response = {"degree": degree, "motorSpeed": motor_speed}

        return jsonify(response)
    except Exception as e:
        logging.error("Error: %s", str(e))
        # Return a default response if an error occurs
        return jsonify({"degree": 0, "motorSpeed": 0})

@app.route('/status', methods=['GET'])
def get_status():
    return 'OK'

def run_app(port, use_ssl=False):
    # Set up logging
    logging.basicConfig(filename='app.log', level=logging.DEBUG)

    if use_ssl:
        context = ('C:/Certbot/live/p1.nimx.me/fullchain.pem', 'C:\Certbot\live\p1.nimx.me/privkey.pem')
    else:
        context = None

    # Set the server type based on the process name
    app.config['SERVER_TYPE'] = 'HTTPS' if 'https_process' in current_process().name else 'HTTP'

    @app.before_request
    def log_request_info():
        logging.debug('Headers: %s', request.headers)
        logging.debug('Body: %s', request.get_data())

    app.run(host='0.0.0.0', port=port, ssl_context=context, debug=False, threaded=True)

if __name__ == "__main__":
    # Start a process for the HTTPS server
    https_process = Process(target=run_app, kwargs={'port': 5000, 'use_ssl': True})
    https_process.name = 'https_process'
    https_process.start()

    # Start a process for the HTTP server
    http_process = Process(target=run_app, kwargs={'port': 5001, 'use_ssl': False})
    http_process.name = 'http_process'
    http_process.start()

    # Join the processes
    https_process.join()
    http_process.join()
