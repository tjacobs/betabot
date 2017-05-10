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
import walk

# What shall we enable?
ENABLE_KEYS = True
ENABLE_MOUSE = False
ENABLE_BRAIN = False
ENABLE_SIMULATOR = False

# Import Betabot parts
keys = None
mouse = None
brain = None
simulator = None
motors = None
from sensors import AMS
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
	functions.initMotors()

	# Init motor speeds
	velocity       = 0.0
	velocity_left  = 0.0
	velocity_right = 0.0
	motorSpeeds    = [0] * 4
	old_mouse_x    = 0.0
	old_mouse_y	   = 0.0
	mouse_speed_factor = 1.0

	# Flush output for file logging
	sys.stdout.flush()

	# Loop
	while not keys or not keys.esc_key_pressed:

		# Read current IMU accelerometer X, Y, Z values.
#			board = functions.readIMU()

		# Slow down slowly
		velocity       *= 0.98
		velocity_left  *= 0.95
		velocity_right *= 0.95
		
		# keys/brain moving forward, left, or right?
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
			if( keys.up_key_pressed == True ):   velocity += 2.3
			if( keys.down_key_pressed == True ): velocity -= 2.3
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
			velocity -= mouse_y_diff * mouse_speed_factor * 2.0

			# Set rotate left right speed
			velocity_left -= mouse_x_diff * mouse_speed_factor
			velocity_right += mouse_x_diff * mouse_speed_factor

			# Remember
			old_mouse_x = mouse_x
			old_mouse_y = mouse_y

		# Calculate left and right wheel velocities
		#R = 0.1 # Radius of wheels
		#L = 0.1 # Linear distance between wheels
		#(2.0 * velocity - heading * L ) / 2.0 * R
		#(2.0 * velocity + heading * L ) / 2.0 * R

		# Update velocities
#		velocity       = functions.clamp( velocity, -80.0, 80.0 )
#		velocity_left  = functions.clamp( velocity_left, -80.0, 80.0 )
#		velocity_right = functions.clamp( velocity_right, -80.0, 80.0 )

		# Read current wheel rotational angles
		currentAngles = functions.readCurrentAngles(sensors)
		
		# Figure out what our angles should be
		targetAngles = walk.updateTargetAngles(0.5, 0)
		
		# Run our movement controller
		movement = walk.calculateMovement(currentAngles, targetAngles)

		# Send motor speeds
		motorSpeeds[0] = (velocity + velocity_right) - movement[0]
		motorSpeeds[1] = (velocity + velocity_left) - movement[1]
		functions.sendMotorSpeeds(motorSpeeds)

		# Display balance
#		message = "ax= {:+.0f} ay= {:+.0f} az= {:+.0f} gx= {:+.0f} gy= {:+.0f} gz= {:+.0f} mx= {:+.0f} my= {:+.0f} mz= {:+.0f}" .format(float(board.rawIMU['ax']),float(board.rawIMU['ay']),float(board.rawIMU['az']),float(board.rawIMU['gx']),float(board.rawIMU['gy']),float(board.rawIMU['gz']),float(board.rawIMU['mx']),float(board.rawIMU['my']),float(board.rawIMU['mz']))
#		sys.stdout.write("\r%s" % message )
		
		# Display wheel angles and speeds
		#sys.stdout.write("\r\x1b[KCurrent Angles: %3d, %3d, Target Angles: %3d, %3d, Motor Speeds: %3d, %3d" % 
		#	(currentAngles[0], currentAngles[1], targetAngles[0], targetAngles[1], motorSpeeds[0], motorSpeeds[1] ) )
		#sys.stdout.flush()			

	# Finish up
	try:
		import RPi.GPIO as GPIO
		GPIO.cleanup()
	except:
		pass

	# Close
	motorSpeeds[0] = 0
	motorSpeeds[1] = 0
	functions.sendMotorSpeeds(motorSpeeds)
	functions.board.close()

# Go
if __name__=="__main__":
   main()
