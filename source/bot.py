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
from sensors import AMS

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

	# Init motor angle sensors via I2C
	sensors = AMS()
	sensors.connect(1)

	# Init motors via USB
	motors.initMotors()

	# Flush output for file logging
	sys.stdout.flush()

	# Init velocity forward/backward, and individual left right velocities
	velocity       = 0.0
	velocity_left  = 0.0
	velocity_right = 0.0
	motorSpeeds    = [0] * 4

	# Init mouse
	old_mouse_x    = 0.0
	old_mouse_y	   = 0.0
	mouse_speed_factor = 1.0
	
	# Init balance trim
	trim = 0.0

	# Read initial angles
	board = motors.readIMU()
	offsetPitch = board.rawIMU['ay']
	currentAngles = functions.readCurrentAngles(sensors)
	offsetAngle = currentAngles[1]

	# Loop
	while not keys or not keys.esc_key_pressed:

		# Read current IMU accelerometer values to see which way we're leaning
		board = motors.readIMU()
		pitch = board.rawIMU['ay']

		# Slow down slowly
		velocity       *= 0.98
		velocity_left  *= 0.95
		velocity_right *= 0.95
		
		# Update velocities
		if( brain ):
			if( brain.up_key_pressed == True ):   velocity += 2.3
			if( brain.down_key_pressed == True ): velocity -= 2.3
			if( brain.left_key_pressed == True ):
				velocity_right += 1.5
				velocity_left -= 1.5
			if( brain.right_key_pressed == True ):
				velocity_left += 1.5
				velocity_right -= 1.5
		if( keys ):
			if( keys.up_key_pressed == True ):
				trim += 1
				#velocity += 2.3
			if( keys.down_key_pressed == True ):
				trim -= 1
				#velocity -= 2.3
			if( keys.left_key_pressed == True ): 
				velocity_right -= 1.5
				velocity_left += 1.5
			if( keys.right_key_pressed == True ):
				velocity_left -= 1.5
				velocity_right += 1.5

		# Update velocity from mouse
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

			# Set forward/backward speed
#			velocity -= mouse_y_diff * mouse_speed_factor * 2.0

			# Set rotate left right speed
			velocity_left -= mouse_x_diff * mouse_speed_factor
			velocity_right += mouse_y_diff * mouse_speed_factor

			# Remember
			old_mouse_x = mouse_x
			old_mouse_y = mouse_y

		# Update velocities
		velocity       = functions.clamp(velocity,       -100.0, 100.0)
		velocity_left  = functions.clamp(velocity_left,  -100.0, 100.0)
		velocity_right = functions.clamp(velocity_right, -100.0, 100.0)

		# Read current angles of motors
		currentAngles = functions.readCurrentAngles(sensors)
		
		# Figure out what our angles should be now to walk
		targetAngles = walk.updateTargetAngles(1.0, 0)

		# Compensate for the angle seen at startup
		targetAngles[0] += offsetAngle
		targetAngles[1] += offsetAngle

		# Compensate for our current body angle to always stand up straight
		targetAngles[0] += pitch
		targetAngles[1] += pitch

		# Allow ourselves to lean forward back manually
		targetAngles[0] += trim
		targetAngles[1] += trim

		# Run our movement controller to see how fast we should set our motor speeds to get to targets
		movement = walk.calculateMovement(currentAngles, targetAngles)

		# Send motor speeds
		motorSpeeds[0] = (velocity + velocity_right)#- movement[0]
		motorSpeeds[1] = (velocity + velocity_left) #- movement[1]
		motors.sendMotorSpeeds(motorSpeeds)
		
		# Display balance, angles, target angles and speeds
		functions.display( "Pitch: %3d. Angles: %3d, %3d, Targets: %3d, %3d, Speeds: %3d, %3d" % (pitch, currentAngles[0], currentAngles[1], targetAngles[0], targetAngles[1], motorSpeeds[0], motorSpeeds[1] ) )

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
