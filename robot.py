#!/usr/bin/env pybricks-micropython
# Imports
import json
import time
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Button
from pybricks.tools import wait
from pybricks.media.ev3dev import SoundFile
from umqtt.simple import MQTTClient
import threading
import sys

# Set MQTT broker address, port, username, and password
broker_address = "io.adafruit.com"
broker_port = 1883
username = 'USER'
password = "KEY"

# Constants
FACTORS = {
    'base': 1.05,
    'elbow': 1.0  # Adjust if needed
}

# Initialize EV3 components
ev3 = EV3Brick()
gripper = Motor(Port.A)
elbow = Motor(Port.B, Direction.COUNTERCLOCKWISE, [8, 40])
base = Motor(Port.C, Direction.COUNTERCLOCKWISE, [12, 36])
touch = TouchSensor(Port.S1)
rgbsensor = ColorSensor(Port.S2)

stop_program= False

#threading (threads will execute whenever possible)
def message_check(client):
    client.check_msg()


def emergency_check():
    global stop_program
    while True:
        if Button.UP in ev3.buttons.pressed():
            ev3.speaker.beep()  # Optional: Makes a beep sound when the emergency stop is triggered
            gripper.stop()
            elbow.stop()
            base.stop()
            print("Emergency stop triggered!")
            stop_program = True
            break  # Exit the thread

# Start the emergency_check function in a new thread
threading.Thread(target=emergency_check).start()

# Callback function for when the EV3 is connected to the MQTT broker
def on_connect(client, userdata, flags, rc, topic):
    if rc == 0:
        print("Connected to MQTT broker")
        # Subscribe to the topic where EV3 receives messages from GUI
        client.subscribe(topic)

# Callback function for when a message is received
def on_message(topic, msg):
    global stop_program
    payload = msg.decode("utf-8")
    print("Received message:", payload)
    # Parse the received message and perform corresponding actions
    if payload == "pickup":
        pickup()
    elif payload == "dropoff":
        dropoff()
    elif payload == "EMERGENCY":
        ev3.screen.clear()
        showinfo("EMERGENCY STOP")
        stop_program = True
    # Add more cases as needed

# Function to initialize gripper
def gripper_initial():
    gripper.run_until_stalled(200, then=Stop.COAST, duty_limit=50)
    gripper.reset_angle(0)
    gripper.run_target(200, -90)

# Function to open gripper
def opengripper():
    gripper.run_target(200, -90)

# Function to close gripper
def closegripper():
    gripper.run_target(100, -30, then=Stop.HOLD, wait=True)

# Function to move elbow down
def elbowdown():
    elbow.run_until_stalled(-100, then=Stop.HOLD, duty_limit=25)

# Function to move elbow up
def elbowup():
    elbow.run_angle(200, 63)

# Function to perform pickup operation
def pickup():
    elbowdown()
    closegripper()
    elbowup()

# Function to perform drop-off operation
def dropoff():
    elbowdown()
    opengripper()

# Function to show information on the EV3 screen
def showinfo(thetext):
    ev3.screen.draw_text(50, 50, thetext.upper())

def read_rgb():
    # Read red, green, and blue values from the sensor
    red, green, blue= rgbsensor.rgb()
    return red, green, blue

# Function to assign color based on RGB values
def rgb_to_color(red, green, blue):
    threshold = 3
    
    if red > green + threshold and red > blue + threshold and red > green+blue and green < 7 and blue < 7:
        itemcolor = "Red"
        ev3.speaker.play_file(SoundFile.RED)
    elif green > red and green >= blue:
        itemcolor = "Green"
        ev3.speaker.play_file(SoundFile.GREEN)
    elif blue > red + threshold and blue > green + threshold:
        itemcolor = "Blue"
        ev3.speaker.play_file(SoundFile.BLUE)
    else:
        itemcolor = "Other"
        ev3.speaker.play_file(SoundFile.ERROR_ALARM)
    
    return itemcolor

# Read settings from configuration file
def read_settings():
    try:
        with open('robot_config.json', 'r') as file:
            config_data = json.load(file)
            
            # Initialize an empty dictionary to store variables
            settings_dict = {}
            
            # Process colours data
            colours_data = config_data.get('colours', {})
            settings_dict['sorting_red'] = colours_data.get('sort_red', False)
            settings_dict['sorting_green'] = colours_data.get('sort_green', False)
            settings_dict['sorting_blue'] = colours_data.get('sort_blue', False)

            elevate_data = config_data.get('elevate', {})
            settings_dict['z1_altitude'] = 65 if elevate_data.get('z1') else 0
            settings_dict['z2_altitude'] = 65 if elevate_data.get('z2') else 0
            settings_dict['z3_altitude'] = 65 if elevate_data.get('z3') else 0
            settings_dict['z4_altitude'] = 65 if elevate_data.get('z4') else 0


            # Process auto_assign_zones data
            auto_assign_zones_data = config_data.get('auto_assign_zones', {})
            settings_dict['pickuppoint_auto'] = auto_assign_zones_data.get('pickuppoint_auto', 1)
            if settings_dict['pickuppoint_auto'] == 1:
                settings_dict['red_auto']= 2
                settings_dict['green_auto']= 3
                settings_dict['blue_auto']= 4
            
            elif settings_dict['pickuppoint_auto'] == 2:
                settings_dict['red_auto']= 1
                settings_dict['green_auto']= 3
                settings_dict['blue_auto']= 4
            
            elif settings_dict['pickuppoint_auto'] == 3:
                settings_dict['red_auto']= 2
                settings_dict['green_auto']= 1
                settings_dict['blue_auto']= 4

            elif settings_dict['pickuppoint_auto'] == 4:
                settings_dict['red_auto']= 2
                settings_dict['green_auto']= 3
                settings_dict['blue_auto']= 1
        
            
            # Process manual_assign data
            manual_assign_data = config_data.get('manual_assign', {})
            settings_dict['preset'] = manual_assign_data.get('Preset', 'auto')
            settings_dict['pickuppoint_manual'] = manual_assign_data.get('pickuppoint_manual', 0)
            settings_dict['red_manual'] = manual_assign_data.get('red_manual', 0)
            settings_dict['green_manual'] = manual_assign_data.get('green_manual', 0)
            settings_dict['blue_manual'] = manual_assign_data.get('blue_manual', 0)
            
            return settings_dict
                
    except FileNotFoundError:
        print("Error: File 'robot_config.json' not found.")


# Function to sort item to red zone
def sort_to_red(settings_dict):
    global red_zone
    if settings_dict['sorting_red'] == True:
        red_zone = settings_dict['red_manual'] if settings_dict['preset'].lower() == 'manual' else settings_dict['red_auto']
        base_target = {1: 10, 2: 100, 3: 145, 4: 190}.get(red_zone, 0) * FACTORS['base']
        elbow_target = (30) + settings_dict.get('z' + str(red_zone) + '_altitude', 0 * FACTORS['elbow'])
        base.run_target(200, base_target)
        elbow.run_target(200, elbow_target)
    else:
        elbowdown()

# Function to sort item to green zone
def sort_to_green(settings_dict):
    global green_zone
    if settings_dict['sorting_green'] == True:
        green_zone = settings_dict['green_manual'] if settings_dict['preset'].lower() == 'manual' else settings_dict['green_auto']
        base_target = {1: 10, 2: 100, 3: 145, 4: 190}.get(green_zone, 0) * FACTORS['base']
        elbow_target = (30) + settings_dict.get('z' + str(green_zone) + '_altitude', 0 * FACTORS['elbow'])
        base.run_target(200, base_target)
        elbow.run_target(200, elbow_target)
    else:
        elbowdown()

# Function to sort item to blue zone
def sort_to_blue(settings_dict):
    global blue_zone
    if settings_dict['sorting_blue'] == True:
        blue_zone = settings_dict['blue_manual'] if settings_dict['preset'].lower() == 'manual' else settings_dict['blue_auto']
        base_target = {1: 10, 2: 100, 3: 145, 4: 190}.get(blue_zone, 0) * FACTORS['base']
        elbow_target = (30) + settings_dict.get('z' + str(blue_zone) + '_altitude', 0 * FACTORS['elbow'])
        base.run_target(200, base_target)
        elbow.run_target(200, elbow_target)
    else:
        elbowdown()

# Function to return to pickup point
def goback(settings_dict):
    global pickup_point
    pickup_point = settings_dict.get('pickuppoint_auto') if settings_dict.get('preset').lower() == 'auto' else settings_dict.get('pickuppoint_manual', 1)
    base_target = {1: 10, 2: 100, 3: 145, 4: 190}.get(pickup_point, 0) * FACTORS['base']
    elbow_target = (30) + settings_dict.get('z' + str(pickup_point) + '_altitude', 0 * FACTORS['elbow'])
    elbow.run_target(200, elbow_target)
    base.run_target(200, -base_target)

# Function for sorting items based on color
def sort_item(itemcolor, settings_dict):
    if itemcolor == "Red":
        sort_to_red(settings_dict)
    elif itemcolor == "Green":
        sort_to_green(settings_dict)
    elif itemcolor == "Blue":
        sort_to_blue(settings_dict)
    else:
        dropoff()

# Function to calibrate angle
def angle_calibration():
    if touch.pressed() == True:
        while touch.pressed == True:
            base.run(20)
        base.reset_angle(1)
    else:
        while touch.pressed() == False:
            base.run(-20)
        base.reset_angle(0)
    base.run_target(100, 10, then=Stop.HOLD, wait=True)

def start_on_pickup_zone(settings_dict):
    # Move the arm to the pickup zone
    elbowup()  # Lift the elbow
    pickup_zone = settings_dict.get('pickuppoint_auto') if settings_dict.get('preset').lower() == 'auto' else settings_dict.get('pickuppoint_manual', 1)
    base_target = {1: 10, 2: 100, 3: 145, 4: 190}.get(pickup_zone, 0) * FACTORS['base']
    elbow_target = 0 + settings_dict.get('z' + str(pickup_zone) + '_altitude', 0 * FACTORS['elbow'])
    base.run_target(200, base_target)
    elbow.run_target(200, elbow_target)
    pass

# Initialize MQTT client globally
mqtt_client = None

# Initialize settings dictionary
settings_dict = read_settings()
# Initialize MQTT client
mqtt_client = MQTTClient(username, broker_address, broker_port, username, password)
mqtt_client.set_callback(on_message)
mqtt_client.connect()

threading.Thread(target=mqtt_client.check_msg).start()
# Calibration and initialization
angle_calibration()
gripper_initial()
elbow.run_until_stalled(-100, then=Stop.HOLD, duty_limit=25)
elbow.reset_angle(0)
for key, value in settings_dict.items():
    print(key, value)

# Call start_on_pickup_zone after initializing mqtt_client
start_on_pickup_zone(settings_dict)



topic= TOPIC

showinfo("Connected to MQTT broker")
# Main loop
while True:
    if stop_program:
        sys.exit()
    else:
        while True:
            # Position the arm to pick up the item
            pickup()
            if stop_program: break

            # Read RGB values and determine item color
            itemcolor = ""
            red, green, blue = read_rgb()
            itemcolor = rgb_to_color(red, green, blue)
            mqtt_client.publish(topic, itemcolor)
            showinfo(itemcolor)
            if stop_program: break

            # Sort the item based on its color
            sort_item(itemcolor, settings_dict)
            if stop_program: break

            # Drop off the sorted item
            dropoff()
            if stop_program: break
            start_on_pickup_zone(settings_dict)

            if stop_program: break

            # Clear the EV3 screen and wait before continuing
            ev3.screen.clear()
            time.sleep(0.1)
            if stop_program: break
