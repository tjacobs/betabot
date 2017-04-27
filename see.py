import camera
import time
import cv2

# Create window
cv2.namedWindow( "preview" )
cv2.moveWindow( "preview", 10, 10 )

# Start camera
camera.startCamera( (640, 368) )

# Loop
while True:
	frame = camera.getFrame()
	cv2.imshow( "preview", frame )

	# Esc key?
	key = cv2.waitKey(20)
	if key == 27:
		break

cv2.destroyWindow( "preview" )
