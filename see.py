import camera
import time
import cv2
import cv_helpers

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
	combined_binary, stacked_binary, gradx_binary, grady_binary, mag_binary, dir_binary = cv_helpers.threshold( frame )
	#thresholded_saturation_image = cv_helpers.hls_select(frame, thresh=(40, 255))

	# Show
	cv2.imshow( "preview", stacked_binary )

	# Esc key?
	key = cv2.waitKey(20)
	if key == 27:
		break

# Close
cv2.destroyWindow( "preview" )
