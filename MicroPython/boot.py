# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
from machine import reset
from InterpolationTurret import Run
#from SmoothServo import SmoothServo
#x = SmoothServo(2)
#y = SmoothServo(5)
#    x.set_position(0.5)
 #   x.do_loop()
  #  y.set_position(0.2)
   # y.do_loop()