import time
import sys
import cv2
import keras
import camera
import brain_model

# This is how we output our will, for now
up_key_pressed = False
down_key_pressed = False
left_key_pressed = False
right_key_pressed = False
left_velocity = 0
right_velocity = 0

def brain():
	global left_velocity, right_velocity

	# Turn off our brain for now
	return False

	# Load our brain
	model_path = "brain.model"
	try:
		model = keras.models.load_model( model_path )
	except:
		print( "Error loading brain. That could be a problem." )
		print( sys.exc_info() )
		pass

	# Brain loop
	while True:
		# What can we see?
		frame = camera.getFrame()
		#camera.showFrame( frame )
		
		# Use our brain
		outputs = model.predict( frame[None, :, :, :] )
		left_v, right_v = outputs[0]
		left_velocity = left_v * 1.0
		right_velocity = right_v * 1.0
		#print( "\nRight: " + str( right_velocity ) + "  Left: " + str( left_velocity ) )
		if right_v > left_v:
			print( "Right. " )
		else:
			print( "Left. " )
		
	print( "Brain done" )

	
# Rename this to brain() for some simple movement
def old_brain():
	global up_key_pressed, down_key_pressed, left_key_pressed, right_key_pressed
	
	# Start
	print( "Starting brain." )
	time.sleep( 4 )
	while True:
		print( "\nForward" )
		up_key_pressed = True
		time.sleep( 5 )

		print( "\nStop" )
		up_key_pressed = False
		print( "\nTurn right" )
		right_key_pressed = True
		time.sleep( 3 )

		print( "\nStop" )
		right_key_pressed = False
		time.sleep( 5 )

try:
	import thread
	thread.start_new_thread( brain, () )
except:
	print( "Error: Cannot start brain. That's a problem." )
	print( sys.exc_info() )
