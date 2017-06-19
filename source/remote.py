import sys
import time
from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketServerProtocol, WebSocketClientFactory

speedL = 0
speedR = 0
buttonUp = False
buttonDown = False
buttonLeft = False
buttonRight = False

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
				speedL = numpy.clip( speedL + 30, 1, maxSpeed )
				speedR = numpy.clip( speedR + 30, 1, maxSpeed )
			if buttonDown:
				speedL = numpy.clip( speedL - 30, minSpeed, -1 )
				speedR = numpy.clip( speedR - 30, minSpeed, -1 )
			if buttonLeft:
				speedL = numpy.clip( speedL - 35, minSpeed, -1 )
				speedR = numpy.clip( speedR + 35, 1, maxSpeed )
			if buttonRight:
				speedL = numpy.clip( speedL + 35, 1, maxSpeed )
				speedR = numpy.clip( speedR - 35, minSpeed, -1 )
			print( speedL, speedR )

			# Slow down
			speedL = numpy.clip( 0.7 * speedL, -100, 100 )
			speedR = numpy.clip( 0.7 * speedR, -100, 100 )

			# Loop
			self.factory.loop.call_later(0.1, loop)

		loop()

	def onMessage(self, payload, isBinary):
		global buttonUp, buttonDown, buttonLeft, buttonRight
		global speedL, speedR

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
try:
	import asyncio
except ImportError:
	import trollius as asyncio

# Start websocket client
factory = WebSocketClientFactory(u"ws://meetzippy.com:8080")
factory.protocol = BotClient

# Connect
loop = asyncio.get_event_loop()
coro = loop.create_connection(factory, 'meetzippy.com', 8080)
loop.run_until_complete(coro)
loop.run_forever()
loop.close()
