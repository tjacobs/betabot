# Betabot
# https://github.com/tjacobs/betabot
# by Tom Jacobs

print( "Starting Betabot." )

# What shall we enable?
ENABLE_SIMULATOR = False
ENABLE_BRAIN = True
ENABLE_KEYBOARD = True

# Imports
import sys
import time
import math
import array
import datetime
import functions

# Import Betabot I/O
sbus = 0
brain = 0
from sensors import AMS
from sbus import SBUS
if ENABLE_KEYBOARD:
	import keyboard
if ENABLE_BRAIN:
	import brain

# Import simulator
simulator = 0
if ENABLE_SIMULATOR:
	try:
		import sys
		sys.path.append( 'sim' )
		from simulator import Simulator
	except:
		print( "Simulator unavailable." )
		print( sys.exc_info() )

# Variables
armTime = time.time()*1000
motorSpeeds = [0] * 8
motorEnablePin = 18 # Broadcom pin 18

# Go
def main():
		global motorSpeeds, simulator, sbus

		# Motor enable pin
		try:
			import RPi.GPIO as GPIO
			GPIO.setwarnings(False)
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(motorEnablePin, GPIO.OUT)
			GPIO.output(motorEnablePin, GPIO.LOW)

			# Test
			if( True ):
				time.sleep( 0.2 )
				sys.stdout.write("\r\x1b[KTest: Motors on." )
				GPIO.output(motorEnablePin, GPIO.HIGH)
				time.sleep( 2 )
				sys.stdout.write("\r\x1b[KTest: Motors off." )
				GPIO.output(motorEnablePin, GPIO.LOW)
				time.sleep( 1 )
				sys.stdout.write("\n" )

		except:
			print( "Error: No Raspberry Pi GPIO available." )
			print( sys.exc_info() )

		# Talk to motor angle sensors via I2C
		sensors = AMS()
		sensors.connect(1)

		# Talk to motor controller via serial UART SBUS
		sbus = SBUS()
		sbus.connect()

		# Start simulator if loaded
		try:
			simulator = Simulator()
		except:
			pass

		# Init motor speeds
		velocity = 0.0
		velocity_left = 0.0
		velocity_right = 0.0

		# Flush output for file logging
		sys.stdout.flush()

		# Loop
		while not brain.esc_key_pressed:

			# Read current IMU accelerometer X, Y, Z values.
			accelX, accelY, accelZ = sbus.readIMU()

			# Arm after one second
			# TODO: Let controller always arm
			arm = 500
			if time.time()*1000 > armTime + 2000:
				arm = 1000

			# Keyboard/brain moving forward, left, or right?
			if( brain ):
				if( brain.up_key_pressed == True ):   velocity += 0.15
				if( brain.down_key_pressed == True ): velocity -= 0.15
				if( brain.left_key_pressed == True ): velocity_right += 0.3
				if( brain.right_key_pressed == True ): velocity_left += 0.3

			# Calculate left and right wheel velocities
			#R = 0.1 # Radius of wheels
			#L = 0.1 # Linear distance between wheels
			#(2.0 * velocity - heading * L ) / 2.0 * R
			#(2.0 * velocity + heading * L ) / 2.0 * R

			# Update velocity
			velocity = functions.clamp( velocity, -100.0, 100.0 )
			velocity = velocity * 0.998

			# Update left and right velocities
			velocity_left = functions.clamp( velocity_left, -100.0, 100.0 )
			velocity_right = functions.clamp( velocity_right, -100.0, 100.0 )
			velocity_left *= 0.998
			velocity_right *= 0.998

			# Read current wheel rotational angles
			currentAngles = functions.readCurrentAngles(sensors)

			# Send motor speeds
			motorSpeeds[0] = velocity + velocity_left
			motorSpeeds[1] = velocity + velocity_right
			motorSpeeds[3] = 10
			if( velocity > 50 ): motorSpeeds[3] = -10
			motorSpeeds = functions.clampMotorSpeeds(motorSpeeds)
			motorSpeeds[2] = -150 	# Throttle off to enable arming. TODO: Remove
			if( sbus.sbus ):
				functions.sendMotorSpeeds(sbus, motorSpeeds, arm)

 			# Update simulator
			if( simulator ):
				simulator.simStep( motorSpeeds )
			
			# Display wheel angles and speeds
			sys.stdout.write("\r\x1b[KAngles: %3d, %3d, Speeds: %3d, %3d" % 
				(currentAngles[0] / 100, currentAngles[1] / 100, motorSpeeds[0], motorSpeeds[1] ) )
			sys.stdout.flush()
			

		# Finish up
		GPIO.cleanup()


# Go
if __name__=="__main__":
   main()
