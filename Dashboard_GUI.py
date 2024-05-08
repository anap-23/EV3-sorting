import tkinter as tk
import paho.mqtt.client as mqtt
import time
import webbrowser

menu_stack = []

broker_address = "io.adafruit.com"
broker_port = 1883
username = 'mohalh963'
password = "aio_eXHS71Xd3zWxJI4eKj2BXDizRTMe"
topic = "mohalh963/feeds/bth.ev3-ass"  # Change to string format

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print("Failed to connect to MQTT broker")

# Initialize MQTT client
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
# Set MQTT broker username and password
mqtt_client.username_pw_set(username, password)

# Callback function for when a message is received
def on_message(client, userdata, message):
    print("Received message:", str(message.payload.decode("utf-8")))

mqtt_client.on_message = on_message

# MQTT action mapping dictionary
action_mapping = {
    "EMERGENCY": "911",
    "START": "9999",
    "Sort Red ON": "1101",
    "Sort Red OFF": "1102",
    "Sort Green ON": "1103",
    "Sort Green OFF": "1104",
    "Sort Blue ON": "1105",
    "Sort Blue OFF": "1106",
    "Choose pickup point 1": "1201",
    "Choose pickup point 2": "1202",
    "Choose pickup point 3": "1203",
    "Choose pickup point 4": "1204",
    "Elevate zone 1 ON": "1301",
    "Elevate zone 1 OFF": "1302",
    "Elevate zone 2 ON": "1303",
    "Elevate zone 2 OFF": "1304",
    "Elevate zone 3 ON": "1305",
    "Elevate zone 3 OFF": "1306",
    "Elevate zone 4 ON": "1307",
    "Elevate zone 4 OFF": "1308",
    "Preset: Auto": "1401",
    "Preset: Manual": "1402",
    "Manual pickup 1": "1411",
    "Manual pickup 2": "1412",
    "Manual pickup 3": "1413",
    "Manual pickup 4": "1414",
    "Manual red 1": "1421",
    "Manual red 2": "1422",
    "Manual red 3": "1423",
    "Manual red 4": "1424",
    "Manual red None": "1425",
    "Manual green 1": "1431",
    "Manual green 2": "1432",
    "Manual green 3": "1433",
    "Manual green 4": "1434",
    "Manual green None": "1435",
    "Manual blue 1": "1441",
    "Manual blue 2": "1442",
    "Manual blue 3": "1443",
    "Manual blue 4": "1444",
    "Manual blue None": "1445",
    "Activate": "1451",
    "Save": "1452",
    "Detect zone 1": "1601",
    "Detect zone 2": "1602",
    "Detect zone 3": "1603",
    "Detect zone 4": "1604",
    "Start time indicator": "88",
    "End time indicator": "77",
    "Rolling belt YES": "1801",
    "Rolling belt NO": "1802",
    "Pause": "9000",
    "Proceed": "9001"
}

# Button to MQTT action mapping dictionary
button_to_mqtt_mapping = {
    "Sort Red": ["Sort Red ON", "Sort Red OFF"],
    "Sort Green": ["Sort Green ON", "Sort Green OFF"],
    "Sort Blue": ["Sort Blue ON", "Sort Blue OFF"],
    "Choose pickup point": ["Choose pickup point 1", "Choose pickup point 2", "Choose pickup point 3", "Choose pickup point 4"],
    "Elevate zone 1": ["Elevate zone 1 ON", "Elevate zone 1 OFF"],
    "Elevate zone 2": ["Elevate zone 2 ON", "Elevate zone 2 OFF"],
    "Elevate zone 3": ["Elevate zone 3 ON", "Elevate zone 3 OFF"],
    "Elevate zone 4": ["Elevate zone 4 ON", "Elevate zone 4 OFF"],
    "Preset": ["Preset: Auto", "Preset: Manual"],
    "Choose pickup": ["Manual pickup 1", "Manual pickup 2", "Manual pickup 3", "Manual pickup 4"],
    "Choose red": ["Manual red 1", "Manual red 2", "Manual red 3", "Manual red 4", "Manual red None"],
    "Choose green": ["Manual green 1", "Manual green 2", "Manual green 3", "Manual green 4", "Manual green None"],
    "Choose blue": ["Manual blue 1", "Manual blue 2", "Manual blue 3", "Manual blue 4", "Manual blue None"],
    "Button control": ["Activate", "Save"],
    "Detect colours": ["Detect zone 1", "Detect zone 2", "Detect zone 3", "Detect zone 4"],
    "Update Schedule": ["Update Schedule"],
    "Rolling belt": ["Rolling belt YES", "Rolling belt NO"],
    "Pause": ["Pause"],
    "Proceed": ["Proceed"],
    "EMERGENCY": ["EMERGENCY"],
    "Start": ["START"]
}
def handle_gui_action(action_name):
    print(action_name)
    if action_name == "VIEW_LIVE_OUTPUT":
        webbrowser.open("https://io.adafruit.com/mohalh963/feeds/bth.ev3-ass")
    elif action_name in action_mapping:
        # Publish the value associated with the action name
        mqtt_client.publish(topic, action_mapping[action_name])
    elif action_name == "Update Schedule":
        start_time = start_time_entry.get()
        end_time = end_time_entry.get()

        # Validate time format
        if len(start_time) != 4 or len(end_time) != 4 or not start_time.isdigit() or not end_time.isdigit():
            print("Invalid time format. Please enter 4 digits for both start and end times.")
            return

        # Publish start and end times to the topic
        mqtt_client.publish(topic, f"{action_mapping['Start time indicator']}{start_time}")
        mqtt_client.publish(topic, f"{action_mapping['End time indicator']}{end_time}")

        print("Schedule updated successfully.")
    else:
        print("Action not found in mapping.")

def show_menu(menu_content):
    if menu_stack:
        menu_stack[-1].pack_forget()
    menu_stack.append(menu_content)
    menu_content.pack()

def back():
    menu_stack.pop().pack_forget()
    if menu_stack:
        menu_stack[-1].pack()

# List of options that should have radio buttons
radio_options = [
    "Sort Red", 
    "Sort Green", 
    "Sort Blue", 
    "Choose pickup point", 
    "Elevate zone 1", 
    "Elevate zone 2", 
    "Elevate zone 3", 
    "Elevate zone 4", 
    "Preset", 
    "Choose pickup", 
    "Choose red", 
    "Choose green", 
    "Choose blue",  
    "Rolling belt", 
]

schedule_list = [
    ("Start time", "start_time_entry"),
    ("End time", "end_time_entry")
]

# Function to handle button click events
def handle_button_click(action_name):
    handle_gui_action(action_name)

def only_four_digits(input):
    if input.isdigit() and len(input) <= 4:
        return True
    elif input == "":
        return True
    else:
        return False
    
def create_submenu(root, title, options):
    submenu = tk.Frame(root)
    
    # Define a dictionary to store the radio button variables for each option
    radio_vars = {}
    
    # Iterate over the options to create the submenu
    for option, suboptions in options:
        option_frame = tk.Frame(submenu)
        tk.Label(option_frame, text=option).pack(side="left")
        
        # Check if the option should have radio buttons
        if option in radio_options:
            # Initialize radio variable for this option
            radio_vars[option] = tk.IntVar(value=None)
            
            # Iterate over suboptions to create radio buttons
            for suboption in suboptions:
                button_text = suboption[0]  # Assuming the button text is the first element of each suboption tuple
                action_name = button_to_mqtt_mapping[option][suboptions.index(suboption)]
                
                # Create the radio button
                rb = tk.Radiobutton(option_frame, text=button_text, variable=radio_vars[option], value=action_name,
                                    command=lambda action_name=action_name, option=option: handle_gui_action(action_name))
                rb.pack(side="left")
        elif option == "Schedule Pickups":
            # Iterate over suboptions to create labels and entries
            for option, entry_name in schedule_list:
                entry_frame = tk.Frame(submenu)
                entry_frame.pack(side="top", padx=5, pady=2)

                label_text = option + ":"
                tk.Label(entry_frame, text=label_text).pack(side="left")

                entry = tk.Entry(entry_frame, validate="key", validatecommand=(root.register(only_four_digits), "%P"))
                entry.pack(side="left")

                if entry_name == "start_time_entry":
                    global start_time_entry
                    start_time_entry = entry
                elif entry_name == "end_time_entry":
                    global end_time_entry
                    end_time_entry = entry

            # Create the Update button
            update_button = tk.Button(submenu, text="Update", command=lambda: handle_gui_action("Update Schedule"))
            update_button.pack(side="top", pady=5)
        else:
            # Iterate over suboptions to create regular buttons
            for suboption in suboptions:
                button_text = suboption[0]  # Assuming the button text is the first element of each suboption tuple
                action_name = button_to_mqtt_mapping[option][suboptions.index(suboption)]
                
                # Create the regular button
                btn = tk.Button(option_frame, text=button_text,  # Adding some padding
                                command=lambda action_name=action_name: handle_gui_action(action_name))
                btn.pack(side="left")
        
        # Pack the option frame
        option_frame.pack(side="top")
    
    # Add a back button to return to the previous menu
    tk.Button(submenu, text="Back", command=back).pack(side="top")
    
    # Show the submenu
    show_menu(submenu)

def main():
    root = tk.Tk()
    main_menu = tk.Frame(root)

    tk.Label(main_menu, text="Main Menu").pack()

    # Submenu 1: Colours
    colours_options = [
        ("Sort Red", ["ON", "OFF"]),
        ("Sort Green", ["ON", "OFF"]),
        ("Sort Blue", ["ON", "OFF"])
    ]
    tk.Button(main_menu, text="Colours", command=lambda: create_submenu(root, "Colours", colours_options)).pack(side="top")

    # Submenu 2: Auto Assign Zones
    auto_assign_zones_options = [("Choose pickup point", ["1", "2", "3", "4"])]
    tk.Button(main_menu, text="Auto Assign Zones", command=lambda: create_submenu(root, "Auto Assign Zones", auto_assign_zones_options)).pack(side="top")

    # Submenu 3: Elevate Zones
    elevate_zones_options = [
        ("Elevate zone 1", ["ON", "OFF"]),
        ("Elevate zone 2", ["ON", "OFF"]),
        ("Elevate zone 3", ["ON", "OFF"]),
        ("Elevate zone 4", ["ON", "OFF"])
    ]
    tk.Button(main_menu, text="Elevate Zones", command=lambda: create_submenu(root, "Elevate Zones", elevate_zones_options)).pack(side="top")

    # Submenu 4: Manually Assign Zones
    manually_assign_zones_options = [
        ("Preset", ["Auto", "Manual"]),
        ("Choose pickup", ["1", "2", "3", "4"]),
        ("Choose red", ["1", "2", "3", "4", "None"]),
        ("Choose green", ["1", "2", "3", "4", "None"]),
        ("Choose blue", ["1", "2", "3", "4", "None"]), 
        ("Button control", ["Activate", "Save"])
    ]
    tk.Button(main_menu, text="Manually Assign Zones", command=lambda: create_submenu(root, "Manually Assign Zones", manually_assign_zones_options)).pack(side="top")

    # Submenu 5: Detect Colours
    detect_options = [
        ("Detect colours", ["Detect zone 1","Detect zone 2","Detect zone 3", "Detect zone 4"])
    ]
    tk.Button(main_menu, text="Detect Colours", command=lambda: create_submenu(root, "Detect Colours", detect_options)).pack(side="top")

    # Submenu 6: Schedule Pickups
    schedule_pickups_options = [("Schedule Pickups", schedule_list)]
    tk.Button(main_menu, text="Schedule Pickups", command=lambda: create_submenu(root, "Schedule Pickups", schedule_pickups_options)).pack(side="top")

    # Submenu 7: Rolling Belt
    rolling_belt_options = [("Rolling belt", ["YES", "NO"])]
    tk.Button(main_menu, text="Rolling Belt", command=lambda: create_submenu(root, "Rolling Belt", rolling_belt_options)).pack(side="top")

    # Buttons
    tk.Button(main_menu, text="Start", command=lambda: handle_gui_action("START"), fg="green").pack(side="left")
    tk.Button(main_menu, text="Pause", command=lambda: handle_gui_action("Pause")).pack(side="left")
    tk.Button(main_menu, text="Proceed", command=lambda: handle_gui_action("Proceed")).pack(side="left")
    tk.Button(main_menu, text="EMERGENCY", command=lambda: handle_gui_action("EMERGENCY"), fg="red").pack(side="top", pady=10)

    show_menu(main_menu)
    root.mainloop()

if __name__ == "__main__":
    # Connect to the MQTT broker
    mqtt_client.connect(broker_address, broker_port)
    mqtt_client.loop_start()
    mqtt_client.on_connect = on_connect

    main()
