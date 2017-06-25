import sys
import time
import functions
import asyncio
import websockets
from threading import Thread

# Export x and y
x = 0
y = 0
done = False

# Start thread and create new event loop
loop = asyncio.new_event_loop()
def thread_function(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
thread = Thread(target=thread_function, args=(loop,))
thread.start()    

# Coroutine for websocket handling
@asyncio.coroutine
def remote_connect():
    global x, y
    print( "\nConnecting." )
    try:
        websocket = yield from websockets.connect("ws://meetzippy.com:8080")
        print( "\nConnected to server." )
    except:
        print( "\nNo internet." )
        return

    # Loop
    try:
        while not done:
            text = yield from websocket.recv()
            if text.startswith( 'x' ):
                x = int(text.split()[1])
#                print( "\nX: " + str( x ) + "" )
            if text.startswith( 'y' ):
                y = int(text.split()[1])
#                print( "Y: " + str( y ) + "\n" )
    finally:
        yield from websocket.close()
    print( "Remote done" )

# Run coroutine
loop.call_soon_threadsafe(asyncio.async, remote_connect())


#try:
#	import thread
#	thread.start_new_thread( remote_listener, () )
#except:
#	print( "Error: Cannot start remote listener. Please install python threads." )
