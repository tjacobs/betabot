import face_recognition
import camera
import numpy as np
import motors as motorsModule
import matplotlib.image as mpimg
import random
import time

# Start camera
#camera.startCamera( (320, 160) )
output = np.empty((240, 320, 3), dtype=np.uint8)
output = mpimg.imread('face.jpg')

# Init motors
motorsModule.initMotors()
motors = [0.0] * 9

# Initialize some variables
face_locations = []
while True:

    # Grab a single frame of video from the camera as a numpy array    
#    camera.capture(output, format="rgb")
#    frame = camera.getFrame()

    # De-blue
#    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    print( "\nFinding" )
    
    # Find the faces and in the current frame of video
    #face_locations = face_recognition.face_locations(output)
    face_locations =[(10,50+random.randint(0,50), 50+random.randint(0,50), 10)]
    print("Found {} faces in image.".format(len(face_locations)))

    for face_location in face_locations:
        # Print the location of each face in this image
        top, right, bottom, left = face_location
        print("Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))

        # Face center
        face_x = right - left
        face_y = bottom - top

        # Image center
        image_center_x = 320/2
        image_center_y = 240/2

        # How far should we move?
        movement_x = image_center_x - face_x
        movement_y = image_center_y - face_y

        # PID controller
        k_d = 0.1
        p_x = k_d * movement_x
        p_y = k_d * movement_y

        print( "{} {}".format( p_x, p_y ) )

        motors[1] = p_x 
        motors[2] = p_y
        motorsModule.sendMotorCommands(motors, None, False, True)

	break
    time.sleep(5)

