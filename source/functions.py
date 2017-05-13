# -------------
# Betabot functions
import time
import sys

def display(string):
	sys.stdout.write("\r\x1b[K" + string)
	sys.stdout.flush()

def clamp(n, smallest, largest):
	return max(smallest, min(n, largest))

# Read angles from sensors
def readCurrentAngles( sensors ):
	currentAngles = [0] * 4
	try:
		for i in range(len(currentAngles)):
			mag = sensors.getMagnitude(i+1)
			if mag > 100:
				currentAngles[i] = 360.0 * sensors.getAngle(i+1) / 16384.0
	except:
		return currentAngles
	return currentAngles

