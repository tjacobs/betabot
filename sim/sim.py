import pybullet as p
from time import sleep 

#physicsClient = p.connect(p.GUI)
p.connect(p.SHARED_MEMORY)

planeId = p.loadURDF( "plane.urdf" )
p.setGravity(0,0,-10)

cubeStartPos = [0,0,1]
cubeStartOrientation = p.getQuaternionFromEuler([0,0,0])
boxId = p.loadURDF("../betabot_ws/src/betabot_description/urdf/betabot.urdf", cubeStartPos, cubeStartOrientation)

p.setRealTimeSimulation(1)

p.disconnect()
