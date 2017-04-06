import pybullet as p
import time
import math

# Constants
useRealTime = 0
fixedTimeStep = 0.01
speed = 10

# Tunable robot behaviour
amplitude = 0.8
jump_amp = 0.5
maxForce = 3.5
kneeFrictionForce = 0.00
kp = 1
kd = .1

# Motor directions
motordir=[-1, -1]

# How far can we go
kneeangle = -2.1834

# Useful for quarter turns
halfpi = 1.57079632679

# Connect
#physId = p.connect(p.SHARED_MEMORY)
#if (physId<0):
print( "" )
print( "GPU info:" )
p.connect(p.GUI)

# Set up physics
p.setPhysicsEngineParameter(numSolverIterations=50)
p.setGravity(0,0,0)
p.setTimeStep(fixedTimeStep)
p.setRealTimeSimulation(0)

# Load the ground
p.loadURDF("plane.urdf",0,0,0)

# Load model
betabot = p.loadURDF("../betabot_ws/src/betabot_description/urdf/betabot.urdf", [1, 0, 0.2], p.getQuaternionFromEuler([0,0,.4]), useFixedBase=False)

# Map joint names to ids
nJoints = p.getNumJoints(betabot)
jointNameToId = {}
for i in range(nJoints):
	jointInfo=p.getJointInfo(betabot, i)
	jointNameToId[jointInfo[1].decode('UTF-8')] = jointInfo[0]

# Make nice names of joints
right_wheel_joint = jointNameToId['right_wheel_joint']
left_wheel_joint = jointNameToId['left_wheel_joint']

# 
p.resetJointState(betabot, right_wheel_joint, motordir[0] * halfpi)
p.resetJointState(betabot, left_wheel_joint, motordir[1] * halfpi)
#constraintID = p.createConstraint(betabot, right_wheel_joint, betabot, knee_front_leftL_link, p.JOINT_POINT2POINT, [0,0,0], [0,0.005,0.2], [0,0.01,0.2])
#p.changeConstraint(cid,maxForce=10000)
p.setJointMotorControl(betabot, right_wheel_joint, p.VELOCITY_CONTROL, 0, kneeFrictionForce)
p.setJointMotorControl(betabot, left_wheel_joint, p.VELOCITY_CONTROL, 0, kneeFrictionForce)

# Gravity go!
p.setGravity(0, 0, -10)

    
# 
p.setJointMotorControl2(bodyIndex=betabot, jointIndex=right_wheel_joint, controlMode=p.POSITION_CONTROL, targetPosition=motordir[0] * halfpi, positionGain=kp, velocityGain=kd, force=maxForce)
p.setJointMotorControl2(bodyIndex=betabot, jointIndex=left_wheel_joint,  controlMode=p.POSITION_CONTROL, targetPosition=motordir[1] * halfpi, positionGain=kp, velocityGain=kd, force=maxForce)

# Real time
p.setRealTimeSimulation(useRealTime)

# Save
#p.saveWorld("betabot_saved.py")

# Log
#logId = p.startStateLogging(p.STATE_LOGGING_MINITAUR,"betabotLog.txt",[betabot])

# Init move
t = 0.0
t_end = t + 100
i=0
ref_time = time.time()

print( "" )
print( "Running Betabot simulator. Press 'g' in simulator for full view." )

# Move!
while t < t_end:
	if (useRealTime):
		t = time.time() - ref_time
	else:
		t = t + fixedTimeStep

	target = math.sin(t * speed) * jump_amp + halfpi;
	p.setJointMotorControl2(bodyIndex=betabot, jointIndex=right_wheel_joint, controlMode=p.POSITION_CONTROL, targetPosition=motordir[0]*target, positionGain=kp, velocityGain=kd, force=maxForce)
	p.setJointMotorControl2(bodyIndex=betabot, jointIndex=left_wheel_joint, controlMode=p.POSITION_CONTROL, targetPosition=motordir[1]*target, positionGain=kp, velocityGain=kd, force=maxForce)

	if (useRealTime==0):	
		p.stepSimulation()
		time.sleep(fixedTimeStep)

