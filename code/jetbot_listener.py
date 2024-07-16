from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

FLASK_SERVER_IP = '10.5.64.216'  # Replace with your computer's IP address
FLASK_SERVER_PORT = 5001  # Port where Flask server is running

# Global flag to indicate parking status
parking_completed = False

@app.route('/start_parking', methods=['POST'])
def start_parking_route():
    global parking_completed
    data = request.get_json()
    parking_number = data.get('parking_number')
    if parking_number is not None:
        print(f"Received start signal for parking number: {parking_number}")
        # Reset the parking completed flag
        parking_completed = False
        
        # Start the parking process (replace this comment with your actual parking logic)
        # For now, we'll simulate the parking process by waiting for the flag to be set to True
        while not parking_completed:
            pass  # Busy-wait for the flag to turn True
        
        # Send completion signal to Flask server
        response = requests.post(f'http://{FLASK_SERVER_IP}:{FLASK_SERVER_PORT}/parking_completed', json={"parking_number": parking_number})
        print(response.json())
        return jsonify({"status": "Parking process initiated"}), 200
    else:
        return jsonify({"error": "Invalid request"}), 400

@app.route('/set_parking_completed', methods=['POST'])
def set_parking_completed():
    global parking_completed
    parking_completed = True
    return jsonify({"status": "Parking completed flag set"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
