import pybullet as p
import time
import math

class Simulator():
	def __init__(self):
		# Start
		print( "" )
		print( "Starting Betabot simulator. Press 'g' in simulator for full view." )

		# Simulator constants
		self.useRealTime = 1
		self.fixedTimeStep = 0.01
		self.speed = 10

		# Tunable Betabot behaviour
		self.maxForce = 50.0
		self.kp = 2.0
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
		p.loadURDF("sim/data/plane.urdf", 0, 0, 0)

		# Load a duck
		p.loadURDF("sim/data/duck.urdf", -2, 0, 0.5)

		# Load model
		self.betabot = p.loadURDF("betabot_ws/src/betabot_description/urdf/betabot.urdf", [1, 0, 0.2], p.getQuaternionFromEuler([0, 0, 0.1]), useFixedBase=False)

		# Map joint names to ids
		nJoints = p.getNumJoints(self.betabot)
		jointNameToId = {}
		for i in range(nJoints):
			jointInfo=p.getJointInfo(self.betabot, i)
			jointNameToId[jointInfo[1].decode('UTF-8')] = jointInfo[0]

		# Make nice names of joints
		self.right_wheel_joint = jointNameToId['right_wheel_joint']
		self.left_wheel_joint = jointNameToId['left_wheel_joint']

		# Reset joints
		p.resetJointState(self.betabot, self.right_wheel_joint, self.motordir[0] * self.halfpi)
		p.resetJointState(self.betabot, self.left_wheel_joint, self.motordir[1] * self.halfpi)
		p.setJointMotorControl(self.betabot, self.right_wheel_joint, p.VELOCITY_CONTROL, 0, 0.0)
		p.setJointMotorControl(self.betabot, self.left_wheel_joint, p.VELOCITY_CONTROL, 0, 0.0)

		# Gravity go! (a moon)
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

		# Move joints
		target_left = 0
		target_right = 0

		target_left = motorSpeeds[0] #self.t * self.speed * 10.0;
		target_right = motorSpeeds[1] #self.t * self.speed * 0.1;
		p.setJointMotorControl2(bodyIndex=self.betabot, jointIndex=self.right_wheel_joint, controlMode=p.VELOCITY_CONTROL, targetVelocity=self.motordir[0]*target_left, positionGain=self.kp, velocityGain=self.kd, force=self.maxForce)
		p.setJointMotorControl2(bodyIndex=self.betabot, jointIndex=self.left_wheel_joint,  controlMode=p.VELOCITY_CONTROL, targetVelocity=self.motordir[1]*target_right, positionGain=self.kp, velocityGain=self.kd, force=self.maxForce)

		# Step if not real time
		if (self.useRealTime==0):
			p.stepSimulation()
			time.sleep(self.fixedTimeStep)
