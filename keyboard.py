import time

# Keyboard handling
up_key_pressed = False
down_key_pressed = False
left_key_pressed = False
right_key_pressed = False

def on_press(key):
	global up_key_pressed, down_key_pressed, left_key_pressed, right_key_pressed
	from pynput import keyboard
	if( key == keyboard.Key.up ): up_key_pressed = True
	if( key == keyboard.Key.down ): down_key_pressed = True
	if( key == keyboard.Key.left ): left_key_pressed = True
	if( key == keyboard.Key.right ): right_key_pressed = True

def on_release(key):
	global up_key_pressed, down_key_pressed, left_key_pressed, right_key_pressed
	from pynput import keyboard
	if( key == keyboard.Key.up ): up_key_pressed = False
	if( key == keyboard.Key.down ): down_key_pressed = False
	if( key == keyboard.Key.left ): left_key_pressed = False
	if( key == keyboard.Key.right ): right_key_pressed = False

def keyboard_listener():
	time.sleep( 1 )
	# Collect events until released
	from pynput import keyboard
	print( "Starting keyboard listening." )
	try:
		with keyboard.Listener(
				on_press=on_press,
				on_release=on_release) as listener:
			listener.join()
	except:
		print( "Error: Cannot start keyboard listener. Please run with linux desktop running." )

try:
	import thread
	thread.start_new_thread( keyboard_listener, () )
except:
	print( "Error: Cannot start keyboard listener. Please install python threads." )
