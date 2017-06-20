import sys
import time
from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketServerProtocol, WebSocketClientFactory
import functions

speedL = 0
speedR = 0
buttonUp = False
buttonDown = False
buttonLeft = False
buttonRight = False
x = 0
y = 0

class BotClient(WebSocketClientProtocol):

	def onConnect(self, response):
		print("Server connected: {0}".format(response.peer))

	def onOpen(self):
		print("WebSocket connection open.")

		def loop():
			global buttonUp, buttonDown, buttonLeft, buttonRight
			global speedL, speedR
			minSpeed = -100
			maxSpeed = 100
			if buttonUp:
				speedL = functions.clamp( speedL + 30, 1, maxSpeed )
				speedR = functions.clamp( speedR + 30, 1, maxSpeed )
			if buttonDown:
				speedL = functions.clamp( speedL - 30, minSpeed, -1 )
				speedR = functions.clamp( speedR - 30, minSpeed, -1 )
			if buttonLeft:
				speedL = functions.clamp( speedL - 35, minSpeed, -1 )
				speedR = functions.clamp( speedR + 35, 1, maxSpeed )
			if buttonRight:
				speedL = functions.clamp( speedL + 35, 1, maxSpeed )
				speedR = functions.clamp( speedR - 35, minSpeed, -1 )
			print( speedL, speedR )

			# Slow down
			speedL = functions.clamp( 0.7 * speedL, -100, 100 )
			speedR = functions.clamp( 0.7 * speedR, -100, 100 )

			# Loop
			self.factory.loop.call_later(0.1, loop)

#		loop()

	def onMessage(self, payload, isBinary):
		global buttonUp, buttonDown, buttonLeft, buttonRight
		global speedL, speedR
		global x, y

		if isBinary:
			print("Binary message received: {0} bytes".format(len(payload)))
		else:
			text = payload.decode('utf8')
			if text.startswith( 'x' ):
				x = text.split()[1]
				print( x )
			if text.startswith( 'y' ):
				y = text.split()[1]
				print( y )
			if text == 'up':
				print( "Forward" )
				buttonUp = True
			if text == 'up-release':
				buttonUp = False
			if text == 'down':
				print( "Back" )
				buttonDown = True
			if text == 'down-release':
				buttonDown = False
			if text == 'left':
				print( "Left" )
				buttonLeft = True
			if text == 'left-release':
				buttonLeft = False
			if text == 'right':
				print( "Right" )
				buttonRight = True
			if text == 'right-release':
				buttonRight = False

	def onClose(self, wasClean, code, reason):
		print("WebSocket connection closed: {0}".format(reason))


# Import websockets
import asyncio

# Start websocket client
factory = WebSocketClientFactory(u"ws://meetzippy.com:8080")
factory.protocol = BotClient

# Connect
def remote_listener():
	
#	loop = asyncio.new_event_loop()	
#	asyncio.set_event_loop(loop)
	
	loop = asyncio.get_event_loop()
	coro = loop.create_connection(factory, 'meetzippy.com', 8080)
	loop.run_until_complete(coro)
	
	
	try:
		import thread
		thread.start_new_thread( loop.run_forever, () )
	except:
		print( "Error: Cannot start remote listener. Please install python threads." )


	loop.close()

remote_listener()

