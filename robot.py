#!/usr/bin/env pybricks-micropython
#imports
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction
from pybricks.tools import wait
from pybricks.media.ev3dev import SoundFile, ImageFile
import GUI_edit
import time


faktor=1.15

#config.
ev3 = EV3Brick()
gripper = Motor(Port.A)
elbow = Motor(Port.B, Direction.COUNTERCLOCKWISE, [8, 40])
base = Motor(Port.C, Direction.COUNTERCLOCKWISE, [12, 36])
#elbow.control.limits(speed=100, acceleration=100)
#base.control.limits(speed=200, acceleration=200)

touch = TouchSensor(Port.S1)
rgbsensor = ColorSensor(Port.S2)

def gripper_initial():
    gripper.run_until_stalled(200, then=Stop.COAST, duty_limit=50)
    gripper.reset_angle(0)
    gripper.run_target(200, -90)

def opengripper():
    gripper.run_target(200, -90)

def closegripper():
    gripper.run_target(100, -27, then= Stop.HOLD, wait=True)

def elbowdown():
    elbow.run_until_stalled(-100, then=Stop.HOLD, duty_limit=25)

def elbowup():
    elbow.run_angle(200, 65)

def pickup():
    elbowdown()
    closegripper()
    elbowup()


def dropoff():
    elbowdown()
    opengripper()

def assign_color():
    red, green, blue= rgbsensor.rgb()

    return red, green, blue

def rgb_to_color(red, green, blue):
    # Define a threshold to determine color dominance
    threshold = 3
    
    # Check if red is dominant
    if red > green + threshold and red > blue + threshold and green<3 and blue<3:
        itemcolor="Red"
        ev3.speaker.play_file(SoundFile.RED)
    # Check if green is dominant
    elif green > red and green >= blue:
        itemcolor= "Green"
        ev3.speaker.play_file(SoundFile.GREEN)
    # Check if blue is dominant
    elif blue > red + threshold and blue > green + threshold:
        itemcolor= "Blue"
        ev3.speaker.play_file(SoundFile.BLUE)
    else:
        itemcolor= "Other"
        ev3.speaker.play_file(SoundFile.ERROR_ALARM)
    return itemcolor

#SORTING
def sort_to_red():
    elbow.run_angle(200, 30)
    base.run_angle(200, 93*faktor)
def sort_to_green():
    elbow.run_angle(200, 30)
    base.run_angle(200, 138*faktor)
def sort_to_blue():
    elbow.run_angle(200, 30)
    base.run_angle(200, 183*faktor)

def goback():
    if itemcolor=="Red":
        elbow.run_angle(200, 60)
        base.run_angle(200, -93*faktor)
    elif itemcolor=="Green":
        elbow.run_angle(200, 60)
        base.run_angle(200, -138*faktor)
    elif itemcolor=="Blue":
        elbow.run_angle(200, 60)
        base.run_angle(200, -183*faktor)
    else:
        pass


def sort_item():
    global itemcolor
    if itemcolor=="Red":
        sort_to_red()
    elif itemcolor=="Green":
        sort_to_green()
    elif itemcolor=="Blue":
        sort_to_blue()
    else:
        dropoff()

def angle_calibration():
    if touch.pressed()==True:
        while touch.pressed==True:
            base.run(20)
        base.reset_angle(1)
    else:
        while touch.pressed()== False:
            base.run(-20)
        base.reset_angle(0)


angle_calibration()
GUI_edit.main()
gripper_initial()
z1= 10
z2= 20
z3= 30
z4= 40

while True:
    print(touch.pressed())
    itemcolor=""
    red=0
    green=0
    blue=0
    pickup()
    time.sleep(0.1)
    red, green, blue= assign_color()
    print(red, green , blue)
    itemcolor=rgb_to_color(red, green, blue)
    print(itemcolor)
    sort_item()
    print(touch.pressed())
    dropoff()
    print(touch.pressed())
    goback()
    time.sleep(0.1)

