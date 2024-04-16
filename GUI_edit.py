import tkinter as tk
import json

menu_stack = []
changes_to_save = {}

# Load configurations into dictionaries
def load_config():
    with open('robot_config.json') as f:
        config = json.load(f)
    return config

# Write modified configurations back to the file
def write_config():
    global changes_to_save
    config = load_config()
    for section, key_value in changes_to_save.items():
        for key, value in key_value.items():
            config[section][key] = value
    with open('robot_config.json', 'w') as f:
        json.dump(config, f, indent=4)
    changes_to_save = {}  # Clear changes after saving

# Map GUI element names to config element names and handle special cases
def handle_special_cases(value):
    if value == "ON":
        return True
    elif value == "OFF":
        return False
    else:
        try:
            # Attempt to convert to integer if it's a numbered option
            return int(value)
        except ValueError:
            # If it's not "ON", "OFF", or a number, return as is
            return value

# Function to handle changes in the GUI elements
def handle_change(section, key, value):
    global changes_to_save
    # Map GUI element names to config element names
    gui_to_config_mapping = {
        "Sort red": "sort_red",
        "Sort Green": "sort_green",
        "Sort blue": "sort_blue",
        "Choose pickup point": "pickuppoint_auto",
        "Zone 1": "z1",
        "Zone 2": "z2",
        "Zone 3": "z3",
        "Zone 4": "z4",
        "Chose pickup": "pickuppoint_manual",
        "Chose red": "red_manual",
        "Chose green": "green_manual",
        "Chose blue": "blue_manual",
        "Sync: ON": "sync_on",
        "Sync: OFF": "sync_off"
    }

    # Map the section name if needed
    section = section_names.get(section, section)
    
    # Map the key name if needed
    key = gui_to_config_mapping.get(key, key)
    
    # Check if the section already exists in the changes_to_save dictionary
    if section in changes_to_save:
        # If the key already exists in the section, update its value
        if key in changes_to_save[section]:
            changes_to_save[section][key] = handle_special_cases(value)
        else:
            # If the key doesn't exist, add it to the section
            changes_to_save[section][key] = handle_special_cases(value)
    else:
        # If the section doesn't exist, create it and add the key-value pair
        changes_to_save[section] = {key: handle_special_cases(value)}

# Function to update the initial state of radio buttons based on the loaded configuration
def update_initial_state(section, option, var):
    config = load_config()
    section_name = section_names.get(section, section)
    if section_name in config and option in config[section_name]:
        var.set("ON" if config[section_name][option] else "OFF")
    else:
        var.set("OFF")  # Default to OFF if the option doesn't exist in the loaded configuration

def show_menu(menu_content):
    if menu_stack:
        menu_stack[-1].pack_forget()
    menu_stack.append(menu_content)
    menu_content.pack()

def back():
    menu_stack.pop().pack_forget()
    if menu_stack:
        menu_stack[-1].pack()

section_names = {
    "Colours": "colours",
    "Auto assign zones": "auto_assign_zones",
    "Elevate zones": "elevate",
    "Manually assign zones": "manual_assign",
    # Add other submenus here
}

def create_submenu(title, options):
    def show_submenu():
        submenu = tk.Frame(root)
        for option, suboptions in options:
            option_frame = tk.Frame(submenu)
            tk.Label(option_frame, text=option).pack(side="left")
            if option in ["Sort red", "Sort Green", "Sort blue", "Choose pickup point", "Zone 1", "Zone 2", "Zone 3", "Zone 4", "Preset:", "Chose pickup", "Chose red", "Chose green", "Chose blue", "Sync: ON", "Sync: OFF"]:
                var = tk.StringVar()
                update_initial_state(title, option, var)  # Update initial state
                for suboption in suboptions:
                    rb = tk.Radiobutton(option_frame, text=suboption, variable=var, value=suboption,
                                        command=lambda section=section_names[title], key=option, value=suboption: handle_change(section, key, value))
                    rb.pack(side="left")
            else:
                for suboption in suboptions:
                    btn = tk.Button(option_frame, text=suboption)
                    btn.pack(side="left")
            option_frame.pack(side="top")
        tk.Button(submenu, text="Back", command=back).pack(side="top")
        show_menu(submenu)
    return show_submenu

root = tk.Tk()
main_menu = tk.Frame(root)

def main():
    tk.Label(main_menu, text="Main Menu").pack()
    colours_options = [("Sort red", ["ON", "OFF"]), ("Sort Green", ["ON", "OFF"]), ("Sort blue", ["ON", "OFF"])]
    tk.Button(main_menu, text="Colours", command=create_submenu("Colours", colours_options)).pack(side="top")

    auto_assign_zones_options = [("Choose pickup point", ["1", "2", "3", "4"])]
    elevate_zones_options = [("Zone 1", ["ON", "OFF"]), ("Zone 2", ["ON", "OFF"]), ("Zone 3", ["ON", "OFF"]), ("Zone 4", ["ON", "OFF"])]
    manually_assign_zones_options = [("Preset:", ["Auto", "Manual"]), ("Chose pickup", ["1", "2", "3", "4"]), ("Chose red", ["1", "2", "3", "4", "None"]), ("Chose green", ["1", "2", "3", "4", "None"]), ("Chose blue", ["1", "2", "3", "4", "None"]), ("Button control", ["Activate","save"])]

    zones_options = [("Auto assign zones", auto_assign_zones_options), ("Elevate zones", elevate_zones_options), ("Manually assign zones", manually_assign_zones_options)]
    for option, suboptions in zones_options:
        tk.Button(main_menu, text=option, command=create_submenu(option, suboptions)).pack(side="top")

    log_options = [("Log", ["View sorting log"])]
    tk.Button(main_menu, text="Log", command=create_submenu("Log", log_options)).pack(side="top")

    detect_options = [("Detect", ["Select zone: 1", "Select zone: 2", "Select zone: 3", "Select zone: 4"])]
    tk.Button(main_menu, text="Detect", command=create_submenu("Detect", detect_options)).pack(side="top")

    sync_options = [("Sync", ["Instructions", "Sync: ON", "Sync: OFF", "IP-address"])]
    tk.Button(main_menu, text="Sync", command=create_submenu("Sync", sync_options)).pack(side="top")

    view_live_output_options = [("View Live Output", ["Open Live Output"])]
    tk.Button(main_menu, text="View Live Output", command=create_submenu("View Live Output", view_live_output_options)).pack(side="top")

    tk.Button(main_menu, text="SAVE", command=write_config).pack(side="top")

    show_menu(main_menu)
    root.mainloop()

if __name__ == "__main__":
    main()
