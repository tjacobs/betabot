import time
import sys
import cv2
import camera

def remember():
	i = 1
	while i < 11 :
		camera.saveFrame( "memories/%05d.jpg" % i )
		i += 1

remember()	
