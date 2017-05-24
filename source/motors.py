# -------------
# Motor functions
import time
import sys
import functions

# Motor speeds can go from -100 to 100
def clampMotorSpeeds(motorSpeeds):
	minSpeed = -100.0
	maxSpeed = 100.0
	for i in range(len(motorSpeeds)):
		motorSpeeds[i] = functions.clamp(motorSpeeds[i], minSpeed, maxSpeed)
	return motorSpeeds

def readIMU(xy='ax'):
	global board
	if board == None:
		return 0
	board.getData(MultiWii.RAW_IMU)
	return board.rawIMU[xy] # Pitch

# Init
simulator = None
motorEnablePin = 18 # Broadcom 18 = pin 12, 6 from the top corner on the outside of the Pi
goTime = 0
MultiWii = None
board = None
try:
	from controller_board import MultiWii
except:
	pass

# Init motors
def initMotors():
	global board
	try:
		board = MultiWii("/dev/ttyUSB0")
	except:
		try:
			board = MultiWii("/dev/ttyACM0")
		except:
			try:
				board = MultiWii("/dev/ttyACM1")
			except:
#				print( "\nError: Cannot access USB motors." )
				sys.stdout.flush()

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
#		print( "Error: Cannot access GPIO." )
#		print( sys.exc_info() )
		sys.stdout.flush()

# Send the motor speeds to the motors, and enable the motors if any have any speed
def sendMotorSpeeds(motorSpeedsIn, simulator=None, displayChannels=False, displayCommands=False):
	global goTime, board, motorEnablePin
	motorSpeeds = [0.0] * 9
	
	# Any motor speeds?
	for i in range(len(motorSpeedsIn)):
		motorSpeeds[i] = motorSpeedsIn[i]
		if motorSpeeds[i] > 1 or motorSpeeds[i] < -1:
			# Set used time as now
			go = True
			goTime = time.time()*1000

	# Leave disabled
	if False:
		# Test all motor commands
		sineOffset += 10.0
		motorSpeeds[1] = math.sin(sineOffset/100.0)*100.0 # Right hip
		motorSpeeds[2] = math.sin(sineOffset/100.0)*100.0 # Left hip
		motorSpeeds[3] = math.sin(sineOffset/100.0)*100.0 # Right knee servo
		motorSpeeds[4] = math.sin(sineOffset/100.0)*100.0 # Left knee servo
		motorSpeeds[5] = math.sin(sineOffset/100.0)*100.0 # Right foot servo
		motorSpeeds[6] = math.sin(sineOffset/100.0)*100.0 # Left foot servo
		motorSpeeds[7] = math.sin(sineOffset/100.0)*100.0 # Unused
		motorSpeeds[8] = math.sin(sineOffset/100.0)*100.0 # Unused
			
	# Motors been on for two seconds unused?
	if time.time()*1000 > goTime + 2000:
		go = False

	# Display?
	if( displayCommands ):
		functions.display( "Motors: %3d, %3d, %1f, %1f, %1f, %1f" % (motorSpeeds[1], motorSpeeds[2], motorSpeeds[3], motorSpeeds[4], motorSpeeds[5], motorSpeeds[6] ) )

	# Send
	middle = 1000.0 + 500.0 #+ 5
	scale = 5.0
	motorSpeeds = clampMotorSpeeds(motorSpeeds)
	channels = [motorSpeeds[1]*scale+middle,
				motorSpeeds[2]*scale+middle,
				motorSpeeds[4]*scale+middle, # Why be these flipped, betaflight throttle
				motorSpeeds[3]*scale+middle,
				motorSpeeds[5]*scale+middle,
				motorSpeeds[6]*scale+middle,
				motorSpeeds[7]*scale+middle,
				motorSpeeds[8]*scale+middle]
	if( displayChannels ):
		functions.display( "Channels: " + str( channels ) )
	try:
		board.sendCMD(16, MultiWii.SET_RAW_RC, channels)
	except Exception as error:
		initMotors()

	# Set enable pin
	try:
		import RPi.GPIO as GPIO
		if( go ):
			GPIO.output(motorEnablePin, GPIO.HIGH)
		else:
			GPIO.output(motorEnablePin, GPIO.LOW)
	except:
		pass

	# Update simulator
	if simulator and simulator.simulator:
		simulator.simulator.simStep(motorSpeeds)
