
import serial
import serial.tools.list_ports
import sys

last_x = 127  # Default values
last_y = 127
last_laser = False
def send_command(x_byte=None, y_byte=None, laser=None, scaling_factor=1.0, port='/dev/ttyUSB1'):
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


def GetSerial():
    ports = list(serial.tools.list_ports.comports())
    if sys.platform.startswith('win'):
        # Windows
        com_ports = [port.device for port in ports if port.device.startswith("COM")]
        if not com_ports:
            return None
        com_numbers = [int(port.replace("COM", "")) for port in com_ports]
        return f"COM{max(com_numbers)}"
    else:
        # Linux
        acm_ports = [port.device for port in ports if port.device.startswith("/dev/ttyACM")]
        usb_ports = [port.device for port in ports if port.device.startswith("/dev/ttyUSB")]
        
        all_ports = acm_ports + usb_ports
        if not all_ports:
            return None

        # Extracting numbers from the port string and returning the highest one
        port_numbers = [int(port.split('/')[-1].replace("ttyACM", "").replace("ttyUSB", "")) for port in all_ports]
        highest_port_num = max(port_numbers)

        if f"/dev/ttyACM{highest_port_num}" in all_ports:
            return f"/dev/ttyACM{highest_port_num}"
        else:
            return f"/dev/ttyUSB{highest_port_num}"

