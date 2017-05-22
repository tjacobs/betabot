# Walking ability

# We're were going, we're gonna need some serious math
import math
import time

# Init
timeOffset = 0.0
targetAngles = [0] * 9
oldTime = time.time()

def updateTargetAngles(velocity):
	global targetAngles, timeOffset, oldTime

	# Move forward in time
	timeJump = time.time() - oldTime
	if timeJump > 100: timeJump = 0.0 # Laggier than 100ms? Forget it
	timeOffset += timeJump * velocity
	oldTime = time.time()
	
	# Calculate
	angleSpan = 10.0 # Degrees of movement in hip joint for a step
	angleSpan *= 0.5 # Half, as sine goes -1 to 1 = 2.
	
	# Hips
	rightHipAngle = math.sin( timeOffset ) * angleSpan + angleSpan
	leftHipAngle = math.sin( timeOffset ) * angleSpan + angleSpan
	
	# Knees
	rightKneeAngle = math.cos( timeOffset ) * angleSpan + angleSpan
	leftKneeAngle = math.cos( timeOffset ) * angleSpan + angleSpan
	
	# Feet
	rightFootAngle = math.sin( timeOffset ) * angleSpan/2.0
	leftFootAngle = math.sin( timeOffset ) * angleSpan/2.0

	# Save
	targetAngles[1] = int( rightHipAngle )
	targetAngles[2] = int( leftHipAngle )
	targetAngles[3] = rightKneeAngle
	targetAngles[4] = leftKneeAngle
	targetAngles[5] = rightFootAngle
	targetAngles[6] = leftFootAngle
	return targetAngles

def calculateMovement(currentAngles, targetAngles):
	# PID controller. Start with P. Deal with craziness of wraparound angles.
	numAngles = 4
	Ps = [0] * numAngles
	P_rate = 0.01
	for i in range(numAngles):
		# Go the shortest way around
		angle_cw =  targetAngles[i] - currentAngles[i]
		angle_ccw = targetAngles[i] - currentAngles[i] + 360
		angleFromTarget = angle_ccw
		if abs(angle_cw) < abs(angle_ccw):
			angleFromTarget = angle_cw
		Ps[i] = P_rate * angleFromTarget
	return Ps
