import face_recognition
import picamera
import numpy as np

# Start camera
camera = picamera.PiCamera()
camera.resolution = (320, 240)
output = np.empty((240, 320, 3), dtype=np.uint8)

# Initialize some variables
face_locations = []
while True:
    # Grab a single frame of video from the camera as a numpy array    
    camera.capture(output, format="rgb")
    
    # Find the faces and in the current frame of video
    face_locations = face_recognition.face_locations(output)
    print("Found {} faces in image.".format(len(face_locations)))

    for face_location in face_locations:
        # Print the location of each face in this image
        top, right, bottom, left = face_location
        print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))

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


