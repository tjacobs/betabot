# Betabot
# https://github.com/tjacobs/betabot
# by Tom Jacobs

print( "Starting Betabot." )

# Imports
import sys
import time
import math
import array
import datetime
import functions
import motors as motorsModule
import walk
import sensors

# What shall we enable?
ENABLE_KEYS 		= True
ENABLE_MOUSE 		= True
ENABLE_BRAIN 		= False
ENABLE_SIMULATOR 	= False

# Import Betabot parts
keys 		= None
mouse 		= None
brain 		= None
simulator 	= None
if ENABLE_KEYS:
	import keys
if ENABLE_MOUSE:
	import mouse
if ENABLE_BRAIN:
	import brain
if ENABLE_SIMULATOR:
	sys.path.append( 'simulator' )
	import simulator

# Go
def main():
	# Flush output for file logging
	sys.stdout.flush()

	# Init motor angle sensors via I2C
	magneticSensors = sensors.AMS()
	magneticSensors.connect(1)
	
	# Init motors via USB
	motorsModule.initMotors()
	motors = [0.0] * 9 # Motor outputs 1 to 8, ignore 0
	
	# Loop
	while not keys or not keys.esc_key_pressed:

		# Read current angles of motors
		currentAngles = functions.readCurrentAngles(magneticSensors)

		# Read current accelerometer value to see how far forward we're leaning
		pitch = motorsModule.readIMU('ax')

		# Figure out what our angles should be now to walk
		targetAngles = walk.updateTargetAngles(1.0)
#		targetAngles = walk.standUp(2.0)

		# Run movement controller to see how fast we should set our motor speeds
#		targetAngles = walk.restrictAngles(targetAngles)
		movement = walk.calculateMovement(currentAngles, targetAngles)
#		movement[1] = functions.clamp(movement[1], -1, 1)
#		movement[2] = functions.clamp(movement[2], -1, 1)

		# Send motor commands
		motors[1] = movement[1] 	 # Right motor
		motors[2] = movement[2] 	 # Left motor
		motors[3] = targetAngles[3]  # Right knee servo
		motors[4] = targetAngles[4]  # Left knee servo
		motors[5] = targetAngles[5]  # Right foot servo
		motors[6] = targetAngles[6]  # Left foot servo
		motorsModule.sendMotorCommands(motors, simulator, False, True)

		# Display balance, angles, target angles and speeds
#		functions.display( "Pitch: %3d. Right, Left: Hips: %3d, %3d, Targets: %3d, %3d, Speeds: %3d, %3d" 
#		        % (pitch, currentAngles[1], currentAngles[2], targetAngles[1], targetAngles[2], motors[1], motors[2] ) )
		#functions.display( "Pitch: %3d. Right, Left: Knees: %3d, %3d, Targets: %3d, %3d, Speeds: %3d, %3d" 
		#        % (pitch, 0, 0, targetAngles[3], targetAngles[4], motors[3], motors[4] ) )
#		functions.display( "Pitch: %3d. Right, Left: Feet: %3d, %3d, Targets: %3d, %3d, Speeds: %3d, %3d" 
#		        % (pitch, 0, 0, targetAngles[5], targetAngles[6], motors[5], motors[6] ) )

	# Stop motors
	motorsModule.stopMotors()

# Go
if __name__=="__main__":
   main()
