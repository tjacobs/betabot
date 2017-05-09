import time
import sys

mouse_x = 0
mouse_y = 0

def on_move(x, y):
	global mouse_x, mouse_y
	mouse_x = x
	mouse_y = y

def on_click(x, y, button, pressed):
	return

def on_scroll(x, y, dx, dy):
	return

def mouse_listener():
	print( "Using mouse." )
	try:
		from pynput.mouse import Listener
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
