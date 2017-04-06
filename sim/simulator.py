import pybullet as p
import time
import math

# Simulator constants
useRealTime = 0
fixedTimeStep = 0.01
speed = 10

# Tunable Betabot behaviour
maxForce = 50.0
kp = 2.0
kd = 0.1

# Motor directions
motordir=[1, 1]

# Useful for quarter turns
halfpi = 1.57079632679

# Connect
print( "" )
print( "GPU info:" )
p.connect(p.GUI)

# Set up physics
p.setPhysicsEngineParameter(numSolverIterations=50)
p.setGravity(0, 0, 0)
p.setTimeStep(fixedTimeStep)
p.setRealTimeSimulation(0)

# Load the ground
p.loadURDF("data/plane.urdf", 0, 0, 0)

# Load some rocks
#p.loadURDF("data/rock.urdf", 0, 0, 0)

# Load model
betabot = p.loadURDF("../betabot_ws/src/betabot_description/urdf/betabot.urdf", [1, 0, 0.2], p.getQuaternionFromEuler([0, 0, 0.1]), useFixedBase=False)

# Map joint names to ids
nJoints = p.getNumJoints(betabot)
jointNameToId = {}
for i in range(nJoints):
	jointInfo=p.getJointInfo(betabot, i)
	jointNameToId[jointInfo[1].decode('UTF-8')] = jointInfo[0]

# Make nice names of joints
right_wheel_joint = jointNameToId['right_wheel_joint']
left_wheel_joint = jointNameToId['left_wheel_joint']

# Reset joints
p.resetJointState(betabot, right_wheel_joint, motordir[0] * halfpi)
p.resetJointState(betabot, left_wheel_joint, motordir[1] * halfpi)
p.setJointMotorControl(betabot, right_wheel_joint, p.VELOCITY_CONTROL, 0, 0.0)
p.setJointMotorControl(betabot, left_wheel_joint, p.VELOCITY_CONTROL, 0, 0.0)

# Gravity go! (a moon)
p.setGravity(0, 0, -9.8 / 1.0)
    
# Real time?
p.setRealTimeSimulation(useRealTime)

# Start
print( "" )
print( "Running Betabot simulator. Press 'g' in simulator for full view." )
t = 0.0
t_end = t + 10000.0
reference_time = time.time()
try:
	while t < t_end:
		# Calculate time step
		if (useRealTime):
			t = time.time() - reference_time
		else:
			t = t + fixedTimeStep

		# Move joints
		target_left = t * speed * 10.0;
		target_right = t * speed * 0.1;
#		print( target )
		p.setJointMotorControl2(bodyIndex=betabot, jointIndex=right_wheel_joint, controlMode=p.POSITION_CONTROL, targetPosition=motordir[0]*target_left, positionGain=kp, velocityGain=kd, force=maxForce)
		p.setJointMotorControl2(bodyIndex=betabot, jointIndex=left_wheel_joint,  controlMode=p.POSITION_CONTROL, targetPosition=motordir[1]*target_right, positionGain=kp, velocityGain=kd, force=maxForce)

		# Step if not real time
		if (useRealTime==0):
			p.stepSimulation()
			time.sleep(fixedTimeStep)
except:
	print( "Exited." )

# Done
print( "Done." )
