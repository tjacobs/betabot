import time
import sys

# Init mouse
mouse_x = 0
mouse_y = 0
mouse = None
mouse_x_diff   = 0.0
mouse_y_diff   = 0.0
old_mouse_x    = 0.0
old_mouse_y	   = 0.0
mouse_speed_factor = 1.0

def on_move(x, y):
	global mouse_x, mouse_y, old_mouse_x, old_mouse_y, mouse_x_diff, mouse_y_diff
	mouse_x = x
	mouse_y = y
	#print( "\n" + str( mouse_x ) + " " + str( mouse_y ) )
	
	# Set pointer position
	if( mouse.position[0] > 1000 ):
		mouse.position = (0, mouse.position[1])
	if( mouse.position[1] > 900 ):
		mouse.position = (mouse.position[0], 0)
	if( mouse.position[0] == 0 ):
		mouse.position = (1000, mouse.position[1])
	if( mouse.position[1] == 0 ):
		mouse.position = (mouse.position[0], 900)

	# How much has the mouse moved from last loop?
	mouse_x_diff = mouse_x - old_mouse_x
	mouse_y_diff = mouse_y - old_mouse_y			
	if( mouse_x_diff > 500 ): mouse_x_diff = 0
	if( mouse_x_diff < -500 ): mouse_x_diff = 0
	if( mouse_y_diff > 500 ): mouse_y_diff = 0
	if( mouse_y_diff < -500 ): mouse_y_diff = 0
	old_mouse_x = mouse_x
	old_mouse_y = mouse_y
	mouse_x_diff *= mouse_speed_factor
	mouse_y_diff *= mouse_speed_factor

def on_click(x, y, button, pressed):
	return

def on_scroll(x, y, dx, dy):
	return

def mouse_listener():
	global mouse
	print( "Using mouse." )
	try:
		from pynput.mouse import Listener, Controller
		mouse = Controller()
		with Listener(
				on_move=on_move,
				on_click=on_click,
				on_scroll=on_scroll) as listener:
			listener.join()
	except:
		print( "Error: Cannot access mouse." )
		print( sys.exc_info() )
	return

try:
	import thread
	thread.start_new_thread( mouse_listener, () )
except:
		print( "Error: Cannot start mouse." )
		print( sys.exc_info() )
