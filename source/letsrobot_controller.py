import platform
import os
import uuid
import urllib.request, urllib.error, urllib.parse
import json
import traceback
import tempfile
import time
import atexit
import sys
import _thread
import subprocess
import datetime
from socketIO_client import SocketIO, LoggingNamespace
import argparse
from threading import Thread

# Exports
forward = False
backward = False
left = False
right = False

parser = argparse.ArgumentParser(description='start robot control program')
#parser.add_argument('robot_id', help='Robot ID')
parser.add_argument('--env', help="Environment for example dev or prod, prod is default", default='prod')
parser.add_argument('--type', help="serial or motor_hat or gopigo or l298n or motozero", default='motor_hat')
parser.add_argument('--serial-device', help="serial device", default='/dev/ttyACM0')
parser.add_argument('--male', dest='male', action='store_true')
parser.add_argument('--female', dest='male', action='store_false')
parser.add_argument('--voice-number', type=int, default=1)
parser.add_argument('--led', help="Type of LED for example max7219", default=None)
parser.add_argument('--ledrotate', help="Rotates the LED matrix. Example: 180", default=None)
parser.add_argument('--tts-volume', type=int, default=80)
parser.add_argument('--secret-key', default=None)
parser.add_argument('--turn-delay', type=float, default=0.4)
parser.add_argument('--straight-delay', type=float, default=0.5)
parser.add_argument('--driving-speed', type=int, default=90)
parser.add_argument('--night-speed', type=int, default=170)
parser.add_argument('--forward', default='[-1,1,-1,1]')
parser.add_argument('--left', default='[1,1,1,1]')
parser.add_argument('--festival-tts', dest='festival_tts', action='store_true')
parser.set_defaults(festival_tts=False)

commandArgs = parser.parse_args()
print(commandArgs)

chargeIONumber = 17
robotID = "86663988" #commandArgs.robot_id

# Enable watchdog timer
os.system("sudo modprobe bcm2835_wdt")
os.system("sudo /usr/sbin/service watchdog start")

# Set volume level
if commandArgs.tts_volume > 50:
    os.system("amixer set PCM -- -100")
os.system("amixer -c 2 cset numid=3 %d%%" % commandArgs.tts_volume)

# Temp dir
tempDir = tempfile.gettempdir()

steeringSpeed = 90
steeringHoldingSpeed = 90
global drivingSpeed
drivingSpeed = commandArgs.driving_speed
handlingCommand = False

if commandArgs.env == 'dev':
    print('DEV MODE ***************')
    print("using dev port 8122")
    port = 8122
elif commandArgs.env == 'prod':
    port = 8022
else:
    print("invalid environment")
    sys.exit(0)

# Connect
server = "runmyrobot.com"
socketIO = SocketIO(server, port, LoggingNamespace)
print('Connected to', server)

def times(lst, number):
    return [x*number for x in lst]

forward = json.loads(commandArgs.forward)
backward = times(forward, -1)
left = json.loads(commandArgs.left)
right = times(left, -1)
straightDelay = commandArgs.straight_delay 
turnDelay = commandArgs.turn_delay

#Change sleeptime to adjust driving speed
#Change rotatetimes to adjust the rotation. Will be multiplicated with sleeptime.
l298n_sleeptime=0.2
l298n_rotatetimes=5
    
def handle_exclusive_control(args):
        if 'status' in args and 'robot_id' in args and args['robot_id'] == robotID:

            status = args['status']

        if status == 'start':
                print("start exclusive control")
        if status == 'end':
                print("end exclusive control")

def handle_chat_message(args):

    # Write to file
    print("Chat message received:", args)
    rawMessage = args['message']
    withoutName = rawMessage.split(']')[1:]
    message = "".join(withoutName)
    tempFilePath = os.path.join(tempDir, "text_" + str(uuid.uuid4()))
    f = open(tempFilePath, "w")
    f.write(message)
    f.close()

    # Speak    
    if commandArgs.festival_tts:
        os.system('festival --tts < ' + tempFilePath)
    else:
        # espeak tts
        for hardwareNumber in (2, 0, 1):
            if commandArgs.male:
                os.system('cat ' + tempFilePath + ' | espeak --stdout | aplay -D plughw:%d,0' % hardwareNumber)
            else:
                os.system('cat ' + tempFilePath + ' | espeak -ven-us+f%d -s170 --stdout | aplay -D plughw:%d,0' % (commandArgs.voice_number, hardwareNumber))
    os.remove(tempFilePath)

def handle_command(args):
        global left, right, forward, backward
        now = datetime.datetime.now()
        now_time = now.time()

        drivingSpeedActuallyUsed = 250

        global drivingSpeed
        global handlingCommand

        #print( "received command:", str(args) )
        # Note: If you are adding features to your bot,
        # you can get direct access to incomming commands right here.

        if handlingCommand:
            return

        handlingCommand = True

        #if 'robot_id' in args:
        #    print "args robot id:", args['robot_id']

        #if 'command' in args:
        #    print "args command:", args['command']
     
        if 'command' in args and 'robot_id' in args and args['robot_id'] == robotID:

            print('Got command', args)
            command = args['command']

            if commandArgs.type == 'motor_hat':

                if command == 'F':
                    print( "Forward" )
                    forward = True
                    time.sleep(straightDelay)
                if command == 'B':
                    print( "Backward" )
                    backward = True
                    time.sleep(straightDelay)
                if command == 'L':
                    print( "Left" )
                    left = True
                    time.sleep(turnDelay)
                if command == 'R':
                    print( "Right" )
                    right = True
                    time.sleep(turnDelay)
                if command == 'U':
                    incrementArmServo(1, 10)
                    time.sleep(0.05)
                if command == 'D':
                    incrementArmServo(1, -10)
                    time.sleep(0.05)
                if command == 'O':
                    incrementArmServo(2, -10)
                    time.sleep(0.05)
                if command == 'C':
                    incrementArmServo(2, 10)
                    time.sleep(0.05)

            if commandArgs.type == 'motor_hat':
                left = False
                right = False
                forward = False
                backward = False
                pass
                #turnOffMotors()

            if commandArgs.led == 'max7219':
                if command == 'LED_OFF':
                    SetLED_Off()
                if command == 'LED_FULL':
                    SetLED_On()
                    SetLED_Full()
                if command == 'LED_MED':
                    SetLED_On()
                    SetLED_Med()
                if command == 'LED_LOW':
                    SetLED_On()
                    SetLED_Low()
                if command == 'LED_E_SMILEY':
                    SetLED_On()
                    SetLED_E_Smiley()
                if command == 'LED_E_SAD':
                    SetLED_On()
                    SetLED_E_Sad()
                if command == 'LED_E_TONGUE':
                    SetLED_On()
                    SetLED_E_Tongue()
                if command == 'LED_E_SUPRISED':
                    SetLED_On()
                    SetLED_E_Suprised()
        handlingCommand = False


def handleStartReverseSshProcess(args):
    print("starting reverse ssh")
    socketIO.emit("reverse_ssh_info", "starting")
    returnCode = subprocess.call(["/usr/bin/ssh", "-X", "-i", "/home/pi/reverse_ssh_key1.pem", "-N", "-R", "2222:localhost:22", "ubuntu@52.52.204.174"])
    socketIO.emit("reverse_ssh_info", "return code: " + str(returnCode))
    print("reverse ssh process has exited with code", str(returnCode))
    
def handleEndReverseSshProcess(args):
    print("handling end reverse ssh process")
    resultCode = subprocess.call(["killall", "ssh"])
    print("result code of killall ssh:", resultCode)

def on_handle_command(*args):
   _thread.start_new_thread(handle_command, args)

def on_handle_exclusive_control(*args):
   _thread.start_new_thread(handle_exclusive_control, args)

def on_handle_chat_message(*args):
   _thread.start_new_thread(handle_chat_message, args)
   
socketIO.on('command_to_robot', on_handle_command)
socketIO.on('exclusive_control', on_handle_exclusive_control)
socketIO.on('chat_message_with_name', on_handle_chat_message)

def startReverseSshProcess(*args):
   _thread.start_new_thread(handleStartReverseSshProcess, args)

def endReverseSshProcess(*args):
   _thread.start_new_thread(handleEndReverseSshProcess, args)

socketIO.on('reverse_ssh_8872381747239', startReverseSshProcess)
socketIO.on('end_reverse_ssh_8872381747239', endReverseSshProcess)

def myWait():
  socketIO.wait()
  _thread.start_new_thread(myWait, ())
    
def ipInfoUpdate():
    socketIO.emit('ip_information',
                  {'ip': subprocess.check_output(["hostname", "-I"]), 'robot_id': robotID})

def sendChargeState():
    charging = 0 #GPIO.input(chargeIONumber) == 1
    chargeState = {'robot_id': robotID, 'charging': charging}
    socketIO.emit('charge_state', chargeState)
    print("charge state:", chargeState)

def sendChargeStateCallback(x):
    sendChargeState()

def identifyRobotId():
    socketIO.emit('identify_robot_id', robotID);


identifyRobotId()

if platform.system() == 'Darwin':
    pass
elif platform.system() == 'Linux':
    ipInfoUpdate()

def robot_listener():
    waitCounter = 0
    while True:
        socketIO.wait(seconds=10)
        if (waitCounter % 10) == 0:

            # Tell the server what robot id is using this connection
            identifyRobotId()
            
            if platform.system() == 'Linux':
                ipInfoUpdate()

            if commandArgs.type == 'motor_hat':
                sendChargeState()

        waitCounter += 1

thread = Thread(target=robot_listener, args=())
thread.start()    
