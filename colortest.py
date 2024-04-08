#!/usr/bin/env pybricks-micropython
#imports
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction
from pybricks.tools import wait
import time


#config.
ev3 = EV3Brick()
gripper = Motor(Port.A)
elbow = Motor(Port.B, Direction.COUNTERCLOCKWISE, [8, 40])
base = Motor(Port.C, Direction.COUNTERCLOCKWISE, [12, 36])
elbow.control.limits(speed=60, acceleration=120)
base.control.limits(speed=60, acceleration=120)

touch = TouchSensor(Port.S1)
rgbsensor = ColorSensor(Port.S2)

#elbow.run_angle(100, 60)

def assign_color():
    red, green, blue= rgbsensor.rgb()

    return red, green, blue

def rgb_to_color(red, green, blue):
    # Define a threshold to determine color dominance
    threshold = 1
    
    # Check if red is dominant
    if red > green + threshold and red > blue + threshold:
        itemcolor="Red"
    # Check if green is dominant
    elif green > red + threshold and green > blue + threshold:
        itemcolor= "Green"
    # Check if blue is dominant
    elif blue > red + threshold and blue > green + threshold:
        itemcolor= "Blue"
        
    else:
        itemcolor= "Other"
    return itemcolor
while True:
    itemcolor=""
    red=0
    green=0
    blue=0
    red, green, blue = assign_color()
    print(red, green , blue)
    itemcolor=rgb_to_color(red, green, blue)
    print(itemcolor)
    time.sleep(0.5)
