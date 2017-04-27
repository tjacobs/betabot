# Walking ability

# We're were going, we're gonna need some serious math
import math

timeOffset = 0.0
targetAngles = [0] * 4
def updateTargetAngles( velocity, inverseTurningRadius ):
	global targetAngles, timeOffset
	
	# Calculate desired hip angles
	hipTravel = 50 # Degrees of movement in hip joint for a step
	leftHipAngle = math.sin( timeOffset ) * hipTravel
	rightHipAngle = math.cos( timeOffset ) * hipTravel
	timeOffset += 0.001

	# Save
	targetAngles[0] = int( rightHipAngle )
	targetAngles[1] = int( leftHipAngle )
	return targetAngles

def calculateMovement( currentAngles, targetAngles ):
	# PID controller. Start with P.
	Ps = [0] * len( targetAngles )
	P_rate = 0.1
	for i in range(len(targetAngles)):
		Ps[i] = P_rate * (targetAngles[i] - currentAngles[i])
	return Ps
