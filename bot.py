# Betabot
# https://github.com/tjacobs/betabot
# by Tom Jacobs

print( "Starting Betabot." )

# What shall we enable?
ENABLE_SIMULATOR = False
ENABLE_BRAIN = False
ENABLE_KEYBOARD = False

# Imports
import sys
import time
import math
import array
import datetime
import functions
import walk


# Import Betabot I/O
sbus = None
brain = None
keyboard = None
from sensors import AMS
from sbus import SBUS
if ENABLE_KEYBOARD:
	import keyboard
if ENABLE_BRAIN:
	import brain

# Import simulator
simulator = None
if ENABLE_SIMULATOR:
	try:
		sys.path.append( 'sim' )
		from simulator import Simulator
		simulator = Simulator()
	except:
		print( "Simulator unavailable." )
		print( sys.exc_info() )

# Variables
armTime = time.time()*1000
motorSpeeds = [0] * 4

# Go
def main():
		global motorSpeeds, simulator, sbus

		# TODO: MOve to motors.py
		# Motor enable pin
		try:
			import RPi.GPIO as GPIO
			GPIO.setwarnings(False)
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(functions.motorEnablePin, GPIO.OUT)
			GPIO.output(functions.motorEnablePin, GPIO.LOW)

			# Test
			if( False ):
				time.sleep( 0.2 )
				sys.stdout.write("\r\x1b[KTest: Motors on." )
				GPIO.output(functions.motorEnablePin, GPIO.HIGH)
				time.sleep( 2 )
				sys.stdout.write("\r\x1b[KTest: Motors off." )
				GPIO.output(functions.motorEnablePin, GPIO.LOW)
				time.sleep( 1 )
				sys.stdout.write("\n" )

		except:
			print( "Error: Missing Raspberry Pi GPIO." )

		# Talk to motor angle sensors via I2C
		sensors = AMS()
		sensors.connect(1)

		# Talk to motor controller via serial UART SBUS
		sbus = SBUS()
		sbus.connect()

		# Init motor speeds
		velocity = 0.0
		velocity_left = 0.0
		velocity_right = 0.0

		# Flush output for file logging
		sys.stdout.flush()

		# Loop
		while not keyboard or not keyboard.esc_key_pressed:

			# Read current IMU accelerometer X, Y, Z values.
			accelX, accelY, accelZ = sbus.readIMU()
#			print( "\n X:" + str( accelX ) )

			# Arm after one second
			# TODO: Let controller always arm
			arm = 500
			if time.time()*1000 > armTime + 2000:
				arm = 1000

			# Keyboard/brain moving forward, left, or right?
			if( brain ):
				if( brain.up_key_pressed == True ):   velocity += 0.15
				if( brain.down_key_pressed == True ): velocity -= 0.15
				if( brain.left_key_pressed == True ):
					velocity_right += 0.3
					velocity_left -= 0.3
				if( brain.right_key_pressed == True ):
					velocity_left += 0.3
					velocity_right -= 0.3
			if( keyboard ):
				if( keyboard.up_key_pressed == True ):   velocity += 0.3
				if( keyboard.down_key_pressed == True ): velocity -= 0.3
				if( keyboard.left_key_pressed == True ): 
					velocity_right += 0.5
					velocity_left -= 0.5
				if( keyboard.right_key_pressed == True ):
					velocity_left += 0.5
					velocity_right -= 0.5

			# Calculate left and right wheel velocities
			#R = 0.1 # Radius of wheels
			#L = 0.1 # Linear distance between wheels
			#(2.0 * velocity - heading * L ) / 2.0 * R
			#(2.0 * velocity + heading * L ) / 2.0 * R

			# Update velocity
			velocity = functions.clamp( velocity, -80.0, 80.0 )
			velocity = velocity * 0.98

			# Update left and right velocities
			velocity_left = functions.clamp( velocity_left, -80.0, 80.0 )
			velocity_right = functions.clamp( velocity_right, -80.0, 80.0 )
			velocity_left *= 0.95
			velocity_right *= 0.95

			# Read current wheel rotational angles
			currentAngles = functions.readCurrentAngles(sensors)
			
			# Figure out where our hips should be
			targetAngles = walk.updateTargetAngles( 10, 0 )
			
			# Run our PID controller
			motorSpeeds = walk.calculateMovement( currentAngles, targetAngles )

			# Send motor speeds
			motorSpeeds[0] = -( velocity + velocity_right )
			motorSpeeds[1] = -( velocity + velocity_left )
			motorSpeeds[3] = 0
			motorSpeeds = functions.clampMotorSpeeds(motorSpeeds)
			motorSpeeds[2] = -150 	# Throttle off to enable arming. TODO: Remove
			functions.sendMotorSpeeds(sbus, motorSpeeds, arm)

 			# Update simulator
			if( simulator ): simulator.simStep( motorSpeeds )
			
			# Display wheel angles and speeds
			sys.stdout.write("\r\x1b[KHip Angles: %3d, %3d, Hip targets: %3d, %3d, Speeds: %3d, %3d" % 
				(currentAngles[0] / 100, currentAngles[1] / 100, targetAngles[0], targetAngles[1], motorSpeeds[0], motorSpeeds[1] ) )
			sys.stdout.flush()
			

		# Finish up
		GPIO.cleanup()


# Go
if __name__=="__main__":
   main()
