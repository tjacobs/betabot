var WebSocketServer = require('ws').Server
  , wss = new WebSocketServer({ port: 8080 });

var connections = [];

wss.on('connection', function connection(ws) {
  ws.on('message', function incoming(message) {
  
    for( var con in connections ) {
        if( connections[con] != ws ) {
	try{
            connections[con].send( message );
	}
	catch( e ) {
	    console.log( 'oops' );
	}
	}
    }
    console.log('received: %s', message);
  });

    connections.push( ws );
    console.log('Connected!');
	console.log( ws );
});

