import time
import sys
import cv2
import picamera
from picamera.array import PiRGBArray
from picamera import PiCamera

rawCapture = None
picamera = None

def startCamera():
	global rawCapture, picamera
	picamera = PiCamera()
	picamera.resolution = (160, 128)
	rawCapture = PiRGBArray(picamera, size=(160, 128))
	#time.sleep(2)

def saveFrame(filepath):
	global picamera
	picamera.start_preview()
	picamera.capture(filepath)

def getFrame():
	global rawCapture, picamera
	rawCapture.truncate(0)
	picamera.capture(rawCapture, format="rgb") #, resize=(640, 360))
	return rawCapture.array

def showFrame(image):
	cv2.imshow( "Image", image )
	cv2.waitKey(0)

startCamera()

