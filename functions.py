# -------------
# Betabot functions

def clamp(n, smallest, largest):
	return max(smallest, min(n, largest))

# Read angles from sensors
def readCurrentAngles( sensors ):
	currentAngles = [0] * 8
	try:
		for i in range(4):
			currentAngles[i] = sensors.getAngle(i+1)
	except:
		return currentAngles
	return currentAngles

# Motor speeds can go from -100 to 100
def clampMotorSpeeds( motorSpeeds ):
	minSpeed = -100
	maxSpeed = 100
	for i in range(len(motorSpeeds)):
		motorSpeeds[i] = max(min(motorSpeeds[i], maxSpeed), minSpeed)
	return motorSpeeds

# Send the motor speeds to the motors
# And enable the motors if any have any speed
def sendMotorSpeeds( sbus, motorSpeedsIn, arm ):
	motorSpeeds = [0] * 8
	go = False
	for i in range(len(motorSpeedsIn)):
		motorSpeeds[i] = int(motorSpeedsIn[i])
		if( (i != 2 ) and (motorSpeeds[i] > 1 or motorSpeeds[i] < -1 ) ):
			go = True
	try:
		import RPi.GPIO as GPIO
		global motorEnablePin
		if( go ):
			GPIO.output(motorEnablePin, GPIO.HIGH)
		else:
			GPIO.output(motorEnablePin, GPIO.LOW)
	except NameError:
		pass
	middle = 995
	sbus.sendSBUSPacket( [motorSpeeds[0]*6+middle, motorSpeeds[1]*6+middle, motorSpeeds[2]*6+middle, motorSpeeds[3]*6+middle, arm] )

#t = 0.0
#targetAngles = [0] * 8
#def updateTargetAngles( vel_left, vel_right ):
#	global targetAngles, t
#	targetAngles[0] = int( (t * 16384.0 / 2000.0) % 16384 )
#	targetAngles[1] = int( (t * 16384.0 / 2000.0) % 16384 )
#	t += 1.0
#	return targetAngles

#def calculatePs( currentAngles, targetAngles ):
#	Ps = [0] * len( targetAngles )
#	P_rate = 0.05
#	for i in range(len(targetAngles)):
#		Ps[i] = P_rate * (targetAngles[i] - currentAngles[i])
#	return Ps
