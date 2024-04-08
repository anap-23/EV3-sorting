#!/usr/bin/env pybricks-micropython
#imports
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction
from pybricks.tools import wait
import time
faktor= 1.15

#config.
ev3 = EV3Brick()
gripper = Motor(Port.A)
elbow = Motor(Port.B, Direction.COUNTERCLOCKWISE, [8, 40])
base = Motor(Port.C, Direction.COUNTERCLOCKWISE, [12, 36])
elbow.control.limits(speed=100, acceleration=120)
base.control.limits(speed=100, acceleration=120)

touch = TouchSensor(Port.S1)
rgbsensor = ColorSensor(Port.S2)


base.run_angle(100, 90)
print(touch.pressed())
while touch.pressed() == False:
    base.run(-20)
'''
def gripper_initial():
    gripper.run_until_stalled(200, then=Stop.COAST, duty_limit=50)
    gripper.reset_angle(0)
    gripper.run_target(200, -90)
def opengripper():
    gripper.run_target(200, -90)

def closegripper():
    gripper.run_until_stalled(200, then=Stop.HOLD, duty_limit=50)

gripper_initial()
opengripper()
time.sleep(3)
closegripper()
print(gripper.angle())
'''