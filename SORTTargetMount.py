import cv2
import numpy as np
import tensorflow as tf
from sort.sort import Sort  # Import the SORT tracker
from ESPTurret import send_command
from time import sleep

send_command(0.5,0.01,0)
# Initialize TFLite interpreter
interpreter = tf.lite.Interpreter(model_path='/home/noire/Downloads/lite-model_ssd_mobilenet_v1_1_metadata_2.tflite')
interpreter.allocate_tensors()

# Define a minimum confidence threshold
min_confidence = 0.4
# Proportional control constants
KP_X = 0.00025
KP_Y = 0.00025

# Initialize Camera
cap = cv2.VideoCapture("http://192.168.2.130:81/stream")

if not cap.isOpened():
    print("Error: Couldn't open the MJPEG stream.")
    exit()

# Initialize SORT tracker
tracker = Sort()

# Initialize variables for the focused object
focused_track_id = None
ret, frame = cap.read()
frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
frame_height, frame_width, _ = frame.shape
FRAME_CENTER_Y = frame_height/2
FRAME_CENTER_X = frame_width /2
current_servo_x = 0.1  # Initial servo position in the range [0, 1]
current_servo_y = 0.5  # Initial servo position in the range [0, 1]
noPeoplePasses = 0
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    # Inference
    input_image = cv2.resize(frame, (300, 300)).astype(np.uint8)
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    interpreter.set_tensor(input_details[0]['index'], [input_image])
    interpreter.invoke()
    Box_data = interpreter.get_tensor(output_details[0]['index'])
    classids = interpreter.get_tensor(output_details[1]['index'])[0]
    scores = interpreter.get_tensor(output_details[2]['index'])[0]

    # Extract bounding boxes
    boxes = Box_data[0, :, :4]

    # Initialize a list to store valid detection boxes
    valid_boxes = []
    blue = (255, 0, 0)
    red = (0, 0, 255)
    # Iterate through bounding boxes and filter by confidence score
    for i, box in enumerate(boxes):
        if scores[i] >= min_confidence and classids[i] == 0:  # Class 0 corresponds to "person"
            valid_boxes.append(box)
            y1, x1, y2, x2 = box
            #print(f"1 x1: {x1}, x2: {x2}, y1: {y1}, y2: {y2}")
            x1, y1, x2, y2 = int(x1*frame_width), int(y1*frame_height), int(x2*frame_width), int(y2*frame_height)
            cv2.rectangle(frame, (x1, y1), (x2, y2), blue, 2)
    #print("Valid Boxes:", len(valid_boxes))
    # Perform tracking with SORT
    if valid_boxes:
        noPeoplePasses = 0
        tracked_objects = tracker.update(np.array(valid_boxes))
    else:
        noPeoplePasses += 1
        tracked_objects = []
        if(noPeoplePasses == 3):
            tracker = Sort()

    #print("Tracked Objects:", tracked_objects)

    # Focus on the largest tracked object
    if len(tracked_objects) > 0:
        focused_object = None  # Initialize focused object as None

        if focused_track_id is not None:
            # Check if the focused_track_id is present in the list of tracked objects
            for obj in tracked_objects:
                if obj[4] == focused_track_id:
                    # The focused_track_id is present in the list of tracked objects
                    focused_object = obj
                    #print("The focused object is being tracked.")
                    break  # Exit the loop once the focused object is found
        if focused_object is None:
            focused_object = max(tracked_objects, key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))
        
        y1, x1, y2, x2, track_id = focused_object
        #print(f"2 x1: {x1}, x2: {x2}, y1: {y1}, y2: {y2}")
        focused_track_id = track_id

        # Visualize the tracking results for the focused object
        x1, y1, x2, y2 = map(int, [x1 * frame_width, y1 * frame_height, x2 * frame_width , y2 * frame_height])
        #print(f"3 x1: {x1}, x2: {x2}, y1: {y1}, y2: {y2}")
        cv2.rectangle(frame, (x1, y1), (x2, y2), red, 2)
        cv2.putText(frame, str(focused_track_id), (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, red, 2)
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        error_x = -(FRAME_CENTER_X - center_x)
        error_y = -(FRAME_CENTER_Y - center_y)
        print(f"error: {error_x} {error_y}")
        servo_movement_x = KP_X * error_x
        servo_movement_y = KP_Y * error_y
        print(f"movement: {servo_movement_x} {servo_movement_y}")
        current_servo_x = min(max(current_servo_x - servo_movement_x, 0), 1)
        current_servo_y = min(max(current_servo_y - servo_movement_y, 0), 1)

        # Send the adjusted absolute values to your device
        print(f"current: {current_servo_x} {current_servo_y}")
        send_command(1-current_servo_x,current_servo_y, 0)
    
    # Show frame with bounding boxes and tracking results
    cv2.imshow('Frame', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and destroy all OpenCV windows
cap.release()
cv2.destroyAllWindows()
