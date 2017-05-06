# -------------
# Betabot functions
import time
import sys

def clamp(n, smallest, largest):
	return max(smallest, min(n, largest))

# Read angles from sensors
def readCurrentAngles( sensors ):
	currentAngles = [0] * 4
	try:
		for i in range(len(currentAngles)):
			currentAngles[i] = 360.0 * sensors.getAngle(i+1) / 16384.0
	except:
		return currentAngles
	return currentAngles

# Motor speeds can go from -100 to 100
def clampMotorSpeeds(motorSpeeds):
	minSpeed = -100
	maxSpeed = 100
	for i in range(len(motorSpeeds)):
		motorSpeeds[i] = clamp(motorSpeeds[i], minSpeed, maxSpeed)
	return motorSpeeds

# Send the motor speeds to the motors
# And enable the motors if any have any speed
motorEnablePin = 18 # Broadcom 18 = pin 12, 6 from the top corner on the outside of the Pi
goTime = 0
MultiWii = None
try:
	from controller_board import MultiWii
except:
	pass
board = None

def initMotors():
	global board
	try:
		board = MultiWii("/dev/ttyUSB0")
	except:
		print( "Error: Cannot access motors." )

	# Motor enable pin
	try:
		import RPi.GPIO as GPIO
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(motorEnablePin, GPIO.OUT)
		GPIO.output(motorEnablePin, GPIO.LOW)

		# Test
		if( False ):
			time.sleep( 0.2 )
			sys.stdout.write("\r\x1b[KTest: Motors on." )
			GPIO.output(motorEnablePin, GPIO.HIGH)
			time.sleep( 2 )
			sys.stdout.write("\r\x1b[KTest: Motors off." )
			GPIO.output(motorEnablePin, GPIO.LOW)
			time.sleep( 1 )
			sys.stdout.write("\n" )

	except:
		print( "Error: Cannot access GPIO." )
		print( sys.exc_info() )


def readIMU():
	global board
	board.getData(MultiWii.RAW_IMU)
	return board

def sendMotorSpeeds(motorSpeedsIn):
	global goTime, board
	motorSpeeds = [0] * 4
	
	# Any motor speeds?
	for i in range(len(motorSpeedsIn)):
		motorSpeeds[i] = int(motorSpeedsIn[i])
		if( (i != 2 ) and (motorSpeeds[i] > 1 or motorSpeeds[i] < -1 ) ):
			# Set used time as now
			go = True
			goTime = time.time()*1000
			
	# Motors been on for five seconds unused?
	if time.time()*1000 > goTime + 2000:
		go = False

	# Send
	middle = 992 + 500
	scale = 5
	rcChannels = [motorSpeeds[0]*scale+middle, motorSpeeds[1]*scale+middle, motorSpeeds[2]*scale+middle, motorSpeeds[3]*scale+middle, 1000, 1000, 1000, 1000]
	try:
#		print( rcChannels )
		board.sendCMD(16, MultiWii.SET_RAW_RC, rcChannels)

	except Exception as error:
#		print( "Error sending: " + str(error) )
		pass

	try:
		import RPi.GPIO as GPIO
		global motorEnablePin
		if( go ):
			GPIO.output(motorEnablePin, GPIO.HIGH)
		else:
			GPIO.output(motorEnablePin, GPIO.LOW)
	except:
		pass

