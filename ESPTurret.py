
import serial

last_x = 127  # Default values
last_y = 127
last_laser = False
def send_command(x_byte=None, y_byte=None, laser=None, scaling_factor=1.0, port='/dev/ttyUSB0'):
    global last_x, last_y, last_laser

    if x_byte is None:
        x_byte = last_x
    if y_byte is None:
        y_byte = last_y
    if laser is None:
        laser = last_laser

    scaled_x = min(255, int(x_byte * scaling_factor))
    scaled_y = min(255, int(y_byte * scaling_factor))
    avg_x = (last_x + scaled_x) // 2
    avg_y = (last_y + scaled_y) // 2

    if scaled_x != last_x or scaled_y != last_y or laser != last_laser:
        command = f"move,{avg_x},{avg_y},{127 if laser else 0}\r\n"
        
        with serial.Serial(port, 115200) as ser:
            ser.write(command.encode())

    last_x, last_y, last_laser = avg_x, avg_y, laser