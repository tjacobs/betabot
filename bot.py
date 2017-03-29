# Betabot
# Code: https://github.com/tjacobs/betabot
# by Tom Jacobs

# Neural Network

# Inputs are:
# IMU X, Y angles (2) ( values 0 - 1. 0.5, 0.5 is flat level )
# CurrentAngles (8) ( values 0 - 1. from 0 to 2pi radians)
# Resistances (8) ( 0 - 1. amount of resistance each motor is currently experiencing )
# MotorSpeeds (8) ( 0 - 1. current motor speeds )
# Sin(t) (1) ( 0 - 1, sin of t, where t is increasing with time )
# Cos(t) (1) ( 0 - 1, cos of t, where t is increasing with time )

# Outputs are:
# TargetAngles (8) ( 0 - 1. )
# P_rate (8) (0 - 1, from off to max_p_rate)


# First task:

# Read FrSky telemetry, get acc_smoothed X,Y,Z.
# Use that to balance on wheels/

# Second task:

# Install Picamera[array] - openCV videoinput into TF.



from ams import AMS
from time import sleep
import time
import math
import array
#import tensorflow as tf

armTime = time.time()*1000

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

#~ sess = tf.Session()
#~ def network(x):
#~ 
	#~ # Fully Connected.
    #~ fc_W  = tf.Variable(tf.truncated_normal(shape=(n_legs, n_params), mean = 0, stddev = 0.1))
    #~ fc_b  = tf.Variable(tf.zeros(n_params))
    #~ output = tf.matmul(x, fc_W) + fc_b
    #~ return tf.sigmoid( output )


# Go
def main():
#	try:
		# Talk to motor angle sensors via I2C
		sensors = AMS()
		connected = sensors.connect(1)
		if connected < 0:
			print( "Warning: Can not read all motor sensors" )

		# Talk to motor controller via serial UART SBUS
		sbus = openSBUS()

		# What speed is each motor at, and one step back, two steps back?
		motorSpeeds = [0] * 8
		lastMotorSpeeds = [0] * 8
		lastLastMotorSpeeds = [0] * 8

		# Last loop values
		lastAngles = [0] * 8
		lastCheck = time.time()*1000

		#~ x_in = [[1]]
		#~ x = tf.placeholder(tf.float32, (1, 1))
		#~ input = network(x)
		#~ sess.run(tf.global_variables_initializer())

		# Loop
		while True:
			
			# Read accel X, Y, Z.
			accelX, accelY, accelZ = readTelemetryPackets(sbus)

			# Arm after one second
			arm = 500
			if time.time()*1000 > armTime + 1000:
				arm = 1000
    
		    #~ # What does our brain say to do?
			#~ x_in[0][0] = x_in[0][0] + 0.1
			#~ output = sess.run(input, feed_dict={x:x_in})
			#~ print( output )

			v = 1.0
			heading = math.pi

			vel_left = v
			vel_right = v
			
			# Main loop
			targetAngles = updateTargetAngles(vel_left, vel_right)
			currentAngles = readCurrentAngles(sensors)
			Ps = calculatePs(currentAngles, targetAngles)
			motorSpeeds = clampMotorSpeeds(Ps)
			print( currentAngles[0] / 100, currentAngles[1] / 100, motorSpeeds[0], motorSpeeds[1] )

			# Calculate how much the motor has moved in the last 100ms
			if time.time()*1000 > lastCheck + 100:
				lastCheck = time.time()*1000
				moved = currentAngles[0] - lastAngles[0]
				if( moved > 16384 - 5000 ):
					moved = moved - 16384
				if( moved < -(16384 - 5000) ):
					moved = moved + 16384
				percentageMoved = abs( moved / 30.0 )				
				percentagePower = abs(lastLastMotorSpeeds[0])
				
				# Record values for next check
				lastAngles[0] = currentAngles[0]
				lastLastMotorSpeeds[0] = lastMotorSpeeds[0]
				lastMotorSpeeds[0] = motorSpeeds[0]

				# Did we hit something?
#				percentageExpectedMoved = percentagePower
				#print "MOVED " + str( int( percentageMoved)) + "   POWER " + str( int(percentageExpectedMoved))
#				if( percentagePower > 30 and motorSpeeds[0] > 30 and percentageMoved < percentageExpectedMoved * 0.6 and hit == False):
#					print( "OW!" )
#					hit = True

			# Move
			sendMotorSpeeds(sbus, motorSpeeds, arm)
				

#	except:
#		
#	 	print( "DONE" )
#	 	arm = 500
#	 	sendMotorSpeeds(sbus, motorSpeeds, arm)
#	 	sleep(0.5)
#	 	sendMotorSpeeds(sbus, motorSpeeds, arm)

# -------------
# Functions

t = 0.0
targetAngles = [0] * 8
def updateTargetAngles( vel_left, vel_right ):
	global targetAngles, t
	targetAngles[0] = int( (t * 16384.0 / 100.0) % 16384 )
	targetAngles[1] = int( (t * 16384.0 / 100.0) % 16384 )
	t += 1.0
	return targetAngles

def readCurrentAngles(sensors):
	currentAngles = [0] * 8
	try:
		for i in range(4):
			currentAngles[i] = sensors.getAngle(i+1)
	except:
		return currentAngles
	return currentAngles

def clampMotorSpeeds( motorSpeeds ):
	minSpeed = -100
	maxSpeed = 100
	for i in range(len(motorSpeeds)):
		motorSpeeds[i] = max(min(motorSpeeds[i], maxSpeed), minSpeed)
	return motorSpeeds

def calculatePs( currentAngles, targetAngles ):
	Ps = [0] * len( targetAngles )
	P_rate = 0.05
	for i in range(len(targetAngles)):
		Ps[i] = P_rate * (targetAngles[i] - currentAngles[i])
	return Ps

def sendMotorSpeeds( sbus, motorSpeedsIn, arm ):
	motorSpeeds = [0] * 8
	for i in range(len(motorSpeedsIn)):
		motorSpeeds[i] = int(motorSpeedsIn[i])
	middle = 995
	sendSBUSPacket( sbus, [motorSpeeds[0]*6+middle, motorSpeeds[1]*6+middle, motorSpeeds[2]*6+middle, motorSpeeds[3]*6+middle, arm] )

# ----------
# SBUS

def openSBUS():
	try:
		import serial
		return serial.Serial(
			port='/dev/serial0',
			baudrate = 115200, # Must rebuild and flash betaflight to listen at this rate, not 100,000 as per normal SBUS.
			parity=serial.PARITY_EVEN,
			stopbits=serial.STOPBITS_TWO,
			bytesize=serial.EIGHTBITS,
			timeout=10)
	except:
		print( "Serial not available" )


PROTOCOL_HEADER      = 0x5E
PROTOCOL_TAIL        = 0x5E
ID_ACC_X             = 0x24
ID_ACC_Y             = 0x25
ID_ACC_Z             = 0x26

def read16( serial ):
	v1 = serial.read( )
	v2 = serial.read( )
	print( v1, v2 )
	value = v1 + v2 << 8
	return value	

def readTelemetryPackets( serial ):

	accelX, accelY, accelZ = 0, 0, 0
	while( serial.inWaiting() > 0 ):
		x = serial.read( )
		if( x == PROTOCOL_HEADER ):
			packet = serial.read( )
			print( packet )
			if( packet == ID_ACC_X ):
				accelX = read16( serial )
			if( packet == ID_ACC_Y ):
				accelY = read16( serial )
			if( packet == ID_ACC_Z ):
				accelZ = read16( serial )
	return accelX, accelY, accelZ


def sendSBUSPacket(sbus, channelValues):

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
		sbus.write( array.array('B', sbus_data).tostring() )
	except:
		pass


if __name__=="__main__":
   main()
