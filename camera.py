import time
import sys

# Try some OpenCV and Picamera
try:
	import cv2
	import picamera
	from picamera.array import PiRGBArray
	from picamera import PiCamera
except:
	pass

rawCapture = None
picamera = None

def startCamera():
	global rawCapture, picamera
	try:
		picamera = PiCamera()
		picamera.resolution = (160, 128)
		rawCapture = PiRGBArray(picamera, size=(160, 128))
	except:
		picamera = None

def saveFrame(filepath):
	global picamera
	picamera.start_preview()
	picamera.capture(filepath)

def getFrame():
	global rawCapture, picamera
	if rawCapture:
		rawCapture.truncate(0)
		picamera.capture(rawCapture, format="rgb") #, resize=(640, 360))
		return rawCapture.array

def showFrame(image):
	cv2.imshow( "Image", image )
	cv2.waitKey(0)

startCamera()

