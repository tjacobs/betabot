			# Calculate how much the motor has moved in the last 100ms
			if time.time()*1000 > lastCheck + 100:
				lastCheck = time.time()*1000
				moved = currentAngles[0] - lastAngles[0]
				if( moved > 16384 - 5000 ):
					moved = moved - 16384
				if( moved < -(16384 - 5000) ):
					moved = moved + 16384
				percentageMoved = abs( moved / 30.0 )				
				percentagePower = abs(lastLastMotorSpeeds[0])
				
				# Record values for next check
				lastAngles[0] = currentAngles[0]
				lastLastMotorSpeeds[0] = lastMotorSpeeds[0]
				lastMotorSpeeds[0] = motorSpeeds[0]

				# Did we hit something?
#				percentageExpectedMoved = percentagePower
				#print "MOVED " + str( int( percentageMoved)) + "   POWER " + str( int(percentageExpectedMoved))
#				if( percentagePower > 30 and motorSpeeds[0] > 30 and percentageMoved < percentageExpectedMoved * 0.6 and hit == False):
#					print( "OW!" )
#					hit = True

#			motorSpeeds[0] = 10
#			motorSpeeds[1] = -motorSpeeds[1]


#~ sess = tf.Session()
#~ def network(x):
#~ 
	#~ # Fully Connected.
    #~ fc_W  = tf.Variable(tf.truncated_normal(shape=(n_legs, n_params), mean = 0, stddev = 0.1))
    #~ fc_b  = tf.Variable(tf.zeros(n_params))
    #~ output = tf.matmul(x, fc_W) + fc_b
    #~ return tf.sigmoid( output )

		#~ x_in = [[1]]
		#~ x = tf.placeholder(tf.float32, (1, 1))
		#~ input = network(x)
		#~ sess.run(tf.global_variables_initializer())
		    #~ # What does our brain say to do?
			#~ x_in[0][0] = x_in[0][0] + 0.1
			#~ output = sess.run(input, feed_dict={x:x_in})
			#~ print( output )

