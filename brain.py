import time

# Keyboard handling
up_key_pressed = False
down_key_pressed = False
left_key_pressed = False
right_key_pressed = False

def brain():
	global up_key_pressed, down_key_pressed, left_key_pressed, right_key_pressed
	print( "Starting brain." )
	while True:
		up_key_pressed = True
		time.sleep( 3 )

		up_key_pressed = False
		left_key_pressed = True
		time.sleep( 1 )

		right_key_pressed = True
		left_key_pressed = False

		time.sleep( 1 )

		right_key_pressed = False
		time.sleep( 3 )

try:
	import thread
	thread.start_new_thread( brain, () )
except:
	print( "Error: Cannot start brain. That's a problem." )
