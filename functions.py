# -------------
# Betabot functions

def clamp(n, smallest, largest):
	return max(smallest, min(n, largest))

# Read angles from sensors
def readCurrentAngles( sensors ):
	currentAngles = [0] * 4
	try:
		for i in range(len(currentAngles)):
			currentAngles[i] = sensors.getAngle(i+1)
	except:
		return currentAngles
	return currentAngles

# Motor speeds can go from -100 to 100
def clampMotorSpeeds( motorSpeeds ):
	minSpeed = -100
	maxSpeed = 100
	for i in range(len(motorSpeeds)):
		motorSpeeds[i] = clamp(motorSpeeds[i], minSpeed, maxSpeed)
	return motorSpeeds

# Send the motor speeds to the motors
# And enable the motors if any have any speed
motorEnablePin = 18 # Broadcom 18 = pin 12, 6 from the top corner on the outside of the Pi
def sendMotorSpeeds( sbus, motorSpeedsIn, arm ):
	motorSpeeds = [0] * 4
	go = False
	for i in range(len(motorSpeedsIn)):
		motorSpeeds[i] = int(motorSpeedsIn[i])
		if( (i != 2 ) and (motorSpeeds[i] > 1 or motorSpeeds[i] < -1 ) ):
			go = True
	middle = 995
	sbus.sendSBUSPacket( [motorSpeeds[0]*6+middle, motorSpeeds[1]*6+middle, motorSpeeds[2]*6+middle, motorSpeeds[3]*6+middle, arm] )
	try:
		import RPi.GPIO as GPIO
		global motorEnablePin
		if( go ):
			GPIO.output(motorEnablePin, GPIO.HIGH)
		else:
			GPIO.output(motorEnablePin, GPIO.LOW)
	except NameError:
		import sys
		print( sys.exc_info() )
		pass

