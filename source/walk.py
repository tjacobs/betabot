# Walking ability

# We're were going, we're gonna need some serious math
import math
import time

# Init
timeOffset = 0.0
targetAngles = [0] * 4
oldTime = time.time()

def updateTargetAngles( velocity, inverseTurningRadius ):
	global targetAngles, timeOffset, oldTime
	
	# Calculate
	angleSpan = 75 # Degrees of movement in hip joint for a step
	angleSpan *= 0.5 # Half, as sine goes -1 to 1 = 2.
	leftHipAngle = math.sin( timeOffset ) * angleSpan + angleSpan
	rightHipAngle = math.sin( timeOffset ) * angleSpan + angleSpan

	# Move forward in time
	timeJump = time.time() - oldTime
	if timeJump > 100: timeJump = 0.0 # Laggier than 100ms? Forget it
#	print( timeJump )
#	timeJump = 1
	timeOffset += timeJump * velocity
	oldTime = time.time()

	# Save
	targetAngles[0] = int( leftHipAngle )
	targetAngles[1] = int( rightHipAngle )
	return targetAngles

def calculateMovement( currentAngles, targetAngles ):
	# PID controller. Start with P. Deal with craziness of wraparound angles.
	Ps = [0] * len( targetAngles )
	P_rate = 1.0
	for i in range(len(targetAngles)):	
		# Go the shortest way around
		angle_cw =  targetAngles[i] - currentAngles[i]
		angle_ccw = targetAngles[i] - currentAngles[i] + 360
		angleFromTarget = angle_ccw
		if abs(angle_cw) < abs(angle_ccw):
			angleFromTarget = angle_cw
		Ps[i] = P_rate * angleFromTarget
	return Ps
