import serial
import cv2
import numpy as np
import  tensorflow as tf
from CocoLabels import get_label
from RedLightDetector import detect_red_light,verify_laser_visibility
from ESPTurret import send_command

# Initialize TFLite interpreter
interpreter = tf.lite.Interpreter(model_path='/home/noire/Downloads/lite-model_ssd_mobilenet_v1_1_metadata_2.tflite')#ssd_mobilenet_v1_1_default_1.tflite')
interpreter.allocate_tensors()

# Define a minimum confidence threshold
min_confidence = 0.4

# Generate 20 distinct colors using hue spectrum divided evenly
colors = []
for i in range(20):
    hue = int(255 * i / 20)
    col = np.uint8([[[hue, 255, 255]]])
    col_bgr = cv2.cvtColor(col, cv2.COLOR_HSV2BGR)[0][0]
    colors.append(tuple(map(int, col_bgr)))

# Use 'colors' as the color_map
color_map = {}
for i, color in enumerate(colors):
    color_map[i] = color

# Initialize Camera
cap = cv2.VideoCapture(0)

verify_laser_visibility(cap)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    input_image = cv2.resize(frame, (300, 300)).astype(np.uint8)

    # Inference
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    interpreter.set_tensor(input_details[0]['index'], [input_image])
    interpreter.invoke()
    Box_data = interpreter.get_tensor(output_details[0]['index'])
    classids = interpreter.get_tensor(output_details[1]['index'])[0]
    scores = interpreter.get_tensor(output_details[2]['index'])[0]
    #print(scores)
    # Extract bounding boxes
    boxes = Box_data[0, :, :4]

    
    # Draw bounding boxes
    max_area = 0
    selected_box = None
    for i, box in enumerate(boxes):
        if scores[i] >= min_confidence and classids[i] == 0:
            y1, x1, y2, x2 = box
            area = (x2 - x1) * (y2 - y1)
            if area > max_area:
                max_area = area
                selected_box = box

    if selected_box is not None:
            color = (0, 0, 255)  # Default to red
            y1, x1, y2, x2 = selected_box
            x1, y1, x2, y2 = int(x1*frame.shape[1]), int(y1*frame.shape[0]), int(x2*frame.shape[1]), int(y2*frame.shape[0])
            
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            scaled_center_x = int((center_x / frame.shape[1]) * 255)
            scaled_center_y = int((center_y / frame.shape[0]) * 255)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw a red point at the scaled center
            cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

            # Prepare byte array: 0x01, <scaled_center_x>, <scaled_center_y>, 0x00
            send_command(scaled_center_x, 255-scaled_center_y, 0,1)


            print(f"person score: {scores[i]:.2f} ")
    else:
        send_command(None,None,False)

    red_light_coords = detect_red_light(frame)
    
    if red_light_coords:
        x, y = red_light_coords
        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)  # Draw a green dot
    
    # Show frame with bounding boxes
    cv2.imshow('Frame', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and destroy all OpenCV windows
cap.release()
cv2.destroyAllWindows()
