import machine
import sys

def set_servo_position(servo, value:float):
    # Convert the float value to PWM duty cycle for the servo
    # For a typical SG90 servo, 0% is around 40 (duty) and 100% is around 115 (duty)
    duty = int(value  * (115 - 40) + 40)
    servo.duty(duty)

def Run():
    # Define servos and laser pins
    servo_x = machine.PWM(machine.Pin(2), freq=50)  # Set frequency to 50Hz for servos
    servo_y = machine.PWM(machine.Pin(5), freq=50)
    laser = machine.PWM(machine.Pin(13))
    while True:
        data = input("Enter command: ")
        if data.startswith('move,'):
            _, x_val, y_val, laser_power = data.split(',')
            set_servo_position(servo_x, float(x_val))
            set_servo_position(servo_y, float(y_val))
            laser.duty(int(laser_power))  # Set PWM for laser; 0 to 255
            print("ok\n")
        if data.startswith('exit'):
            sys.exit()


if __name__ == "__main__":
    Run()