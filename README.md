# Betabot

Work in progress for a walking robot.

[See here.](https://www.instagram.com/p/BRC_-dfhfe6/?taken-by=tomjacobs83)

Example code:


		stepStages, targetAngles = updateTargetAngles(stepStages)
		currentAngles = readCurrentAngles()
		P = calculateP(currentAngles, targetAngles)
		motorSpeeds = clampMotorSpeeds(P)
		sendMotorSpeeds(sbus, motorSpeeds, arm)
