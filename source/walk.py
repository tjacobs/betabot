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
	angleSpan = 30.0 # Degrees of movement in hip joint for a step
	
	# Hips
	rightHipAngle = 90 + math.sin( timeOffset ) * angleSpan/2.0 + angleSpan/2.0
	leftHipAngle = 70 - math.cos( timeOffset ) * angleSpan/2.0  + angleSpan/2.0	

	# Knees
	rightKneeAngle = 10 - math.cos( timeOffset ) * angleSpan/2.0 * 4.0
	leftKneeAngle = 10 + math.cos( timeOffset ) * angleSpan/2.0 * 4.0
	
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

# PID controller. Start with P. Deal with craziness of wraparound angles.
numAngles = 2
previousAngles = [0.0] * (numAngles + 1)
def calculateMovement(currentAngles, targetAngles):
	global previousAngles
	movements = [0.0] * (numAngles + 1)
	Ps = [0.0] * (numAngles + 1)
	Ds = [0.0] * (numAngles + 1)
	P_rate = 0.2
	D_rate = 0.1
	for i in range(1, (numAngles+1)):
		# Go the shortest way around
		angle_cw =  targetAngles[i] - currentAngles[i]
		angle_ccw = targetAngles[i] - currentAngles[i] + 360
		angleFromTarget = angle_ccw
		if abs(angle_cw) < abs(angle_ccw):
			angleFromTarget = angle_cw
		Ps[i] = P_rate * angleFromTarget
		Ds[i] = D_rate * 0.0
		movements = Ps + Ds
	return movements
