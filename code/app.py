from flask import Flask, request, jsonify
import os
import cv2
import time
from jetbot import Robot
from roboflow import Roboflow
import serial
import math
import Jetson.GPIO as GPIO
from smbus2 import SMBus
import requests
from AutoPark import AutoPark
from Peripherals import Peripherals

app = Flask(__name__)

FLASK_SERVER_IP = '10.5.64.216'  # Replace with your computer's IP address
FLASK_SERVER_PORT = 5000  # Port where Flask server is running

plate_number = None  # Initialize the plate number

@app.route('/start_parking', methods=['POST'])
def start_parking_route():
    global plate_number
    data = request.get_json()
    parking_number = data.get('parking_number')
    if parking_number is not None:
        plate_number = parking_number
        print(f"Received start signal for parking number: {parking_number}")
        # Start the parking process
        start_parking_process()
        return jsonify({"status": "Parking process initiated"}), 200
    else:
        return jsonify({"error": "Invalid request"}), 400

def start_parking_process():
    print("Button pressed! Starting JetBot script...")

    model_line = initRoboflow(
        api_key="MRlLd5ilY1jDBF1EnfMO", 
        project_id="line_segment-ye4yy", 
        version=1
    )
    model_number = initRoboflow(
        api_key="SKGyGb2otSlG9XCe3Lyj",
        project_id="number-detection-for-jetbot-64ztp",
        version=2
    )
    vid = setCamera()
    robot = Robot()
    Peripherals.setGPIO()
    bus, arduino_serial = setI2C()

    Peripherals.tcs34725_enable(bus)
    Peripherals.tcs34725_set_integration_time(bus, 0xD5)  # Integration time 101ms
    Peripherals.tcs34725_set_gain(bus, 0x00)  # Gain 1x

    # Phases
    position = False
    onPath = False
    parkStart = False

    # Left and Right Color Sensor Flags
    left_black = False
    right_black = False

    turns = 0
    index = 0

    start_time = time.time()

    while not position:
        ret, frame = vid.read()
        
        while ret is not True:
            continue

        if ret:
            cv2.imwrite(os.path.expanduser("~/jetson-inference/AutoParkProject/camera_capture.jpg"), frame)
            print("Image Captured")
        
        predicted_lines = []
        line_position = []
        x_lines = []
        y_lines = []
        
        current_time = time.time()        
        
        if current_time - start_time >= 0.5:
            line_prediction, image_line = AutoPark.line_det_model_usage(model_line, "~/jetson-inference/AutoParkProject/camera_capture.jpg")

            line_position, predicted_lines, x_lines, y_lines = AutoPark.slope_calculate_indegree(line_prediction)

            print(predicted_lines)
            print(line_position)
            print(x_lines)
            print(y_lines)
            
            if "black" not in predicted_lines:
                AutoPark.z_axis_turn(robot, 60)
                turns += 60

                # Faulty Logic Might Need Work
                if turns >= 300:
                    print("Going Back")
                    robot.backward(0.075)
                    turns = 0
                    start_time = time.time()
                    continue
                else:
                    robot.stop()

            else:
                print("black line detected")
                index = predicted_lines.index("black")
                print(index)
                    
                if line_position[index] <= 95 and line_position[index] >= 60:
                    # If already on black line
                    if line_position[index] <= 81 and line_position[index] >= 72:
                        onPath = True
                        position = True
                    else:
                        AutoPark.z_axis_turn(robot, 85 - line_position[index])
                        turns += abs(85 - line_position[index])
                            
                elif line_position[index] >= 5.5:
                    AutoPark.z_axis_turn(robot, line_position[index])

                    turns += line_position[index]
                else:
                    # Facing the line at 90 degrees
                    position = True
                
            start_time = time.time()

    print("Initialisation Complete")

    print("Start Getting On Path")

    while onPath is not True:
        try:
            white_1, _, _, _ = Peripherals.read_rgbc_sensor1(bus)

            arduino_data = Peripherals.read_rgbc_arduino(arduino_serial)
            white_2, _, _, _, _ = arduino_data
            white_2 /= 2

            if arduino_data is not None:
                left_white = Peripherals.is_white(white_1)
                right_white = Peripherals.is_white(white_2)

                if not left_white or not right_white:
                    robot.stop()
                    AutoPark.z_axis_turn(robot, 90)
                    onPath = True
                else:
                    robot.forward(0.08)
        except Exception as e:
            print(e)
            continue

    print("Getting On Path Completed")

    print("Start Road Following")

    distance = 0

    while onPath is True:
        try:
            white_1, _, _, _ = Peripherals.read_rgbc_sensor1(bus)

            arduino_data = Peripherals.read_rgbc_arduino(arduino_serial)
            white_2, _, _, _, distance = arduino_data
            white_2 /= 2

            if distance <= 75 and distance > 0:
                AutoPark.z_axis_turn(robot, 200)
                onPath = False

            if arduino_data is not None:
                left_white = Peripherals.is_white(white_1)
                right_white = Peripherals.is_white(white_2)

                if left_white and right_white:
                    robot.forward(0.1)  # Adjust speed as needed
                elif left_white and not right_white:
                    robot.right(0.09)  # Adjust speed and turning rate as needed
                elif not left_white and right_white:
                    robot.left(0.09)  # Adjust speed and turning rate as needed
                else:
                    robot.stop()
        except:
            print("exception")
            continue

    print("Stop Road Following")

    print("Start Getting to the First Row")

    start_time = time.time()

    while True:
        current_time = time.time()
        
        if current_time - start_time < 2.5:
            try:
                white_1, _, _, _ = Peripherals.read_rgbc_sensor1(bus)

                arduino_data = Peripherals.read_rgbc_arduino(arduino_serial)
                white_2, _, _, _, _ = arduino_data
                white_2 /= 2

                if arduino_data is not None:
                    left_white = Peripherals.is_white(white_1)
                    right_white = Peripherals.is_white(white_2)

                    if left_white and right_white:
                        robot.forward(0.1)  # Adjust speed as needed
                    elif left_white and not right_white:
                        robot.right(0.09)  # Adjust speed and turning rate as needed
                        current_time -= 0.5
                    elif not left_white and right_white:
                        robot.left(0.09)  # Adjust speed and turning rate as needed
                        current_time -= 0.5
                    else:
                        robot.stop()
            except:
                print("exception")
                continue
        else:
            break
                    
    print("Stop Getting to the First Row")

    AutoPark.z_axis_turn(robot, 90)

    index = 0

    i = 0

    find_parking_lot = False

    distance = 0

    position_to_parking_lot = True
    detect_parking_lot_number = True
    go_next_parking_lot = True
    readyToPark = False

    num_center = (0.0, 0.0)

    num_area = 0.0

    while i < 9 and find_parking_lot is False:
        move_forward = True

        start_time = time.time()

        print("Look at parking lot")

        while position_to_parking_lot is True:
            try:
                white_1, _, _, _ = Peripherals.read_rgbc_sensor1(bus)

                arduino_data = Peripherals.read_rgbc_arduino(arduino_serial)
                white_2, _, _, _, _ = arduino_data
                white_2 /= 2

                if arduino_data is not None:
                    left_white = Peripherals.is_white(white_1)
                    right_white = Peripherals.is_white(white_2)

                    if move_forward is True:
                        robot.forward(0.3)
                        current_time = time.time()
                        if current_time - start_time > 1.5:
                            robot.stop()
                            move_forward = False

                    if left_white and right_white:
                        robot.backward(0.1)  # Adjust speed as needed
                    elif left_white and not right_white:
                        robot.left(0.1)  # Adjust speed and turning rate as needed
                    elif not left_white and right_white:
                        robot.right(0.1)  # Adjust speed and turning rate as needed
                    else:
                        robot.stop()
                        break
            except Exception as e:
                print(e)
                continue

        start_time = time.time()

        turned = False

        print("Detect Parking Lot")

        while detect_parking_lot_number is True:
            ret, frame = vid.read()
            
            while ret is not True:
                continue

            if ret:
                cv2.imwrite(os.path.expanduser("~/jetson-inference/AutoParkProject/camera_capture.jpg"), frame)
                print("Image Captured")
                        
            predicted_numbers = []
            number_widths = []
            number_heights = []
            x_numbers = []
            y_numbers = []
                
            current_time = time.time()
            
            if current_time - start_time > 2.5:
                number_prediction, image_number, _ = AutoPark.num_det_model_usage(model_number, "~/jetson-inference/AutoParkProject/camera_capture.jpg")

                predicted_numbers, number_widths, number_heights, x_numbers, y_numbers = AutoPark.number_details(number_prediction)

                print(predicted_numbers)
                print(number_widths)
                print(number_heights)
                print(x_numbers)
                print(y_numbers)
                
                if plate_number in predicted_numbers:
                    index = predicted_numbers.index(plate_number)
                    print(abs(635 - x_numbers[index]))
                    if abs(635 - x_numbers[index]) >= 0 and abs(635 - x_numbers[index]) <= 250:
                        num_center = (x_numbers[index], y_numbers[index])
                        position_to_parking_lot = False
                        detect_parking_lot_number = False
                        go_next_parking_lot = False
                        find_parking_lot = True
                else:
                    print("Why not breaking?")

                start_time = time.time()
                break

        print("Turn Twat")
        if find_parking_lot is False:
            AutoPark.z_axis_turn(robot, -90)

        start_time = time.time()

        while go_next_parking_lot is True:
            try:
                white_1, _, _, _ = Peripherals.read_rgbc_sensor1(bus)

                arduino_data = Peripherals.read_rgbc_arduino(arduino_serial)
                white_2, _, _, _, distance = arduino_data
                white_2 /= 2

                if arduino_data is not None:
                    left_white = Peripherals.is_white(white_1)
                    right_white = Peripherals.is_white(white_2)

                    current_time = time.time()

                    # Move for 2 secs
                    if current_time - start_time < 2.5 and i is not 4:
                        if left_white and right_white:
                            robot.forward(0.1)  # Adjust speed as needed
                        elif left_white and not right_white:
                            robot.right(0.1)  # Adjust speed and turning rate as needed
                            current_time -= 0.8
                        elif not left_white and right_white:
                            robot.left(0.1)  # Adjust speed and turning rate as needed
                            current_time -= 0.8
                        else:
                            robot.stop()

                    elif i == 4:
                        if distance <= 75 and distance > 0:
                            robot.forward(0.1)  # Adjust speed as needed
                        else:
                            robot.stop()
                            AutoPark.z_axis_turn(robot, 180)
                            break
                    else:
                        AutoPark.z_axis_turn(robot, 90)
                        break
            except:
                print("exception")
                continue
        i += 1

        if i == 8:
            print("No parking lot available")

    start_time = time.time()

    print("----------------------------------------------------------------------------Start Parking----------------------------------------------------------------------------------------")

    start_capture_lot = True
    adjust_to_lot = False
    start_park = False
    x = 0.0

    # park situation = 0 ise düz git park et 
    ################ = -1 ise sağa ilerle
    ################ = 1 ise sola ilerle
    park_situation = 0

    while find_parking_lot is True:
        start_time = time.time()
        
        while start_capture_lot is True:
            ret, frame = vid.read()

            while ret is not True:
                continue

            if ret:
                cv2.imwrite(os.path.expanduser("~/jetson-inference/AutoParkProject/camera_capture.jpg"), frame)
                print("Image Captured")

            predicted_numbers = []
            x_numbers = []

            current_time = time.time()

            if current_time - start_time > 2.5:
                number_prediction, image_number, _ = AutoPark.num_det_model_usage(model_number, "~/jetson-inference/AutoParkProject/camera_capture.jpg")

                predicted_numbers, _, _, x_numbers, _ = AutoPark.number_details(number_prediction)

                print(predicted_numbers)
                print(x_numbers)
                
                
                if plate_number in predicted_numbers:
                    index = predicted_numbers.index(plate_number)
                    x = x_numbers[index]
                    # park situation = 0 ise düz git park et
                    ################ = -1 ise sağa ilerle
                    ################ = 1 ise sola ilerle
                    print(f"x value is: {x}")
                    difference = x - 670
                    # diference 0dan büyükse sağımda
                    # difference 0dan büyükse solumda
                    # park situation = 0 ise düz git park et
                    ################ = -1 ise sağa ilerle
                    ################ = 1 ise sola ilerle
                    if difference <= 150 or difference >= -150 :
                        park_situation = 0
                        start_capture_lot = False
                        print(f"Middle point of number is: {x}")
                        print(f"Difference is: {difference}")
                        print("Robot Should go Straight")
                    elif difference > 150 :
                        park_situation = -1
                        print(f"Middle point of number is: {x}")
                        print(f"Difference is: {difference}")
                        print("Robot Should go Right")
                    elif difference < -150 :
                        print(f"Middle point of number is: {x}")
                        print(f"Difference is: {difference}")
                        park_situation = 1
                        print("Robot Should go Left")
                    
                break

        while adjust_to_lot is False:
            try:
                white_1, _, _, _ = Peripherals.read_rgbc_sensor1(bus)
            
                arduino_data = Peripherals.read_rgbc_arduino(arduino_serial)
                white_2, _, _, _, _ = arduino_data
                white_2 /= 2

                if arduino_data is not None:
                    left_white = Peripherals.is_white(white_1)
                    right_white = Peripherals.is_white(white_2)

                    if park_situation == 0:
                        adjust_to_lot = True
                        start_park = True
                        print("Already Adjusted, Start Parking")
                        continue
                    elif park_situation == -1: # Turn Right
                        AutoPark.z_axis_turn(robot, -90)
                    elif park_situation == 1: # Turn Left
                        AutoPark.z_axis_turn(robot, 90)
        
                    current_time = time.time()

                    if current_time - start_time < 2.5:
                        if left_white and right_white:
                            robot.forward(0.1)
                            # Adjust speed as needed
                        elif left_white and not right_white:
                            robot.right(0.09)
                            # Adjust speed and turning rate as needed
                            current_time -= 0.8
                        elif not left_white and right_white:
                            robot.left(0.09)
                            # Adjust speed and turning rate as needed
                            current_time -= 0.8
                        else:
                            robot.stop()
                    else:
                        if park_situation == -1:
                            AutoPark.z_axis_turn(robot, 90)
                        elif park_situation == 1:
                            AutoPark.z_axis_turn(robot, -90)
                        break
            except:
                print("exception")
                continue
        while start_park is True:
            try:
                arduino_data = Peripherals.read_rgbc_arduino(arduino_serial)
                _, _, _, _, distance = arduino_data

                print(f'Distance: {distance}')

                if arduino_data is not None:
                    robot.forward(0.1)
                    if distance < 75 and distance > 0:
                        robot.stop()
                        start_park = False
                        find_parking_lot = False
                        # Send completion signal to Flask server
                        input_number =0
                        
                        response = requests.post(f'http://{FLASK_SERVER_IP}:{FLASK_SERVER_PORT}/parking_completed', json={"parking_number": input_number})
                        if input_number == 1:
                            plate_number = "one"
                        if input_number == 2:
                            plate_number = "two"
                        if input_number == 3:
                            plate_number = "three"
                        if input_number == 4:
                            plate_number = "four"
                        if input_number == 5:
                            plate_number = "five"
                        if input_number == 6:
                            plate_number = "six"
                        if input_number == 7:
                            plate_number = "seven"
                        if input_number == 8:
                            plate_number ="eight"
                        if input_number == 9:
                            plate_number = "nine"
                        if input_number == 10:
                            plate_number = "ten"

                        print(response.json())
            except Exception as e:
                print(e)
                continue

    GPIO.cleanup()  # Clean up GPIO at the end of the script

def initRoboflow(api_key, project_id, version):
    print("Checkpoint: Initializing Roboflow and Robot")
    
    # Initialise Roboflow Parameters
    rf = Roboflow(api_key)
    project = rf.workspace().project(project_id)
    model = project.version(version).model
    
    print("Checkpoint: Initialization complete")
    
    return model

def setCamera():
    gst_pipeline = (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), width=1280, height=720, format=(string)NV12, framerate=60/1 ! "
        "nvvidconv flip-method= 0 ! "
        "video/x-raw, width=1270, height=720, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
    )

    vid = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
    
    return vid

def setI2C():
    bus = SMBus(0) # Use I2C Bus 0
    arduino_serial = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    return bus, arduino_serial

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

