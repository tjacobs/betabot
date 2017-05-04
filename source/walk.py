# Walking ability

# We're were going, we're gonna need some serious math
import math
import time

timeOffset = 0.0
targetAngles = [0] * 4
oldTime = time.time()
def updateTargetAngles( velocity, inverseTurningRadius ):
	global targetAngles, timeOffset, oldTime
	
	# Calculate desired hip angles
	hipTravel = 50 # Degrees of movement in hip joint for a step
	leftHipAngle = math.sin( timeOffset ) * hipTravel + hipTravel 
	rightHipAngle = math.cos( timeOffset ) * hipTravel + hipTravel

	# Move forward in time
	timeJump = time.time() - oldTime
	if timeJump > 100: timeJump = 0.0 # Laggier than 100ms? Forget it
	timeOffset += timeJump
	oldTime = time.time()

	# Save
	targetAngles[0] = int( rightHipAngle )
	targetAngles[1] = int( leftHipAngle )
	return targetAngles

def calculateMovement( currentAngles, targetAngles ):
	# PID controller. Start with P.
	Ps = [0] * len( targetAngles )
	P_rate = 0.5
	for i in range(len(targetAngles)):
		Ps[i] = P_rate * (targetAngles[i] - currentAngles[i])
	return Ps
