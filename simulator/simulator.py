try:
	import pybullet as p
except:
	pass
import time
import math
import sys

class Simulator():
	def __init__(self):
		# Start
		print( "" )
		print( "Starting Betabot simulator. Press 'g' in simulator for full view." )

		# Simulator constants
		self.useRealTime = 1
		self.fixedTimeStep = 0.01
		self.speed = 1

		# Tunable Betabot behaviour
		self.maxForce = 10.0
		self.kp = 0.01
		self.kd = 0.1

		# Motor directions
		self.motordir=[1, 1]

		# Useful for quarter turns
		self.halfpi = 1.57079632679

		# Connect
		print( "" )
		print( "GPU info:" )
		p.connect(p.GUI)

		# Set up physics
		p.setPhysicsEngineParameter(numSolverIterations=50)
		p.setGravity(0, 0, 0)
		p.setTimeStep(self.fixedTimeStep)
		p.setRealTimeSimulation(0)

		# Load the ground
		p.loadURDF("simulator/data/plane.urdf", 0, 0, 0)

		# Load model
		self.betabot = p.loadURDF("ros/src/betabot_description/urdf/betabot.urdf", [0, 0, 2], p.getQuaternionFromEuler([0, 0, 0.1]), useFixedBase=False)

		# Map joint names to ids
		nJoints = p.getNumJoints(self.betabot)
		jointNameToId = {}
		for i in range(nJoints):
			jointInfo=p.getJointInfo(self.betabot, i)
			jointNameToId[jointInfo[1].decode('UTF-8')] = jointInfo[0]

		# Make nice names of joints
		self.right_hip_joint = jointNameToId['right_hip_joint']
		self.left_hip_joint = jointNameToId['left_hip_joint']
		self.right_knee_joint = jointNameToId['right_knee_joint']
		self.left_knee_joint = jointNameToId['left_knee_joint']
		self.right_foot_joint = jointNameToId['right_foot_joint']
		self.left_foot_joint = jointNameToId['left_foot_joint']

		# Gravity go!
		p.setGravity(0, 0, -9.8 / 1.0)
		    
		# Real time?
		p.setRealTimeSimulation(self.useRealTime)

		self.t = 0.0
		self.reference_time = time.time()

	def simStep(self, motorSpeeds):
		# Calculate time step
		if (self.useRealTime):
			self.t = time.time() - self.reference_time
		else:
			self.t = self.t + self.fixedTimeStep

		# Hips
		target_left = motorSpeeds[1] / math.pi 
		target_right = motorSpeeds[2] / math.pi
		p.setJointMotorControl2(bodyIndex=self.betabot, jointIndex=self.right_hip_joint, controlMode=p.POSITION_CONTROL, targetVelocity=self.motordir[0]*target_left, positionGain=self.kp, velocityGain=self.kd, force=self.maxForce)
		p.setJointMotorControl2(bodyIndex=self.betabot, jointIndex=self.left_hip_joint,  controlMode=p.POSITION_CONTROL, targetVelocity=self.motordir[1]*target_right, positionGain=self.kp, velocityGain=self.kd, force=self.maxForce)

		# Knees
		target_left = motorSpeeds[3] / math.pi
		target_right = motorSpeeds[4] / math.pi 
		p.setJointMotorControl2(bodyIndex=self.betabot, jointIndex=self.right_knee_joint, controlMode=p.POSITION_CONTROL, targetVelocity=self.motordir[0]*target_left, positionGain=self.kp, velocityGain=self.kd, force=self.maxForce)
		p.setJointMotorControl2(bodyIndex=self.betabot, jointIndex=self.left_knee_joint,  controlMode=p.POSITION_CONTROL, targetVelocity=self.motordir[1]*target_right, positionGain=self.kp, velocityGain=self.kd, force=self.maxForce)

		# Feet
		target_left = motorSpeeds[5] / math.pi
		target_right = motorSpeeds[6] / math.pi 
		p.setJointMotorControl2(bodyIndex=self.betabot, jointIndex=self.right_foot_joint, controlMode=p.POSITION_CONTROL, targetVelocity=self.motordir[0]*target_left, positionGain=self.kp, velocityGain=self.kd, force=self.maxForce)
		p.setJointMotorControl2(bodyIndex=self.betabot, jointIndex=self.left_foot_joint,  controlMode=p.POSITION_CONTROL, targetVelocity=self.motordir[1]*target_right, positionGain=self.kp, velocityGain=self.kd, force=self.maxForce)

		# Step if not real time
		if (self.useRealTime==0):
			p.stepSimulation()
			time.sleep(self.fixedTimeStep)

simulator = None
try:
	if p:
		simulator = Simulator()
except:
	print( "Simulator unavailable." )
	print( sys.exc_info() )

