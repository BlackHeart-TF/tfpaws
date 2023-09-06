import cv2
import numpy as np
import time
from ESPTurret import send_command

def detect_red_light(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red = np.array([160, 100, 100])
    upper_red = np.array([180, 255, 255])
    mask = cv2.inRange(hsv, lower_red, upper_red)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=cv2.contourArea) if contours else None

    if largest_contour is not None:
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            return cX, cY
    return None

def verify_laser_visibility(cap):
    # Capture first frame
    ret, frame1 = cap.read()
    if not ret:
        return False
    hsv1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV)

    # Turn on laser
    send_command(127, 127, 0)
    time.sleep(2)
    send_command(127, 127, 254)
    time.sleep(0.5)
    # Capture second frame
    ret, frame2 = cap.read()
    if not ret:
        return False
    hsv2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV)
    time.sleep(0.5)
    # Turn off laser for safety
    send_command(None, None, 0)

    
    # Compute the difference
    diff = cv2.absdiff(hsv1, hsv2)

    # Create a mask for red color
    lower_red = np.array([160, 100, 100])
    upper_red = np.array([180, 255, 255])
    mask = cv2.inRange(diff, lower_red, upper_red)

    # Count non-zero pixels in the mask
    count = cv2.countNonZero(mask)
    cv2.imshow('Mask', diff)
    # If the count is above a threshold, the laser is visible
    return count > 1000

