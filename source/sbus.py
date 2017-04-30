# ----------
# SBUS functions
import sys
import functions

class SBUS():
	def __init__(self):
		self.sbus = None
		pass

	def connect(self):
		try:
			import serial
			self.sbus = serial.Serial(
				port='/dev/serial0',
				baudrate = 115200, # Must rebuild and flash betaflight to listen at this rate, not 100,000 as per normal SBUS.
				parity=serial.PARITY_EVEN,
				stopbits=serial.STOPBITS_TWO,
				bytesize=serial.EIGHTBITS,
				timeout=10)
		except:
			print( "Error: Cannot read serial. Please enable serial in raspi-config." )

		# Motor enable pin
		try:
			import RPi.GPIO as GPIO
			GPIO.setwarnings(False)
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(functions.motorEnablePin, GPIO.OUT)
			GPIO.output(functions.motorEnablePin, GPIO.LOW)

			# Test
			if( False ):
				time.sleep( 0.2 )
				sys.stdout.write("\r\x1b[KTest: Motors on." )
				GPIO.output(functions.motorEnablePin, GPIO.HIGH)
				time.sleep( 2 )
				sys.stdout.write("\r\x1b[KTest: Motors off." )
				GPIO.output(functions.motorEnablePin, GPIO.LOW)
				time.sleep( 1 )
				sys.stdout.write("\n" )

		except:
			print( "Error: Cannot access Raspberry Pi GPIO." )
#			print( sys.exc_info() )
			

	def sendSBUSPacket(self, channelValues):

		# 16 blank channels, copy as many channels as given
		channels = [100]*16
		for j in range(len(channelValues)):
			channels[j] = int(channelValues[j])

		# SBUS start byte
		sbus_data = [0]*25
		sbus_data[0] = 0x0F

		# SBUS channel bytes. 11 bits per channel.
		ch = 0
		bit_in_channel = 0
		byte_in_sbus = 1
		bit_in_sbus = 0
	   
		# For 16ch * 11bits = 176 bits 
		for i in range(1, 176):
			if channels[ch] & (1<<bit_in_channel):
				sbus_data[byte_in_sbus] |= (1<<bit_in_sbus)
			bit_in_sbus = bit_in_sbus + 1
			bit_in_channel = bit_in_channel + 1
			if bit_in_sbus == 8:
				bit_in_sbus = 0
				byte_in_sbus = byte_in_sbus + 1
			if bit_in_channel == 11:
				bit_in_channel = 0
				ch = ch + 1

		# Send
		try:
			import serial
			import array
			import time
			if( self.sbus != 0 ):
				self.sbus.write( array.array('B', sbus_data).tostring() )
				time.sleep( 0.001 )
		except:
			pass

# -- Reading from serial --

	def read16( serial ):
		v1 = serial.read( )
		v2 = serial.read( )
#		print( v1, v2 )
		value = v1 + v2 << 8
		return value	

	def readIMU( self ):
		serial = self.sbus
		if serial == None:
			return 0, 0, 0
		accelX, accelY, accelZ = 0, 0, 0
		waiting = serial.inWaiting()
		if( waiting > 0 ):
			print( "Bytes waiting in serial input: " + str( waiting ) )
		while( serial and waiting > 0 ):
			x = serial.read( )
			print( ord( x ) )
#	#		if( x == PROTOCOL_HEADER ):
			if( False ):
				packet = serial.read( )
				print( packet )
#				print( str( ord( packet ) ) )
				if( packet == ID_ACC_X ):
					accelX = read16( serial )
				if( packet == ID_ACC_Y ):
					accelY = read16( serial )
				if( packet == ID_ACC_Z ):
					accelZ = read16( serial )
			waiting = serial.inWaiting()
		return accelX, accelY, accelZ

# ----------
# Serial telemetry functions

PROTOCOL_HEADER      = 0x5E
PROTOCOL_TAIL        = 0x5E
ID_ACC_X             = 0x24
ID_ACC_Y             = 0x25
ID_ACC_Z             = 0x26

