import sys
import math
import numpy as np
import Box2D
from Box2D.b2 import edgeShape, circleShape, fixtureDef, polygonShape, revoluteJointDef, contactListener
import gym
from gym import spaces
from gym.utils import colorize, seeding
from gym.envs.classic_control import rendering

# World
FPS        = 60
SCALE      = 80
VIEWPORT_W = 1200
VIEWPORT_H = 700

# Betabot
MOTORS_TORQUE  = 100
SPEED_HIP      = 2
SPEED_KNEE     = 4
SPEED_FOOT     = 4
HULL_POLY =[
    (-20, 120), (+10, 120), (+10, 0),
    (+10, -30), (-20, -30)
    ]
LEG_DOWN = -32/SCALE
LEG_W, LEG_H = 32/SCALE, 138/SCALE
LIDAR_RANGE    = 160/SCALE

# Terrain
TERRAIN_STEP   = 14/SCALE
TERRAIN_LENGTH = 200     # in steps
TERRAIN_HEIGHT = VIEWPORT_H/SCALE/4
TERRAIN_GRASS    = 10    # low long are grass spots, in steps
TERRAIN_STARTPAD = 100    # in steps
FRICTION = 2.5

class ContactDetector(contactListener):
    def __init__(self, env):
        contactListener.__init__(self)
        self.env = env
    def BeginContact(self, contact):
        #if self.env.hull in [contact.fixtureA.body, contact.fixtureB.body]:
            #self.env.game_over = True
        for leg in [self.env.legs[1], self.env.legs[3]]:
            if leg in [contact.fixtureA.body, contact.fixtureB.body]:
                leg.ground_contact = True
    def EndContact(self, contact):
        for leg in [self.env.legs[1], self.env.legs[3]]:
            if leg in [contact.fixtureA.body, contact.fixtureB.body]:
                leg.ground_contact = False

class BipedalWalker(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second' : FPS
    }

    def __init__(self):
        self._seed()
        self.viewer = None

        # World
        self.world = Box2D.b2World()

        # Terrain and bot
        self.terrain = None
        self.hull = None

        # Reset
        self.prev_shaping = None
        self._reset()

        # Input and output to the env: actions and observations
        high = np.array([np.inf]*28)
        self.action_space = spaces.Box(np.array([-1,-1,-1,-1,-1,-1]), np.array([+1,+1,+1,+1,+1,+1]))
        self.observation_space = spaces.Box(-high, high)

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _destroy(self):
        if not self.terrain: return
        self.world.contactListener = None
        for t in self.terrain:
            self.world.DestroyBody(t)
        self.terrain = []
        self.world.DestroyBody(self.hull)
        self.hull = None
        for leg in self.legs:
            self.world.DestroyBody(leg)
        self.legs = []
        self.joints = []

    def _generate_terrain(self, hardcore):
        GRASS, STUMP, STAIRS, PIT, _STATES_ = range(5)
        state    = GRASS
        velocity = 0.0
        y        = TERRAIN_HEIGHT
        counter  = TERRAIN_STARTPAD
        oneshot  = False
        self.terrain   = []
        self.terrain_x = []
        self.terrain_y = []
        for i in range(TERRAIN_LENGTH):
            x = i*TERRAIN_STEP
            self.terrain_x.append(x)

            if state==GRASS and not oneshot:
                velocity = 0.8*velocity + 0.01*np.sign(TERRAIN_HEIGHT - y)
                if i > TERRAIN_STARTPAD: velocity += self.np_random.uniform(-1, 1)/SCALE   #1
                y += velocity

            elif state==PIT and oneshot:
                counter = self.np_random.randint(3, 5)
                poly = [
                    (x,              y),
                    (x+TERRAIN_STEP, y),
                    (x+TERRAIN_STEP, y-4*TERRAIN_STEP),
                    (x,              y-4*TERRAIN_STEP),
                    ]
                t = self.world.CreateStaticBody(
                    fixtures = fixtureDef(
                        shape=polygonShape(vertices=poly),
                        friction = FRICTION
                    ))
                t.color1, t.color2 = (1,1,1), (0.6,0.6,0.6)
                self.terrain.append(t)
                t = self.world.CreateStaticBody(
                    fixtures = fixtureDef(
                        shape=polygonShape(vertices=[(p[0]+TERRAIN_STEP*counter,p[1]) for p in poly]),
                        friction = FRICTION
                    ))
                t.color1, t.color2 = (1,1,1), (0.6,0.6,0.6)
                self.terrain.append(t)
                counter += 2
                original_y = y

            elif state==PIT and not oneshot:
                y = original_y
                if counter > 1:
                    y -= 4*TERRAIN_STEP

            elif state==STUMP and oneshot:
                counter = self.np_random.randint(1, 3)
                poly = [
                    (x,                      y),
                    (x+counter*TERRAIN_STEP, y),
                    (x+counter*TERRAIN_STEP, y+counter*TERRAIN_STEP),
                    (x,                      y+counter*TERRAIN_STEP),
                    ]
                t = self.world.CreateStaticBody(
                    fixtures = fixtureDef(
                        shape=polygonShape(vertices=poly),
                        friction = FRICTION
                    ))
                t.color1, t.color2 = (1,1,1), (0.6,0.6,0.6)
                self.terrain.append(t)

            elif state==STAIRS and oneshot:
                stair_height = +1 if self.np_random.rand() > 0.5 else -1
                stair_width = self.np_random.randint(4, 5)
                stair_steps = self.np_random.randint(3, 5)
                original_y = y
                for s in range(stair_steps):
                    poly = [
                        (x+(    s*stair_width)*TERRAIN_STEP, y+(   s*stair_height)*TERRAIN_STEP),
                        (x+((1+s)*stair_width)*TERRAIN_STEP, y+(   s*stair_height)*TERRAIN_STEP),
                        (x+((1+s)*stair_width)*TERRAIN_STEP, y+(-1+s*stair_height)*TERRAIN_STEP),
                        (x+(    s*stair_width)*TERRAIN_STEP, y+(-1+s*stair_height)*TERRAIN_STEP),
                        ]
                    t = self.world.CreateStaticBody(
                        fixtures = fixtureDef(
                            shape=polygonShape(vertices=poly),
                            friction = FRICTION
                        ))
                    t.color1, t.color2 = (1,1,1), (0.6,0.6,0.6)
                    self.terrain.append(t)
                counter = stair_steps*stair_width

            elif state==STAIRS and not oneshot:
                s = stair_steps*stair_width - counter - stair_height
                n = s/stair_width
                y = original_y + (n*stair_height)*TERRAIN_STEP

            oneshot = False
            self.terrain_y.append(y)
            counter -= 1
            if counter==0:
                counter = self.np_random.randint(TERRAIN_GRASS/2, TERRAIN_GRASS)
                if state==GRASS and hardcore:
                    state = self.np_random.randint(1, _STATES_)
                    oneshot = True
                else:
                    state = GRASS
                    oneshot = True

        self.terrain_poly = []
        for i in range(TERRAIN_LENGTH-1):
            poly = [
                (self.terrain_x[i],   self.terrain_y[i]),
                (self.terrain_x[i+1], self.terrain_y[i+1])
                ]
            t = self.world.CreateStaticBody(
                fixtures = fixtureDef(
                    shape=edgeShape(vertices=poly),
                    friction = FRICTION,
                    categoryBits=0x0001,
                ))
            color = (0.3, 1.0 if i%2==0 else 0.8, 0.3)
            t.color1 = color
            t.color2 = color
            self.terrain.append(t)
            color = (0.4, 0.6, 0.3)
            poly += [ (poly[1][0], 0), (poly[0][0], 0) ]
            self.terrain_poly.append( (poly, color) )
        self.terrain.reverse()

    def _generate_clouds(self):
        self.cloud_poly   = []
        for i in range(TERRAIN_LENGTH//10):
            x = self.np_random.uniform(0, TERRAIN_LENGTH)*TERRAIN_STEP
            y = VIEWPORT_H/SCALE*0.9
            poly = [
                (x+15*TERRAIN_STEP*math.sin(3.14*2*a/5)+self.np_random.uniform(0,5*TERRAIN_STEP),
                 y+ 5*TERRAIN_STEP*math.cos(3.14*2*a/5)+self.np_random.uniform(0,5*TERRAIN_STEP) )
                for a in range(5) ]
            x1 = min( [p[0] for p in poly] )
            x2 = max( [p[0] for p in poly] )
            self.cloud_poly.append( (poly,x1,x2) )

    def _reset(self):
        self._destroy()
        self.world.contactListener_bug_workaround = ContactDetector(self)
        self.world.contactListener = self.world.contactListener_bug_workaround
        self.game_over = False
        self.prev_shaping = None
        self.scroll = 0.0
        self.lidar_render = 0

        # Create world
        self._generate_terrain(hardcore=False)
        self._generate_clouds()

        # Create body
        init_x = TERRAIN_STEP*TERRAIN_STARTPAD/2
        init_y = TERRAIN_HEIGHT+2*LEG_H
        self.hull = self.world.CreateDynamicBody(
            position = (init_x, init_y),
            fixtures = fixtureDef(
                shape=polygonShape(vertices=[ (x/SCALE,y/SCALE) for x,y in HULL_POLY ]),
                density=0.4,
                friction=0.1,
                categoryBits=0x0020,
                maskBits=0x001,  # collide only with ground
                restitution=0.0) # 0.99 bouncy
                )
        self.hull.color1 = (0.3, 0.4, 0.9)
        self.hull.color2 = (0.3, 0.4, 0.7)

        # Create legs
        self.legs = []
        self.joints = []
        for i in [-1, 1]:

            # Upper leg
            leg = self.world.CreateDynamicBody(
                position = (init_x, init_y - LEG_H/2 - LEG_DOWN),
                angle = (i*0.01),
                fixtures = fixtureDef(
                    shape=polygonShape(box=(LEG_W/2, LEG_H/2)),
                    density=0.2,
                    restitution=0.0,
                    categoryBits=0x0020,
                    maskBits=0x001)
                )
            leg.color1 = (0.3-i/10, 0.4-i/10, 0.8-i/10)
            leg.color2 = (0.3, 0.4, 0.5)
            rjd = revoluteJointDef(
                bodyA=self.hull,
                bodyB=leg,
                localAnchorA=(0, LEG_DOWN),
                localAnchorB=(0, LEG_H/2),
                enableMotor=True,
                enableLimit=True,
                maxMotorTorque=MOTORS_TORQUE,
                motorSpeed = i,
                lowerAngle = -1.1,
                upperAngle = 1.3,
                )
            self.legs.append(leg)
            self.joints.append(self.world.CreateJoint(rjd))

            # Lower leg
            lower = self.world.CreateDynamicBody(
                position = (init_x, init_y - LEG_H*3/2 - LEG_DOWN),
                angle = (i*0.01),
                fixtures = fixtureDef(
                    shape=polygonShape(box=(0.8*LEG_W/2, LEG_H/2)),
                    density=0.2,
                    restitution=0.0,
                    categoryBits=0x0020,
                    maskBits=0x001)
                )
            lower.color1 = (0.3-i/10., 0.4-i/10., 0.8-i/10.)
            lower.color2 = (0.3-i/10., 0.4-i/10., 0.5-i/10.)
            rjd = revoluteJointDef(
                bodyA=leg,
                bodyB=lower,
                localAnchorA=(0, -LEG_H/2),
                localAnchorB=(0, LEG_H/2),
                enableMotor=True,
                enableLimit=True,
                maxMotorTorque=MOTORS_TORQUE,
                motorSpeed = 1,
                lowerAngle = -2.8,
                upperAngle = 0.2,
                )
            lower.ground_contact = False
            self.legs.append(lower)
            self.joints.append(self.world.CreateJoint(rjd))

            # Feet
            foot = self.world.CreateDynamicBody(
                position = (init_x+4, init_y - LEG_H*3/2 - LEG_DOWN*0.5),
                angle = 0,
                fixtures = fixtureDef(
                    shape=polygonShape(box=(0.8*LEG_H/2, LEG_W/2)),
                    density=1.5,
                    restitution=0.0,
                    categoryBits=0x0020,
                    maskBits=0x001)
                )
            foot.color1 = (0.3-i/10., 0.3-i/10., 0.8-i/10.)
            foot.color2 = (0.3-i/10., 0.3-i/10., 0.8-i/10.)
            rjd = revoluteJointDef(
                bodyA=lower,
                bodyB=foot,
                localAnchorA=(0, -LEG_H/2),
                localAnchorB=(-0.1, 0),
                enableMotor=True,
                enableLimit=True,
                maxMotorTorque=MOTORS_TORQUE,
                motorSpeed = 1,
                lowerAngle = -1.0,
                upperAngle = 1.0,
                )
            foot.ground_contact = False
            self.legs.append(foot)
            self.joints.append(self.world.CreateJoint(rjd))

        # We render this
        self.drawlist = self.terrain + self.legs + [self.hull]

        # Lidar
        class LidarCallback(Box2D.b2.rayCastCallback):
            def ReportFixture(self, fixture, point, normal, fraction):
                if (fixture.filterData.categoryBits & 1) == 0:
                    return 1
                self.p2 = point
                self.fraction = fraction
                return 0
        self.lidar = [LidarCallback() for _ in range(10)]

        # Start
        return self._step(np.array([0,0,0,0,0,0]))[0]

    def _step(self, action):
        
        # Balance
#        self.hull.ApplyForceToCenter((0, 100), True)

        # Apply torques
        self.joints[0].motorSpeed     = float(SPEED_HIP     * np.sign(action[0]))
        self.joints[0].maxMotorTorque = float(MOTORS_TORQUE * np.clip(np.abs(action[0]), 0, 1))
        self.joints[1].motorSpeed     = float(SPEED_KNEE    * np.sign(action[1]))
        self.joints[1].maxMotorTorque = float(MOTORS_TORQUE * np.clip(np.abs(action[1]), 0, 1))
        self.joints[2].motorSpeed     = float(SPEED_FOOT    * np.sign(action[4]))
        self.joints[2].maxMotorTorque = float(MOTORS_TORQUE * np.clip(np.abs(action[4]), 0, 1))
        self.joints[3].motorSpeed     = float(SPEED_HIP     * np.sign(action[2]))
        self.joints[3].maxMotorTorque = float(MOTORS_TORQUE * np.clip(np.abs(action[2]), 0, 1))
        self.joints[4].motorSpeed     = float(SPEED_FOOT    * np.sign(action[3]))
        self.joints[4].maxMotorTorque = float(MOTORS_TORQUE * np.clip(np.abs(action[3]), 0, 1))
        self.joints[5].motorSpeed     = float(SPEED_KNEE    * np.sign(action[5]))
        self.joints[5].maxMotorTorque = float(MOTORS_TORQUE * np.clip(np.abs(action[5]), 0, 1))

        # Step
        self.world.Step(1.0/FPS, 6*30, 2*30)

        # Get bot position and velocity
        pos = self.hull.position
        vel = self.hull.linearVelocity

        # Lidar
        for i in range(10):
            self.lidar[i].fraction = 1.0
            self.lidar[i].p1 = pos
            self.lidar[i].p2 = (
                pos[0] + math.sin(1.5*i/10.0)*LIDAR_RANGE,
                pos[1] - math.cos(1.5*i/10.0)*LIDAR_RANGE)
            self.world.RayCast(self.lidar[i], self.lidar[i].p1, self.lidar[i].p2)

        # Assemble state
        state = [
            self.hull.angle,                     # 0: Body angle
            2.0*self.hull.angularVelocity/FPS,   # 1: Body angular velocity
            0.3*vel.x*(VIEWPORT_W/SCALE)/FPS,    # 2: Body x velocity
            0.3*vel.y*(VIEWPORT_H/SCALE)/FPS,    # 3: Body y velocity
            self.joints[0].angle,                # 4: Leg hip angle
            self.joints[0].speed / SPEED_HIP,    # 5: Leg hip angular velocity
            self.joints[1].angle + 1.0,          # 6: Leg knee angle
            self.joints[1].speed / SPEED_KNEE,   # 7: Leg knee angular velocity
            1.0 if self.legs[2].ground_contact else 0.0, # 8: Foot hit the ground?
            self.joints[3].angle,                # 9: Leg hip angle
            self.joints[3].speed / SPEED_HIP,    # 10: Leg hip angular velocity
            self.joints[4].angle + 1.0,          # 11: Leg knee angle
            self.joints[4].speed / SPEED_KNEE,   # 12: Leg knee angular velocity
            1.0 if self.legs[5].ground_contact else 0.0, # 13: Foot hit the ground?
            self.joints[2].angle,                # 14: Foot angle
            self.joints[5].angle,                # 15: Foot angle
            self.joints[2].speed / SPEED_FOOT,    # 16: Foot angular velocity
            self.joints[5].speed / SPEED_FOOT,    # 17: Foot angular velocity
            ]

        # Add lidar to state
        state += [l.fraction for l in self.lidar]
        assert len(state)==28

        # Scroll to robot
        self.scroll = pos.x - VIEWPORT_W/SCALE/5

        # Rewards
        shaping  = 130*pos[0]/SCALE   # Moving forward is a way to receive reward (normalized to get 300 on completion)
        shaping -= 5.0*abs(state[0])  # Keep head straight, other than that and falling, any behavior is unpunished
        reward = 0
        if self.prev_shaping is not None:
            reward = shaping - self.prev_shaping
        self.prev_shaping = shaping

        # Minus rewards for moving
        for a in action:
            reward -= 0.00035 * MOTORS_TORQUE * np.clip(np.abs(a), 0, 1)

        # Done?
        done = False
        if self.game_over or pos[0] < -2:
            reward = -100
            done   = True
        if pos[0] > (TERRAIN_LENGTH-TERRAIN_GRASS)*TERRAIN_STEP:
            done   = True
        return np.array(state), reward, done, {}

    def _render(self, mode='human', close=False):
        if close:
            if self.viewer is not None:
                self.viewer.close()
                self.viewer = None
            return

        # Open window
        if self.viewer is None:
            self.viewer = rendering.Viewer(VIEWPORT_W, VIEWPORT_H)
        self.viewer.set_bounds(self.scroll, VIEWPORT_W/SCALE + self.scroll, 0, VIEWPORT_H/SCALE)

        # Draw the world
        self.viewer.draw_polygon( [
            (self.scroll,                  0),
            (self.scroll+VIEWPORT_W/SCALE, 0),
            (self.scroll+VIEWPORT_W/SCALE, VIEWPORT_H/SCALE),
            (self.scroll,                  VIEWPORT_H/SCALE),
            ], color=(0.9, 0.9, 1.0) )
        for poly, x1, x2 in self.cloud_poly:
            if x2 < self.scroll/2: continue
            if x1 > self.scroll/2 + VIEWPORT_W/SCALE: continue
            self.viewer.draw_polygon( [(p[0]+self.scroll/2, p[1]) for p in poly], color=(1,1,1))
        for poly, color in self.terrain_poly:
            if poly[1][0] < self.scroll: continue
            if poly[0][0] > self.scroll + VIEWPORT_W/SCALE: continue
            self.viewer.draw_polygon(poly, color=color)

        # Draw the bot
        for obj in self.drawlist:
            for f in obj.fixtures:
                trans = f.body.transform
                if type(f.shape) is circleShape:
                    t = rendering.Transform(translation=trans*f.shape.pos)
                    self.viewer.draw_circle(f.shape.radius, 30, color=obj.color1).add_attr(t)
                    self.viewer.draw_circle(f.shape.radius, 30, color=obj.color2, filled=False, linewidth=2).add_attr(t)
                else:
                    path = [trans*v for v in f.shape.vertices]
                    self.viewer.draw_polygon(path, color=obj.color1)
                    path.append(path[0])
                    self.viewer.draw_polyline(path, color=obj.color2, linewidth=2)

        # Draw the terrain
        flagy1 = TERRAIN_HEIGHT
        flagy2 = flagy1 + 50/SCALE
        x = TERRAIN_STEP*3
        self.viewer.draw_polyline( [(x, flagy1), (x, flagy2)], color=(0,0,0), linewidth=2 )
        f = [(x, flagy2), (x, flagy2-10/SCALE), (x+25/SCALE, flagy2-5/SCALE)]
        self.viewer.draw_polygon(f, color=(0.9,0.2,0) )
        self.viewer.draw_polyline(f + [f[0]], color=(0,0,0), linewidth=2 )

        # Render
        return self.viewer.render(return_rgb_array = mode=='rgb_array')

# Go
if __name__=="__main__":

    # Create
    env = BipedalWalker()
    state = env.reset()

    # Tunable constants
    SPEED = 1.0

    # States
    LEFT_FOOT_STANCE, RIGHT_FOOT_DOWN, RIGHT_FOOT_STANCE, LEFT_FOOT_DOWN = 1, 2, 3, 4
    walk_state = LEFT_FOOT_STANCE
    right_leg = 0
    left_leg   = 1

    # Counts
    steps = 0
    total_reward = 0
    time = 0

    # Loop
    for t in range(1800):

        # Render
        if True:
            env.render()

        # Which indicies are the angles for the legs
        left_hip_angle_index      = 4
        right_leg_hip_angle_index = 9

        # Targets
        hip_target  = [None, None] 
        knee_target = [None, None] 
        foot_target = [None, None]

        # Timer
        time += 2
        time_mod = time % 1000

        # State to target mapping
        if walk_state == LEFT_FOOT_STANCE:
            # Stand on left leg, straight down
            hip_target[left_leg]  = 0.0
            knee_target[left_leg] = 0.0

            # Curl free leg back
            hip_target[right_leg]  = 0.0
            knee_target[right_leg] = 0.0

            # Feet flat
            foot_target[right_leg] = 0
            foot_target[left_leg] = 0

            # Get up
            if time_mod > 150:
                hip_target[left_leg]  = 1.1
                hip_target[right_leg]  = 1.1
                knee_target[left_leg] = 0.2
                knee_target[right_leg] = 0.2
                foot_target[right_leg] = -0.4
                foot_target[left_leg] = -0.4

            if time_mod > 250:
                foot_target[right_leg] = -0.6
                foot_target[left_leg] = -0.6
                hip_target[left_leg]  = None
                hip_target[right_leg] = None
                knee_target[left_leg] = -1.4
                knee_target[right_leg] = -1.4

            if time_mod > 350:
                hip_target[left_leg]  = 1.9
                hip_target[right_leg] = 1.9
                knee_target[left_leg] = -1.3
                knee_target[right_leg] = -1.3

            if time_mod > 550:
                foot_target[right_leg] = 0.8
                foot_target[left_leg] = 0.8

            if time_mod > 650:
                hip_target[left_leg]  = 0.2
                hip_target[right_leg]  = 0.2
                knee_target[left_leg] =  0.8
                knee_target[right_leg] = 0.8
                foot_target[right_leg] = 0.0
                foot_target[left_leg] = 0.0

            if time_mod > 700:
                hip_target[left_leg]  = 0.2
                hip_target[right_leg]  = 0.2
                knee_target[left_leg] =  0.8
                knee_target[right_leg] = 0.8
                foot_target[right_leg] = 0.1
                foot_target[left_leg] = 0.1

            if time_mod > 800:
                hip_target[left_leg]  = 0.25
                hip_target[right_leg]  = 0.25
                knee_target[left_leg] =  0.9
                knee_target[right_leg] = 0.9
                foot_target[right_leg] = 0.1
                foot_target[left_leg] = 0.1

        elif walk_state == RIGHT_FOOT_DOWN:
            if state[8]:
                print( "Right foot is down." )
                walk_state = RIGHT_FOOT_STANCE

        elif walk_state == RIGHT_FOOT_STANCE:
            # Move right leg forward
            hip_target[right_leg]  = 1.1
            knee_target[right_leg] = -0.6

            hip_target[left_leg]  = -0.2
            knee_target[left_leg] = -0.3

            # Jump!
            if time_mod > 50 and time_mod < 150:
                knee_target[left_leg] = 0.1
                knee_target[right_leg] = -0.1

                # If both legs off the ground, go for the leg flip
#                if not state[8] and not state[13]:
                if time_mod > 150:
                    print( "Flip!" )
                    walk_state = LEFT_FOOT_STANCE
                    time = 200

        elif walk_state == LEFT_FOOT_DOWN:
            if state[13]:
                print( "Left foot is down." )
                walk_state = LEFT_FOOT_STANCE

        # How should we move?
        hip_movement  = [0.0, 0.0]
        knee_movement = [0.0, 0.0]
        foot_movement = [0.0, 0.0]

        # If we have targets, use PD controller to move them there. Kp * anglediff - Kd * velocity
        Kp = 1.5
        Kd = -0.1
        hip_in_world_frame = (state[4] - state[0], state[9] - state[0])
        hip_velocity_in_world_frame = (state[5] - state[1], state[10] - state[1])
        if hip_target[0]:  hip_movement[0]  = Kp * (hip_target[0]  - hip_in_world_frame[0])  + Kd * hip_velocity_in_world_frame[0]
        if knee_target[0]: knee_movement[0] = Kp * (knee_target[0] - state[6])               + Kd * state[7]
        if hip_target[1]:  hip_movement[1]  = Kp * (hip_target[1]  - hip_in_world_frame[1])  + Kd * hip_velocity_in_world_frame[1]
        if knee_target[1]: knee_movement[1] = Kp * (knee_target[1] - state[11])              + Kd * state[12]
        if foot_target[0]: foot_movement[0] = Kp * (foot_target[0] - state[14])              + Kd * state[16]
        if foot_target[1]: foot_movement[1] = Kp * (foot_target[1] - state[15])              + Kd * state[17]

        # Balance. PD controller to adjust hip in world frame to keep balance up straight. Kp * body_angle + Kd * body_angle_velocity.
        kBalanceP = 0.0
        kBalanceD = 0.0
        hip_movement[0] += kBalanceP * state[0] + kBalanceD * state[1]
        hip_movement[1] += kBalanceP * state[0] + kBalanceD * state[1]

        # Dampen bounce. PD controller to adjust knee according to vertical speed, to dampen bouncy oscillations. Kd*body_vertical_velocity.
        kDampen = 0.0
        knee_movement[0] -= kDampen * state[3]
        knee_movement[1] -= kDampen * state[3]

        # Set action
        action = np.array([hip_movement[0], knee_movement[0], hip_movement[1], knee_movement[1], foot_movement[0], foot_movement[1]])
        action = np.clip(action, -1.0, 1.0)
        print( "Torques: Hip %0.2f Knee %0.2f Foot %0.2f     Hip %0.2f Knee %0.2f Foot %0.2f" % (action[0], action[1], action[4], action[2], action[3], action[5] ) )

        # Step
        state, reward, done, info = env.step(action)
        total_reward += reward
        steps += 1

        # Display
        if steps % 200 == 0 or done:
            print("Step {} total_reward {:+0.2f}".format(steps, total_reward))
            print("Hull " + str(["{:+0.2f}".format(x) for x in state[0:4] ]))
            print("Leg 0 " + str(["{:+0.2f}".format(x) for x in state[4:9] ]))
            print("Leg 1 " + str(["{:+0.2f}".format(x) for x in state[9:14]]))

        # Done?
        if done:
            break
