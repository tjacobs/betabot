import camera
import time
import cv2
import cv_helpers

def process( image ):
	cv2.putText(image, "Betabot", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
	return image

# Create window
cv2.namedWindow( "preview" )
cv2.moveWindow( "preview", 10, 10 )

# Start camera
camera.startCamera( (640, 368) )

# Loop
while True:

	# Get a frame
	frame = camera.getFrame()
	
	# Process
	processed_image = process( frame )

	# Show
	cv2.imshow( "preview", processed_image )

	# Esc key hit?
	key = cv2.waitKey(20)
	if key == 27:
		break

# Close
cv2.destroyWindow( "preview" )
