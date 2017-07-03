# Walking ability

# We're were going, we're gonna need some serious math
import math
import time
import functions

# Init
timeOffset = 0.0
targetAngles = [0] * 9
oldTime = time.time()

def restrictAngles(targetAngles):
	# Restrict movement
	targetAngles[1] = functions.clamp(targetAngles[1], -180, 180)
	targetAngles[2] = functions.clamp(targetAngles[2], -180, 180)
	targetAngles[3] = functions.clamp(targetAngles[3], -100, 100)
	targetAngles[4] = functions.clamp(targetAngles[4], -100, 100)
	targetAngles[5] = functions.clamp(targetAngles[5], -100, 100)
	targetAngles[6] = functions.clamp(targetAngles[6], -100, 100)
	return targetAngles

def standUp(velocity):
	global timeOffset, oldTime

	# Move forward in time
	timeJump = time.time() - oldTime
	if timeJump > 100: timeJump = 0.0 # Laggier than 100ms? Forget it
	timeOffset += timeJump * velocity
	oldTime = time.time()
	
	angleSpan = 60.0
	
	# Hips
	rightHipAngle = math.sin(timeOffset)*20
	leftHipAngle  = math.sin(timeOffset)*20

	# Knees
	rightKneeAngle = -math.sin(timeOffset)*20
	leftKneeAngle  = -math.sin(timeOffset)*20
	
	# Feet
	rightFootAngle = math.sin(timeOffset)*10 + 4
	leftFootAngle  = math.sin(timeOffset)*10 + 4

	# Save
	targetAngles[1] = rightHipAngle
	targetAngles[2] = leftHipAngle
	targetAngles[3] = rightKneeAngle
	targetAngles[4] = leftKneeAngle
	targetAngles[5] = rightFootAngle
	targetAngles[6] = leftFootAngle
	return targetAngles

def updateTargetAngles(velocity):
	global targetAngles, timeOffset, oldTime

	# Define our gait
	rightHipTimeOffset = 0
	leftHipTimeOffset = math.pi/2
	rightKneeTimeOffset = 0
	leftKneeTimeOffset = math.pi/2
	rightFootTimeOffset = 0 + math.pi/8
	leftFootTimeOffset = math.pi/2 + math.pi/8

	# Move forward in time
	timeJump = time.time() - oldTime
	if timeJump > 100: timeJump = 0.0 # Laggier than 100ms? Forget it
	timeOffset += timeJump * velocity
	oldTime = time.time()
	
	# Calculate
	angleSpan = 160.0 # Degrees of movement in hip joint for a step
	
	# Hips
	rightHipAngle = 0 + math.sin( timeOffset + rightHipTimeOffset ) * angleSpan/2.0 
	leftHipAngle = 0 - math.sin( timeOffset + leftHipTimeOffset ) * angleSpan/2.0	

	# Knees
	rightKneeAngle = - math.sin( timeOffset + rightKneeTimeOffset ) * angleSpan/2.0 * 2.2
	leftKneeAngle =    math.sin( timeOffset + leftKneeTimeOffset ) * angleSpan/2.0 * 2.2
	
	# Feet
	rightFootAngle = 0 - math.sin( timeOffset + rightFootTimeOffset ) * angleSpan/2.0 * 2.1
	leftFootAngle = 0 + math.sin( timeOffset + leftFootTimeOffset ) * angleSpan/2.0 * 2.1

	# Save
	targetAngles[1] = rightHipAngle
	targetAngles[2] = leftHipAngle
	targetAngles[3] = rightKneeAngle
	targetAngles[4] = leftKneeAngle
	targetAngles[5] = rightFootAngle
	targetAngles[6] = leftFootAngle
	return targetAngles

# PD controller.
numAngles = 2
previousAngles = [0.0] * (numAngles + 1)
def calculateMovement(currentAngles, targetAngles):
	global previousAngles
	movements = [0.0] * (numAngles + 1)
	Ps = [0.0] * (numAngles + 1)
	Ds = [0.0] * (numAngles + 1)
	P_rate = 8.0
	D_rate = 0.0
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
