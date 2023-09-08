import cv2
import numpy as np
import tensorflow as tf
from sort.sort import Sort  # Import the SORT tracker
from ESPTurret import send_command

# Initialize TFLite interpreter
interpreter = tf.lite.Interpreter(model_path='/home/noire/Downloads/lite-model_ssd_mobilenet_v1_1_metadata_2.tflite')
interpreter.allocate_tensors()

# Define a minimum confidence threshold
min_confidence = 0.4

# Initialize Camera
cap = cv2.VideoCapture(0)

# Initialize SORT tracker
tracker = Sort()

# Initialize variables for the focused object
focused_track_id = None

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    frame_height, frame_width, _ = frame.shape
    if not ret:
        break

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
        tracked_objects = tracker.update(np.array(valid_boxes))
    else:
        tracked_objects = []
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
        scaled_center_x = int((center_x / frame.shape[1]) * 255)
        scaled_center_y = int((center_y / frame.shape[0]) * 255)

        send_command(scaled_center_x, 255-scaled_center_y, 0,1)
    # Show frame with bounding boxes and tracking results
    cv2.imshow('Frame', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and destroy all OpenCV windows
cap.release()
cv2.destroyAllWindows()
