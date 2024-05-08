#!/usr/bin/env pybricks-micropython
# Imports
import json
import time
import threading
import sys
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Button
from pybricks.tools import wait
from pybricks.media.ev3dev import SoundFile
from umqtt.simple import MQTTClient

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
belt = None
touch = TouchSensor(Port.S1)
rgbsensor = ColorSensor(Port.S2)

stop_program = False
continue_main_loop = True
start = False
button_ctrl = False
activate = False
sensor_ctrl = False
rolling = False

# Global variables for start and end times
start_time = None
end_time = None

# Set MQTT broker address, port, username, and password
broker_address = "io.adafruit.com"
broker_port = 1883
username = 'XXXX'
password = "XXXX"  
topic = b"XXXXX"

custom_base_target = None
custom_elbow_target = None

class RobotState:
    def __init__(self):
        self.gripper_position = None
        self.elbow_position = None
        self.base_position = None

# Create an instance of RobotState to store the state
robot_state = RobotState()

# Function to store robot state
def store_state():
    robot_state.gripper_position = gripper.angle()
    robot_state.elbow_position = elbow.angle()
    robot_state.base_position = base.angle()

# Function to restore robot state
def restore_state():
    gripper.run_target(200, robot_state.gripper_position)
    elbow.run_target(200, robot_state.elbow_position)
    base.run_target(200, robot_state.base_position)

def emergency_check():
    global stop_program, button_ctrl
    while True:
        if sensor_ctrl == False:
            if not button_ctrl:
                if Button.UP in ev3.buttons.pressed():
                    ev3.speaker.beep()  # Optional: Makes a beep sound when the emergency stop is triggered
                    gripper.stop()
                    elbow.stop()
                    base.stop()
                    print("Emergency stop triggered!")
                    stop_program = True
                    break  # Exit the thread
                elif Button.LEFT in ev3.buttons.pressed():
                    pause()

def pause():
    global continue_main_loop, button_ctrl
    ev3.speaker.beep()
    ev3.screen.clear()
    showinfo('PAUSED')
    store_state()
    print("Paused!")
    continue_main_loop = False
    while not continue_main_loop:
        client.check_msg()
        gripper.hold()
        elbow.hold()
        base.hold()
        if sensor_ctrl == False:
            if not button_ctrl:
                if Button.RIGHT in ev3.buttons.pressed():
                    resume()
 
# Function to handle resuming
def resume():
    global continue_main_loop
    print("Resuming...")
    ev3.screen.clear()
    restore_state()
    continue_main_loop = True

# Start the emergency_check function in a new thread
threading.Thread(target=emergency_check).start()

# Callback function for when the EV3 is connected to the MQTT broker
def on_connect(client, userdata, flags, rc, topic):
    if rc == 0:
        print("Connected to MQTT broker")
        # Subscribe to the topic where EV3 receives messages from GUI
        client.subscribe(topic)
    else:
        print("Failed to connect to MQTT broker")

# This function will be called when a message is received
def message_callback(topic, msg):
    global stop_program, settings_dict, start, start_time, end_time, button_ctrl, rolling, belt, activate

    if msg == b'911':
        ev3.speaker.beep()  # Optional: Makes a beep sound when the emergency stop is triggered
        gripper.stop()
        elbow.stop()
        base.stop()
        print("Emergency stop triggered!")
        stop_program = True
        sys.exit()

    elif msg == b'9999':
        start=True


    # Sort Red ON/OFF
    elif msg == b'1101':
        settings_dict['sorting_red'] = True
    elif msg == b'1102':
        settings_dict['sorting_red'] = False

    # Sort Green ON/OFF
    elif msg == b'1103':
        settings_dict['sorting_green'] = True
    elif msg == b'1104':
        settings_dict['sorting_green'] = False

    # Sort Blue ON/OFF
    elif msg == b'1105':
        settings_dict['sorting_blue'] = True
    elif msg == b'1106':
        settings_dict['sorting_blue'] = False

    # Choose pickup point
    elif msg == b'1201':
        settings_dict['pickuppoint_auto'] = 1
    elif msg == b'1202':
        settings_dict['pickuppoint_auto'] = 2
    elif msg == b'1203':
        settings_dict['pickuppoint_auto'] = 3
    elif msg == b'1204':
        settings_dict['pickuppoint_auto'] = 4

    # Elevate zone
    elif msg == b'1301':
        settings_dict['z1_altitude'] = 65
    elif msg == b'1302':
        settings_dict['z1_altitude'] = 0
    elif msg == b'1303':
        settings_dict['z2_altitude'] = 65
    elif msg == b'1304':
        settings_dict['z2_altitude'] = 0
    elif msg == b'1305':
        settings_dict['z3_altitude'] = 65
    elif msg == b'1306':
        settings_dict['z3_altitude'] = 0
    elif msg == b'1307':
        settings_dict['z4_altitude'] = 65
    elif msg == b'1308':
        settings_dict['z4_altitude'] = 0

    # Preset
    elif msg == b'1401':
        settings_dict['preset'] = 'Auto'
    elif msg == b'1402':
        settings_dict['preset'] = 'Manual'

    # Manual pickup
    elif msg == b'1411':
        settings_dict['pickuppoint_manual'] = 1
    elif msg == b'1412':
        settings_dict['pickuppoint_manual'] = 2
    elif msg == b'1413':
        settings_dict['pickuppoint_manual'] = 3
    elif msg == b'1414':
        settings_dict['pickuppoint_manual'] = 4

    # Manual red
    elif msg == b'1421':
        settings_dict['red_manual'] = 1
    elif msg == b'1422':
        settings_dict['red_manual'] = 2
    elif msg == b'1423':
        settings_dict['red_manual'] = 3
    elif msg == b'1424':
        settings_dict['red_manual'] = 4
    elif msg == b'1425':
        settings_dict['red_manual'] = 0

    # Manual green
    elif msg == b'1431':
        settings_dict['green_manual'] = 1
    elif msg == b'1432':
        settings_dict['green_manual'] = 2
    elif msg == b'1433':
        settings_dict['green_manual'] = 3
    elif msg == b'1434':
        settings_dict['green_manual'] = 4
    elif msg == b'1435':
        settings_dict['green_manual'] = 0

    # Manual blue
    elif msg == b'1441':
        settings_dict['blue_manual'] = 1
    elif msg == b'1442':
        settings_dict['blue_manual'] = 2
    elif msg == b'1443':
        settings_dict['blue_manual'] = 3
    elif msg == b'1444':
        settings_dict['blue_manual'] = 4
    elif msg == b'1445':
        settings_dict['blue_manual'] = 0

    elif msg == b'1451':
        activate= True
        button_ctrl= True
        button_control()

    elif msg== b'1452':
        button_ctrl= False
        activate = False

    elif msg == b'1601':
        start_on_pickup_zone(settings_dict)
        detect_zone(1)
    elif msg == b'1602':
        start_on_pickup_zone(settings_dict)
        detect_zone(2)
    elif msg == b'1603':
        start_on_pickup_zone(settings_dict)
        detect_zone(3)
    elif msg == b'1604':
        start_on_pickup_zone(settings_dict)
        detect_zone(4)

    #ROLLING BELT
    elif msg == b'1801':
        belt = Motor(Port.D, Direction.COUNTERCLOCKWISE, [12,36])
        rolling = True
        rolling_belt()
    
    elif msg == b'1802':
        rolling = False

    elif msg.decode('utf-8').startswith('88'):
        # Remove the '88' prefix
        start_time = msg.decode('utf-8')[2:]
        print("Received start time:", start_time)

    elif msg.decode('utf-8').startswith('77'):
        # Remove the '77' prefix
        end_time = msg.decode('utf-8')[2:]
        print("Received end time:", end_time)

    #PAUSE
    elif msg == b'9000' and not button_ctrl:
        pause()

    elif msg == b'9001' and not button_ctrl:
        resume()

# Connect to MQTT broker
client = MQTTClient(username, broker_address, broker_port, username, password)
client.set_callback(message_callback)
client.connect()

# Subscribe to the topic
client.subscribe(topic)
threading.Thread(target=client.check_msg()).start


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
    gripper.run_target(100, -33, then=Stop.HOLD, wait=True)

# Function to move elbow down
def elbowdown():
    elbow.run_until_stalled(-100, then=Stop.HOLD, duty_limit=25)

def elbowdowntarget(settings_dict):
    pickup_zone = settings_dict.get('pickuppoint_auto') if settings_dict.get('preset').lower() == 'auto' else settings_dict.get('pickuppoint_manual', 1)
    elbow_target = custom_elbow_target if custom_base_target is not None else 0 + settings_dict.get('z' + str(pickup_zone) + '_altitude', 0 * FACTORS['elbow'])
    elbow.run_target(100, elbow_target)

# Function to move elbow up
def elbowup():
    elbow_target= settings_dict.get('sensor_altitude')
    elbow.run_target(100, elbow_target)

# Function to perform pickup operation
def pickup():
    elbowdowntarget(settings_dict)
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

            settings_dict['sensor_altitude'] = 65
            
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
        elbowdowntarget(settings_dict)
        opengripper()

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
        elbowdowntarget(settings_dict)
        opengripper()

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
        elbowdowntarget(settings_dict)
        opengripper()

# Function for sorting items based on color
def sort_item(itemcolor, settings_dict):
    if itemcolor == "Red":
        sort_to_red(settings_dict)
    elif itemcolor == "Green":
        sort_to_green(settings_dict)
    elif itemcolor == "Blue":
        sort_to_blue(settings_dict)
    else:
        elbowdowntarget(settings_dict)
        opengripper()

def button_control():
    global button_ctrl, custom_base_target, custom_elbow_target, activate
    if activate:
        while button_ctrl:
            client.check_msg()
            
            # Check for button presses
            if Button.UP in ev3.buttons.pressed():
                elbow.run(30)
            elif Button.DOWN in ev3.buttons.pressed():
                elbow.run(-30)
            elif Button.LEFT in ev3.buttons.pressed():
                base.run(50)
            elif Button.RIGHT in ev3.buttons.pressed():
                base.run(-50)
            else:
                # If no button is pressed, stop the motors
                base.hold()
                elbow.hold()
                
            # Check if the center button is pressed to save the current position
            if Button.CENTER in ev3.buttons.pressed():
                base.hold()
                elbow.hold()
                settings_dict['preset'] = 'manual'
                custom_base_target = base.angle()
                custom_elbow_target = elbow.angle()
                
                button_ctrl = False
                
        print(custom_base_target, custom_elbow_target)
    activate = False
    main_loop()

def rolling_belt():
    global rolling, itemcolor, settings_dict
    print('BELT STARTED')
    client.check_msg()
    settings_dict['preset']= 'auto'
    settings_dict['pickuppoint_auto'] = 1
    settings_dict['z1_altitude'] = 90
    belt.stop()
    start_on_pickup_zone(settings_dict)
    while rolling:
        client.check_msg()
        belt.run(35)
        red, green, blue = read_rgb()
        if red > 3 or green > 3 or blue > 3:
            time.sleep(0.5)
            belt.stop()
            itemcolor = rgb_to_color(red, green, blue)
            opengripper()
            elbow.run_target(150, 65)
            closegripper()
            elbow.run_target(150, 90)
            sort_item(itemcolor, settings_dict)
            dropoff()
            elbow.run_target(150, 90)
            start_on_pickup_zone(settings_dict)

    if rolling == False:
        main_loop()

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
    base.run_target(100, 15, then=Stop.HOLD, wait=True)
    
def calibrate_sensor():
    global button_ctrl, activate, sensor_ctrl
    activate = False
    button_ctrl = True
    sensor_ctrl = True
    if not activate:
        while button_ctrl:
            client.check_msg()
            
            # Check for button presses
            if Button.UP in ev3.buttons.pressed():
                elbow.run(30)
            elif Button.DOWN in ev3.buttons.pressed():
                elbow.run(-30)
            elif Button.LEFT in ev3.buttons.pressed():
                base.run(50)
            elif Button.RIGHT in ev3.buttons.pressed():
                base.run(-50)
            else:
                # If no button is pressed, stop the motors
                base.hold()
                elbow.hold()
                
            # Check if the center button is pressed to save the current position
            if Button.CENTER in ev3.buttons.pressed():
                base.hold()
                elbow.hold()
                value= elbow.angle()
                button_ctrl = False
        sensor_ctrl = False
        return value
    
def start_on_pickup_zone(settings_dict):
    # Move the arm to the pickup zone
    elbowup()  # Lift the elbow
    pickup_zone = settings_dict.get('pickuppoint_auto') if settings_dict.get('preset').lower() == 'auto' else settings_dict.get('pickuppoint_manual', 1)
    base_target = custom_base_target if custom_base_target is not None else {1: 15, 2: 100, 3: 145, 4: 190}.get(pickup_zone, 0) * FACTORS['base']
    elbow_target = custom_elbow_target if custom_base_target is not None else 0 + settings_dict.get('z' + str(pickup_zone) + '_altitude', 0 * FACTORS['elbow'])
    base.run_target(200, base_target)
    elbow.run_target(200, elbow_target)
    pass

def detect_zone(zone):
    global settings_dict

    # Define zone altitudes
    zone_altitudes = {1: 0, 2: 0, 3: 0, 4: 0}  # Define the altitudes for each zone as needed
    
    # Define base targets for each zone
    base_targets = {1: 10, 2: 100, 3: 145, 4: 190}

    # Check if zone is valid
    if zone in zone_altitudes:
        # Open gripper and lift elbow
        opengripper()
        elbowup()

        # Move base to the zone
        base_target = base_targets[zone] * FACTORS['base']
        base.run_target(200, base_target)

        # Lower elbow to the correct altitude for the zone
        elbow_target = 30 + zone_altitudes[zone] * FACTORS['elbow']
        elbow.run_target(200, elbow_target)

        # Perform pickup and detect color
        elbow.run_target(200, zone_altitudes[zone] * FACTORS['elbow'])
        elbow_target(200, settings_dict['sensor_altitude'])
        red, green, blue = read_rgb()
        itemcolor = rgb_to_color(red, green, blue)

        # Print detected color
        print("Detected color in zone", zone, "is:", itemcolor)
        elbow.run_target(200, zone_altitudes[zone] * FACTORS['elbow'])
        opengripper()
        elbow.run_angle(200, 30)
        start_on_pickup_zone(settings_dict)
    else:
        print("Invalid zone number")

def convert_time_to_seconds(time_str):
    # Parse the time string into hours and minutes
    hours = int(time_str[:2])
    minutes = int(time_str[2:])
    
    # Calculate the total seconds
    total_seconds = hours * 3600 + minutes * 60
    
    return total_seconds

def seconds_since_midnight():
    # Get the current epoch time (seconds since 1/1/1970)
    current_epoch_time = int(time.time() + 2*3600)
    
    # Calculate the seconds elapsed since midnight today
    seconds_since_midnight = current_epoch_time % 86400  # 86400 seconds in a day
    
    return seconds_since_midnight

def before_start():
    global start, start_time, end_time
    start = False
    
    while not start:
        client.check_msg()  # Check for messages from the client
        
        current_time = seconds_since_midnight()
        client.check_msg()
        
        # Adjust start and end times if they are not None
        start_time_adjusted = convert_time_to_seconds(start_time) if start_time is not None else None
        client.check_msg()
        end_time_adjusted = convert_time_to_seconds(end_time) if end_time is not None else None
        client.check_msg()
        
        print("Current time:", current_time, "Start time adjusted:", start_time_adjusted, "End time adjusted:", end_time_adjusted)
        client.check_msg()
        
        # Check if the current time falls within the specified time range
        if start_time_adjusted is not None and end_time_adjusted is not None:
            client.check_msg()
            if start_time_adjusted <= current_time <= end_time_adjusted:
                client.check_msg()
                start = True
        
        # Only check for messages from the client once per iteration
        time.sleep(1)  # Wait for 1 second before the next iteration
        
    return start

# Initialize settings dictionary
settings_dict = read_settings()
angle_calibration()
gripper_initial()
elbow.run_until_stalled(-100, then=Stop.HOLD, duty_limit=25)
elbow.reset_angle(0)
for key, value in settings_dict.items():
    print(key, value)

# Call start_on_pickup_zone after initializing mqtt_client
start_on_pickup_zone(settings_dict)
settings_dict['sensor_altitude'] = calibrate_sensor()

before_start()
start = True

def main_loop():
    # Main loop
    while True:
        if stop_program:
            sys.exit()
        elif rolling:
            break
        else:
            while continue_main_loop:
                current_time = time.time() + 2*3600
                current_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time))
                print("Current time: " + current_time_str)

                pickup()
                client.check_msg()
                if stop_program or not continue_main_loop: break

                # Read RGB values and determine item color
                itemcolor = ""
                red, green, blue = read_rgb()
                itemcolor = rgb_to_color(red, green, blue)
                client.publish(topic, itemcolor)
                showinfo(itemcolor)
                client.check_msg()
                if stop_program or not continue_main_loop: break

                # Sort the item based on its color
                sort_item(itemcolor, settings_dict)
                client.check_msg()
                if stop_program or not continue_main_loop: break

                # Drop off the sorted item
                if itemcolor.lower() is not 'other':
                    dropoff()
                client.check_msg()
                if stop_program or not continue_main_loop: break

                start_on_pickup_zone(settings_dict)
                client.check_msg()
                if stop_program or not continue_main_loop: break

                # Clear the EV3 screen and wait before continuing
                ev3.screen.clear()
                time.sleep(0.1)
                client.check_msg()
                if stop_program or not continue_main_loop: break
    if rolling== True and stop_program== False:
        rolling_belt()

if start == True:
    main_loop()