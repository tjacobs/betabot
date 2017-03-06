# Betabot
# Code: https://github.com/tjacobs/betabot
# by Tom Jacobs

# Neural Network: LSTM.
# 

# Inputs are:
# IMU X, Y angles (2) ( 0 - 1, 0.5, 0.5 is flat level )
# CurrentAngles (8) ( 0 - 1, from 20 to 160 degrees, 0 being knees all straight up in the air, flipped for backwards motors )
# Resistances (8) ( 0 - 1, amount of resistance each motor is currently experiencing )
# MotorSpeeds (8) ( 0 - 1, current motor speeds from calculated from PID loop from output params )
# Sin(t) (1) ( 0 - 1, sin of t, where t is increasing with time )
# Cos(t) (1) ( 0 - 1, cos of t, where t is increasing with time )

# Outputs are:
# TargetAngles (8) ( 0 - 1, from 20 to 160 degrees. Flipped for every backwards motor, so 0 is always up. )
# P_rate (8) (0 - 1, from off to max_p_rate) (add later, fix to resonable default to start with)

# How it works
# Robot starts standing, all legs almost knees sraight up.
# CurrentAngles = [ 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1 ]

# 1. Train the network to stay like that.
# Loss function = difference of targetAngles to [ 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1 ]



from ams import AMS
from time import sleep
import time
import math
import array
import tensorflow as tf

hit = False
armTime = time.time()*1000

n_legs = 1
n_params = 6
sess = tf.Session()

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def network(x):

	# Fully Connected.
    fc_W  = tf.Variable(tf.truncated_normal(shape=(n_legs, n_params), mean = 0, stddev = 0.1))
    fc_b  = tf.Variable(tf.zeros(n_params))
    output = tf.matmul(x, fc_W) + fc_b
    return tf.sigmoid( output )


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

		x_in = [[1]]
		x = tf.placeholder(tf.float32, (1, 1))
		input = network(x)
		sess.run(tf.global_variables_initializer())

		# Loop
		global hit
		while True:
			
			# Arm after a second
			arm = 500
			if time.time()*1000 > armTime + 1000:
				arm = 1000
    
			x_in[0][0] = x_in[0][0] + 0.1
		    # What does our brain say to do?
			output = sess.run(input, feed_dict={x:x_in})
			print( output )
			speed = 10
			left = {}
			left['offset'] =     clamp( output[0][0], 0.0, 1.0) * 1000.0
			left['timeOffset'] = clamp( output[0][1], 0.0, 1.0) * 1.0
			left['scale'] =      clamp( output[0][2], 0.0, 1.0) * 4000.0
			right = {}
			right['offset'] = 0
			right['timeOffset'] = 0.5 # Quarter turn
			right['scale'] = 4000

			# Main loop
			targetAngles = updateTargetAngles(speed, left, right)
			currentAngles = readCurrentAngles(sensors)
			Ps = calculatePs(currentAngles, targetAngles)
			motorSpeeds = clampMotorSpeeds(Ps)

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
				percentageExpectedMoved = percentagePower
				#print "MOVED " + str( int( percentageMoved)) + "   POWER " + str( int(percentageExpectedMoved))
				if( percentagePower > 40 and motorSpeeds[0] > 40 and percentageMoved < percentageExpectedMoved * 0.6 and hit == False):
					print( "OW!" )
					hit = True

			# Slow if leg hit something			
			if hit == True:
				motorSpeeds[0] = motorSpeeds[0] / 8
				motorSpeeds[1] = motorSpeeds[1] / 8

			# Move
			sendMotorSpeeds(sbus, motorSpeeds, arm)
				

	# except:
		
	# 	print( "DONE" )
	# 	arm = 500
	# 	sendMotorSpeeds(sbus, motorSpeeds, arm)
	# 	sleep(0.5)
	# 	sendMotorSpeeds(sbus, motorSpeeds, arm)

# -------------
# Functions

t = 0
targetAngles = [0] * 8
def updateTargetAngles( speed, left, right ):
	global targetAngles, t, hit
	targetAngles[0] = int( math.sin( speed * t * math.pi / 500 + (left['timeOffset']*math.pi)) * left['scale'] + 6000 + left['offset'] )
	targetAngles[1] = int( math.sin( speed * t * math.pi / 500 + (right['timeOffset']*math.pi)) * right['scale'] + 9000 + right['offset'] )
	t += 1
	if( t > 500 * 2 / speed ):
		t = 0
		hit = False
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
	sendSBUSPacket( sbus, [motorSpeeds[0]*6+middle, motorSpeeds[1]*6+middle, motorSpeeds[2]*2+middle, motorSpeeds[3]*2+middle, arm] )

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
