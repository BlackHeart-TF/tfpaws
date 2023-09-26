import collections
import machine
import utime
from uQue import uQue

class SmoothServo:
    def __init__(self, pin, maxlen=3, fixed_step_size=0.05, timeout_ms=10000):
        self.servo = machine.PWM(machine.Pin(pin), freq=50)
        self.history = uQue(maxlen,0.5)
        self.fixed_step_size = fixed_step_size
        self.current_position = 0.5  # start position
        self.last_moved_time = utime.ticks_ms()  # initialize with the current time
        self.timeout_ms = timeout_ms

    def set_position(self, desired_position:float):
        # This only sets the target. Actual movement happens in do_loop.
        self.history.append(desired_position)
        if self.history[0] != self.history[1]:
            self.last_moved_time = utime.ticks_ms()

    def do_loop(self):
        # Check if there's a recent target to move towards
        #if not self.history:
        #    self.check_for_timeout()
        #   return
        #print(f"current_position: {self.current_position}")
        # Use the most recent target
        desired_position = self.history[0]
        #print(f"desired_position: {desired_position}")
        # Calculate a movement factor based on historical values
        movement_factor = self.compute_movement_factor()
        #print(f"movement_factor: {movement_factor}")
        # Calculate direction towards desired position
        direction = 1 if desired_position > self.current_position else -1
        #print(f"direction: {direction}")
        # Calculate effective movement with fixed size, but adjust direction
        movement_distance = abs(desired_position - self.current_position)
        step = min(self.fixed_step_size * movement_factor, movement_distance)
        effective_movement = step * direction
        #print(f"effective_movement: {effective_movement}")
        # Update the current position and move the servo
        #print(f"cutoff_movement: {effective_movement}")
        self.current_position += effective_movement
        self.move_servo_to_position(self.current_position)
        #print(f"current_position: {self.current_position}")
        # Update the last moved time
        self.last_moved_time = utime.ticks_ms()

        # Check for timeout after moving
        self.check_for_timeout()


    def move_servo_to_position(self, position):
        duty = int(position  * (115 - 40) + 40)
        self.servo.duty(duty)

    def compute_movement_factor(self):
        HIGH_FACTOR = 1.0
        LOW_FACTOR = 0.5
        NO_MOVE = 0.0
        h0,h1,h2 = self.history[0],self.history[1],self.history[2]
        # Check if there's no movement
        if h0 == h1:
            return NO_MOVE
        # Check for a change in direction or if it was not moving
        elif (h1 - h2) * (h0 - h1) <= 0:  # Change in direction or no prior movement
            return LOW_FACTOR
        else:  # The servo is moving in the same direction
            return HIGH_FACTOR



    def check_for_timeout(self):
        current_time = utime.ticks_ms()
        if utime.ticks_diff(current_time, self.last_moved_time) > self.timeout_ms:
            self.servo.duty(0)


if __name__ == "__main__":
    # Example usage:
    x_servo = SmoothServo(2)  # set pin number for X
    y_servo = SmoothServo(5)  # set pin number for Y

    x_servo.set_position(0.5)  # set target position for X servo
    y_servo.set_position(0.3)  # set target position for Y servo

    for _ in range(10):
        x_servo.do_loop()
        y_servo.do_loop()
