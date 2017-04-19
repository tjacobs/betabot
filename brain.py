import time
import sys

# Keyboard handling
up_key_pressed = False
down_key_pressed = False
left_key_pressed = False
right_key_pressed = False

def brain():
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
