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
	angleSpan = 90.0 # Degrees of movement in hip joint for a step
	
	# Hips
	rightHipAngle = math.sin( timeOffset ) * angleSpan/2.0
	leftHipAngle = math.sin( timeOffset ) * angleSpan/2.0	

	# Knees
	rightKneeAngle = -60#10 - math.cos( timeOffset ) * angleSpan/2.0
	leftKneeAngle = 90#10 + math.cos( timeOffset ) * angleSpan/2.0
	
	# Feet
	rightFootAngle = 10 - math.sin( timeOffset ) * angleSpan/2.0
	leftFootAngle = 10 + math.sin( timeOffset ) * angleSpan/2.0

	# Save
	targetAngles[1] = rightHipAngle
	targetAngles[2] = leftHipAngle
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
