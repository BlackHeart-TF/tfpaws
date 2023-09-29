import machine
import sys
import _thread
from utime import sleep
from SmoothServo import SmoothServo
from collections import deque
buffer = ""
servo_x,servo_y = None,None
laser = None
exiting = False

def servoloop():
    global exiting
    while not exiting:
        servo_x.do_loop()
        servo_y.do_loop()
        sleep(0.02)

def read_commands():
    while True:
        command = sys.stdin.readline().strip()  # This will block, but only in this thread.
        if command:
            print("Received command:", command)
            # process command as necessary

def check_for_command():
    global buffer
    try:
        # This will raise an EOFError if there's nothing to read.
        char = sys.stdin.read(1)
        buffer += char

        if char in ['\n', '\r']:
            # Process command here
            command = buffer.strip()
            if command == "":
                print("OK")
                return
            print("Received command:", command)
            buffer = ""
            process_command(command)
    except EOFError:
        pass  # Nothing to read

def process_command(command:str):
    global servo_x
    global servo_y
    global laser
    global exiting
    print("process_command")
    if command is None:
            sleep(0.1)
            return
    if command.startswith('move,'):
        try:
            _, x_val, y_val, laser_power = command.split(',')
            servo_x.set_position(float(x_val))
            servo_y.set_position(float(y_val))
            laser.duty(int(laser_power))  # Set PWM for laser; 0 to 255
            print("ok\n")
        except ValueError:
            print(f"Invalid Parameters: {command}")
            pass
    if command.startswith('exit'):
        exiting = True
        sys.exit()

def Run():
    global servo_x
    global servo_y
    global laser
    # Define servos and laser pins
    servo_x = SmoothServo(2,fixed_step_size=0.02)  # Set frequency to 50Hz for servos
    servo_y = SmoothServo(5,fixed_step_size=0.02)
    laser = machine.PWM(machine.Pin(13))
    _thread.start_new_thread(servoloop, ())
    while True:
        command = sys.stdin.readline().strip() 
        process_command(command)
        


if __name__ == "__main__":
    Run()