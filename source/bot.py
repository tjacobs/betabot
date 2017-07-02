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
import remote

#import letsrobot_controller
#import letsrobot_video

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

	# Motor speeds
	speed_left = 0.0
	speed_right = 0.0
	
	# Remote control
	old_remote_x = 0.0
	old_remote_y = 0.0

	# Wait on other threads to start up
	time.sleep(1)

	# Loop
	while not keys or not keys.esc_key_pressed:

		# Read current accelerometer value to see how far forward we're leaning
		pitch = 0 #motorsModule.readIMU('ax')

		# Read current angles of motors
		#currentAngles = functions.readCurrentAngles(magneticSensors)

		# Run movement controller to see how fast we should set our motor speeds
#		movement = walk.calculateMovement(currentAngles, targetAngles)

		# Calculate difference in mouse x position
		diff_x = remote.x - old_remote_x
		diff_y = remote.y - old_remote_y
		old_remote_x = remote.x
		old_remote_y = remote.y

		FORWARD_SPEED = 20.0
		BACKWARD_SPEED = 20.0
		TURNING_SPEED = 70.0
		MOVEMENT_SPEED = 100.0

		# Change motor speeds for turning left right
		speed_left -= diff_x * TURNING_SPEED / 100.0
		speed_right += diff_x * TURNING_SPEED / 100.0

		# Remote keyboard commands
		if remote.up:
			speed_left = speed_left - FORWARD_SPEED
			speed_right = speed_right - FORWARD_SPEED
		if remote.down:
			speed_left = speed_left + BACKWARD_SPEED
			speed_right = speed_right + BACKWARD_SPEED
		if remote.left:
			speed_left -= 20.0
			speed_right += 20.0
		if remote.right:
			speed_left += 10.0
			speed_right -= 20.0

		# Go forward backward on mouse y
		speed_left += diff_y * MOVEMENT_SPEED / 100.0
		speed_right += diff_y * MOVEMENT_SPEED / 100.0

		# Go foward backward on clicks
		if remote.left_mouse_down:
			speed_left = speed_left - FORWARD_SPEED
			speed_right = speed_right - FORWARD_SPEED
		if remote.right_mouse_down:
			speed_left = speed_left + BACKWARD_SPEED
			speed_right = speed_right + BACKWARD_SPEED

		# Let's Robot controller
		try:
			if letsrobot_controller.forward:
				speed_left = speed_left - FORWARD_SPEED
				speed_right = speed_right - FORWARD_SPEED
			if letsrobot_controller.backward:
				speed_left = speed_left + BACKWARD_SPEED
				speed_right = speed_right + BACKWARD_SPEED
			if letsrobot_controller.left:
				speed_left += 1.0 * TURNING_SPEED / 5.0
				speed_right -= 1.0 * TURNING_SPEED / 5.0
			if letsrobot_controller.right:
				speed_left -= 1.0 * TURNING_SPEED / 5.0
				speed_right += 1.0 * TURNING_SPEED / 5.0
		except NameError:
			pass

		# Slow down
		speed_left = speed_left * 0.75
		speed_right = speed_right * 0.75

		# Clamp
		speed_left = functions.clamp( speed_left, -100, 100)
		speed_right = functions.clamp( speed_right, -100, 100)

		# Send motor commands
		motors[1] = speed_right	#movement[1] 	 # Right motor
		motors[2] = speed_left #movement[2] 	 # Left motor
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
