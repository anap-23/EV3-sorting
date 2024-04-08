import tkinter as tk

menu_stack = []

def show_menu(menu_content):
    # If there's a menu already being shown, pack it away
    if menu_stack:
        menu_stack[-1].pack_forget()
    # Put the new menu on the stack and show it
    menu_stack.append(menu_content)
    menu_content.pack()

def back():
    # Pack away the current menu
    menu_stack.pop().pack_forget()
    # Show the previous menu
    if menu_stack:
        menu_stack[-1].pack()

def create_submenu(title, options):
    def show_submenu():
        submenu = tk.Frame(root)
        for option, suboptions in options:
            option_frame = tk.Frame(submenu)
            tk.Label(option_frame, text=option).pack(side="left")
            if option in ["Button control", "Log", "Detect", "Sync", "View Live Output"]:
                if option == "Sync":
                    var = tk.StringVar()
                    for suboption in suboptions:
                        if suboption in ["Sync: ON", "Sync: OFF"]:
                            tk.Radiobutton(option_frame, text=suboption, variable=var, value=suboption).pack(side="left")
                        else:
                            tk.Button(option_frame, text=suboption).pack(side="left")
                else:
                    for suboption in suboptions:
                        tk.Button(option_frame, text=suboption).pack(side="left")
            else:
                var = tk.StringVar()
                for suboption in suboptions:
                    tk.Radiobutton(option_frame, text=suboption, variable=var, value=suboption).pack(side="left")
            option_frame.pack(side="top")
        tk.Button(submenu, text="Back", command=back).pack(side="top")
        show_menu(submenu)
    return show_submenu


root = tk.Tk()

main_menu = tk.Frame(root)

def main():

    # Add some content to the main menu
    tk.Label(main_menu, text="Main Menu").pack()
    colours_options = [("Sort red", ["ON", "OFF"]), ("Sort Green", ["ON", "OFF"]), ("Sort blue", ["ON", "OFF"])]
    tk.Button(main_menu, text="Colours", command=create_submenu("Colours", colours_options)).pack(side="top")

    auto_assign_zones_options = [("Choose pickup point", ["1", "2", "3", "4"])]
    elevate_zones_options = [("Zone 1", ["ON", "OFF"]), ("Zone 2", ["ON", "OFF"]), ("Zone 3", ["ON", "OFF"]), ("Zone 4", ["ON", "OFF"])]
    manually_assign_zones_options = [("Chose pickup", ["1", "2", "3", "4"]), ("Chose red", ["1", "2", "3", "4", "None"]), ("Chose green", ["1", "2", "3", "4", "None"]), ("Chose blue", ["1", "2", "3", "4", "None"]), ("Button control", ["Activate","save"])]

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


    # Start on the main menu
    show_menu(main_menu)

    root.mainloop()

if __name__ == "__main__":
    main()
