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
import motors
import walk
import sensors

# What shall we enable?
ENABLE_KEYS 		= True
ENABLE_MOUSE 		= True
ENABLE_BRAIN 		= False
ENABLE_SIMULATOR 	= True

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
	motors.initMotors()
	motorSpeeds = [0.0] * 9 # Motor outputs 1 to 8, ignore 0

	# Init mouse
	mouse_x_diff   = 0.0
	mouse_y_diff   = 0.0
	old_mouse_x    = 0.0
	old_mouse_y	   = 0.0
	mouse_speed_factor = 1.0
	
	# Init balance trim
	trim = 0.0
	sineOffset = 0.0

	# Read initial angles
	offsetPitch = motors.readIMU()
	currentAngles = functions.readCurrentAngles(magneticSensors)
	offsetAngle = currentAngles[1]
	
	# Loop
	while not keys or not keys.esc_key_pressed:

		# Read current IMU accelerometer values to see which way we're leaning
		pitch = motors.readIMU()
		
		# Update from keyboard
		if( keys ):
			if( keys.up_key_pressed == True ):
				trim += 1
			if( keys.down_key_pressed == True ):
				trim -= 1

		# Update from mouse
		if( mouse ):
			# How much has the mouse moved from last loop?
			mouse_x = mouse.mouse_x
			mouse_y = mouse.mouse_y
			mouse_x_diff = mouse_x - old_mouse_x
			mouse_y_diff = mouse_y - old_mouse_y			
			if( mouse_x_diff > 500 ): mouse_x_diff = 0
			if( mouse_x_diff < -500 ): mouse_x_diff = 0
			if( mouse_y_diff > 500 ): mouse_y_diff = 0
			if( mouse_y_diff < -500 ): mouse_y_diff = 0
			old_mouse_x = mouse_x
			old_mouse_y = mouse_y
			mouse_x_diff *= mouse_speed_factor
			mouse_y_diff *= mouse_speed_factor

		# Read current angles of motors
		currentAngles = functions.readCurrentAngles(sensors)
		
		# Compensate for the angle seen at startup
#		currentAngles[1] += offsetAngle
#		currentAngles[3] += offsetAngle

		# Figure out what our angles should be now to walk
		targetAngles = walk.updateTargetAngles(2.0)

		# Compensate for our current body angle to always stand up straight
		targetAngles[1] += pitch

		# Allow ourselves to lean forward back manually
		targetAngles[3] += trim

		# Move mouse up, raise up
		#targetAngles[1] += 255 #mouse_y/3 # Right hip goes CW
		#targetAngles[2] += mouse_y/3 # Left hip goes CW
		#targetAngles[3] += 280 #mouse_x/3 # Right knee goes CCW
		#targetAngles[4] -= mouse_y/3 # Left knee goes CCW
		#targetAngles[5] -= mouse_y/3 # Right foot goes CCW
		#targetAngles[6] -= mouse_y/3 # Left foot goes CCW

		# Restrict movement. Hip and knee should only ever try to go 90 degrees
		targetAngles[1] = functions.clamp(targetAngles[1], -100, 100) #210, 300)
		targetAngles[2] = functions.clamp(targetAngles[2], -100, 100) #210, 300)
		targetAngles[3] = functions.clamp(targetAngles[3], -100, 100)
		targetAngles[4] = functions.clamp(targetAngles[4], -100, 100)
		targetAngles[5] = functions.clamp(targetAngles[5], -100, 100)
		targetAngles[6] = functions.clamp(targetAngles[6], -100, 100)

		# Set servo angles directly
		rightKneeServoAngle = targetAngles[3]
		leftKneeServoAngle = targetAngles[4]
		rightFootServoAngle = targetAngles[5]
		leftFootServoAngle = targetAngles[6]

		# Run our movement controller to see how fast we should set our motor speeds to get to targets
		movement = walk.calculateMovement(currentAngles, targetAngles)

		# Send motor speeds
		motorSpeeds[1] = 0#targetAngles[1]# movement[1] 		  # Right hip
		motorSpeeds[2] = 0#targetAngles[2]# movement[2] 		  # Left hip
		motorSpeeds[3] = rightKneeServoAngle  # Right knee servo
		motorSpeeds[4] = leftKneeServoAngle   # Left knee servo
		motorSpeeds[5] = rightFootServoAngle  # Right foot servo
		motorSpeeds[6] = leftFootServoAngle   # Left foot servo
		motors.sendMotorSpeeds(motorSpeeds, simulator, True, False)
		
		# Display balance, angles, target angles and speeds
#		functions.display( "Pitch: %3d. R Hip, R Knee: %3d, %3d, Target: %3d, %3d, Speeds: %3d, %3d" % (pitch, currentAngles[0], currentAngles[2], targetAngles[0], targetAngles[2], motorSpeeds[0], motorSpeeds[2] ) )

	# Finish up
	try:
		import RPi.GPIO as GPIO
		GPIO.cleanup()
	except:
		pass

	# Close
	motorSpeeds[0] = 0
	motorSpeeds[1] = 0
	motors.sendMotorSpeeds(motorSpeeds)
	motors.board.close()

# Go
if __name__=="__main__":
   main()
