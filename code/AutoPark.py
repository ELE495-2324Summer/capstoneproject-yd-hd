import time
import os
import math
from roboflow import Roboflow

class AutoPark:
    def z_axis_turn(robot, angle_degrees):
        print("Checkpoint: Starting z_axis_turn")
        rotation_time360 = 5
        speed = 0.1
        rotation_time = (abs(angle_degrees) / 360) * rotation_time360

        if angle_degrees > 0:
            robot.left_motor.value = -speed
            robot.right_motor.value = speed
        else:
            robot.left_motor.value = speed
            robot.right_motor.value = -speed 
            
        time.sleep(rotation_time)
        robot.stop()
        print("Checkpoint: Finished z_axis_turn")

    def line_det_model_usage(model, image_path):
        print("Checkpoint: Starting line_det_model_usage")
        
        expanded_image_path = os.path.expanduser(image_path)
        predictions = model.predict(expanded_image_path, confidence=30)
        predictions.save("prediction_line.jpg")
        predictions = predictions.json()["predictions"]
        
        image = "prediction_line.jpg"
        
        print("Checkpoint: Finished line_det_model_usage")
        
        return predictions, image
    
    def num_det_model_usage(model, image_path):
        print("Checkpoint: Starting num_det_model_usage")
        
        start_time = time.time()
        expanded_image_path = os.path.expanduser(image_path)
        predictions = model.predict(expanded_image_path, confidence=50, overlap=30)
        end_time = time.time()
        elapsed_time = end_time - start_time

        predictions.save("prediction_number.jpg")
        predictions = predictions.json()["predictions"]
        
        image = "prediction_number.jpg"
        
        print(f"Model tahmin süresi: {elapsed_time:.2f} saniye")
        print("Checkpoint: Finished num_det_model_usage")
        
        return predictions, image, elapsed_time

    def slope_calculate_indegree(line_prediction):
        print("Checkpoint: Starting slope_calculate_indegree")
        
        labels = []
        slopes = []
        x_lines = []
        y_lines = []
        
        for prediction in line_prediction:
            if "points" in prediction:
                points = prediction["points"]
                
                x_coordinates = [point["x"] for point in points]
                y_coordinates = [point["y"] for point in points]
                
                if x_coordinates and y_coordinates:
                    x_max = max(x_coordinates)
                    y_max = max(y_coordinates)
                    x_min = min(x_coordinates)
                    y_min = min(y_coordinates)
                    
                    slope = math.atan2((y_max - y_min), (x_max - x_min)) * 180 / math.pi
                    
                    labels.append(prediction.get("class", "unknown"))
                    slopes.append(slope)
                    x_lines.append(prediction["x"])
                    y_lines.append(prediction["y"])
        
        print("Checkpoint: Finished slope_calculate_indegree")
        
        return slopes, labels, x_lines, y_lines
    
    def number_details(number_prediction):
        print("Checkpoint: Starting number_details")

        labels = []
        width_numbers = []
        height_numbers = []
        x_numbers = []
        y_numbers = []
        
        for prediction in number_prediction:
            labels.append(prediction.get("class", "unknown"))
            width_numbers.append(prediction["width"])
            height_numbers.append(prediction["height"])
            x_numbers.append(prediction["x"])
            y_numbers.append(prediction["y"])
            
        print("Checkpoint: Finished number_details")
        
        return labels, width_numbers, height_numbers, x_numbers, y_numbers
    
    def line_center_get(line_prediction):
        center_x = []
        center_y = []
        for prediction in line_prediction:
            center_x.append(prediction["x"])
            center_y.append(prediction["y"])
        return center_x, center_y
    
    def find_nearest_two_lines(xin, yin, center_point):
        points_with_index = [(i, (x, y)) for i, (x, y) in enumerate(zip(xin, yin))]
        points_with_index.sort(key=lambda point: AutoPark.compute_distance(point[1], center_point))
        
        nearest_two_points = [point[1] for point in points_with_index[:2]]
        indexes = [point[0] for point in points_with_index[:2]]
        
        return nearest_two_points, indexes
    
    def find_xy_doubles(line_prediction):
        x_coordinates = []
        y_coordinates = []
        
        for prediction in line_prediction:
            if "points" in prediction:
                points = prediction["points"]
                x_coordinates.append([point["x"] for point in points])
                y_coordinates.append([point["y"] for point in points])
        
        return x_coordinates, y_coordinates
    
    def find_max_inlist(lst):
        y_max = max(lst)
        indx = lst.index(y_max)
        return y_max, indx
    
    def compute_distance(point, center):
        return math.sqrt((point[0] - center[0])**2 + (point[1] - center[1])**2)
    
    def angle_to_midpoint(midpoint_x, midpoint_y, reference_point):
        angle = math.atan2((reference_point[1] - midpoint_y), (midpoint_x - reference_point[0]))
        return angle
