import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from ESPTurret import GetSerial
import serial

class App(QMainWindow):

    def __init__(self):
        super().__init__()

        # Serial setup
        serport = "/dev/ttyUSB0"#GetSerial()
        print(f"Port: {serport}")
        self.ser = serial.Serial(serport, 115200, timeout=1) 
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)  # Window dimensions
        self.setWindowTitle('Mouse Command Sender')
        self.show()
        self.mouseMoveEvent = self.HandleMouseMove
        self.setMouseTracking(True)

    def closeEvent(self, event):
        self.ser.close()

    def HandleMouseMove(self, event):
        x, y = event.x(), event.y()

        # Map x, y to 0-255 range
        int8_x = float(1 * (x / self.width()))
        int8_y = float(1 * (y / self.height()))
        command = f"move,{int8_x},{int8_y},0\r\n"  # Laser power is set to 0 in this example
        print(command)
        self.ser.write(command.encode())
        self.ser.flush()
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
