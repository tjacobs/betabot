import time
import sys

# Keyboard handling
up_key_pressed = False
down_key_pressed = False
left_key_pressed = False
right_key_pressed = False
esc_key_pressed = False

def keyboard_hook(key):
	global up_key_pressed, down_key_pressed, left_key_pressed, right_key_pressed, esc_key_pressed
	pressed = True
	if key.event_type == "up":
		pressed = False
	print( key.event_type )
	if key.name == "up":
		up_key_pressed = pressed
	if key.name == "down":
		down_key_pressed = pressed
	if key.name == "left":
		left_key_pressed = pressed
	if key.name == "right":
		right_key_pressed = pressed

def on_press(key):
	global up_key_pressed, down_key_pressed, left_key_pressed, right_key_pressed, esc_key_pressed
	from pynput import keyboard
	if( key == keyboard.Key.up ): up_key_pressed = True
	if( key == keyboard.Key.down ): down_key_pressed = True
	if( key == keyboard.Key.left ): left_key_pressed = True
	if( key == keyboard.Key.right ): right_key_pressed = True
	if( key == keyboard.Key.esc ): esc_key_pressed = True

def on_release(key):
	global up_key_pressed, down_key_pressed, left_key_pressed, right_key_pressed, esc_key_pressed
	from pynput import keyboard
	if( key == keyboard.Key.up ): up_key_pressed = False
	if( key == keyboard.Key.down ): down_key_pressed = False
	if( key == keyboard.Key.left ): left_key_pressed = False
	if( key == keyboard.Key.right ): right_key_pressed = False
	if( key == keyboard.Key.esc ): esc_key_pressed = False

def keyboard_listener():
	print( "Using keyboard." )

	USE_PYNPUT = True
		
	if( USE_PYNPUT ):
		try:
			from pynput import keyboard
			with keyboard.Listener(
					on_press=on_press,
					on_release=on_release) as listener:
				listener.join()
		except:
			print( "Error: Cannot access keyboard. Please install pynput and linux desktop." )
			print( sys.exc_info() )
	else:
		try:
			import keyboard
			keyboard.hook( keyboard_hook )
		except:
			print( "Error: Cannot access keyboard." ) # Pip install keyboard, run with sudo 
			print( sys.exc_info() )

try:
	import thread
	thread.start_new_thread( keyboard_listener, () )
except:
	print( "Error: Cannot start keyboard listener. Please install python threads." )
