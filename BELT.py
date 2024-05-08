#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.tools import wait
from umqtt.simple import MQTTClient
import _thread
import sys

# MQTT settings
broker_address = "io.adafruit.com"
broker_port = 1883
username = 'mohalh963'
password = "aio_eXHS71Xd3zWxJI4eKj2BXDizRTMe"  
topic = b"mohalh963/feeds/bth.ev3-ass"

# EV3 settings
ev3 = EV3Brick()
belt = Motor(Port.D)

# This function will be called when a message is received
def message_callback(topic, msg):
    if msg == b'911':
        ev3.speaker.beep()
        wait(3000)
        belt.stop()
        sys.exit()

# Connect to MQTT broker
client = MQTTClient(username, broker_address, broker_port, username, password)
client.set_callback(message_callback)
client.connect()

# Subscribe to the topic
client.subscribe(topic)

# Main loop
while True:
    client.check_msg()
    belt.run_time(50, 3000)
    wait(100)


def anti_collision():
    while risk:
        time.wait(1)



        
    elif msg.decode("utf-8").startswith("88"):
        # Decode the message and extract hours and minutes
        time_str = msg.decode("utf-8")[2:]  # Remove the "88" prefix
        hours = int(time_str[:2])
        minutes = int(time_str[2:])
        # Convert to a struct_time
        time_struct = time.strptime(f"{hours}:{minutes}", "%H:%M")
        # Convert struct_time to seconds since the epoch
        start_time = time.mktime(time_struct)
        print("Received start time:", hours, "hours", minutes, "minutes. Converted:", start_time)

    elif msg.decode("utf-8").startswith("77"):
        # Decode the message and extract hours and minutes
        time_str = msg.decode("utf-8")[2:]  # Remove the "77" prefix
        hours = int(time_str[:2])
        minutes = int(time_str[2:])
        # Convert to a struct_time
        time_struct = time.strptime(f"{hours}:{minutes}", "%H:%M")
        # Convert struct_time to seconds since the epoch
        end_time = time.mktime(time_struct)
        print("Received end time:", hours, "hours", minutes, "minutes. Converted:", end_time)