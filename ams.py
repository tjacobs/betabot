import smbus
import time

class AMS():
  def __init__(self):
    self.address = 0x40
    self.angleReadReg1 = 0xFE
    self.angleReadReg2 = 0xFF
    self.magnitudeReadReg1 = 0xFC
    self.magnitudeReadReg2 = 0xFD

  def connect(self, bus):
    try:
      self.bus = smbus.SMBus(bus)
      time.sleep(0.5)
      return 0
    except:
      return -1

  def writeAndWait(self, register, value):
    self.bus.write_byte_data(self.address, register, value);
    time.sleep(0.02)

  def readAndWait(self, register):
    res = False
    try: 
    	res = self.bus.read_byte_data(self.address, register)
    except IOError:
        print "Oop"
    time.sleep(0.02)
    return res

  def getAngle(self):
    angle1 = self.readAndWait(self.angleReadReg1)
    angle2 = self.readAndWait(self.angleReadReg2)
    return (angle2 << 6) + angle1

  def getMagnitude(self):
    magnitude1 = self.readAndWait(self.magnitudeReadReg1)
    magnitude2 = self.readAndWait(self.magnitudeReadReg2)
    return magnitude2 << 6 + magnitude1

  def signedInt(self, value):
    if value > 127:
      return (256-value) * (-1)
    else:
      return value


