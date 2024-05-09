# EV3 Sorting System

## Overview
The EV3 Sorting System is a Python script designed to control a robotic arm using MQTT messages. The script is specifically tailored for use with the LEGO Mindstorms EV3 platform, but it can be adapted for other hardware configurations with minimal modifications.

## Features
- **MQTT Communication**: The script connects to an MQTT broker to send and receive messages, allowing for remote control and monitoring of the robot arm.
- **Pickup and Drop-off**: The robot arm can pick up items from a designated pickup zone and drop them off at specified locations.
- **Color Sorting**: Items picked up by the robot arm can be sorted based on their color (red, green, or blue).
- **Emergency Stop**: An emergency stop functionality is implemented to halt all robot arm movements in case of emergencies.
- **Calibration**: The script includes functions for calibrating the robot arm's sensors and movements.
- **Average Speed Calculation**: The system calculates the average speed of item processing based on the time taken to process each item.

## Requirements
- LEGO Mindstorms EV3 hardware platform
- Python 3.x
- Required Python packages (Pybricks, umqtt.simple)

## Installation
1. Connect your LEGO Mindstorms EV3 hardware to your computer.
2. Install Python 3.x on your computer if not already installed.
3. Install the required Python packages using pip:
   ```
   pip install pybricks umqtt.simple
   ```
4. Download the script (`ev3_sorting_system.py`) and any other required files.
5. Configure the MQTT broker settings and other parameters in the script as needed.

## Usage
1. Run the Python script (`ev3_sorting_system.py`) on your EV3 brick.
2. Run the Python script (`sorting_system_GUI.py`) on your computer.
3. Ensure that the EV3 brick is connected to the MQTT broker and is able to send and receive messages.
4. Send MQTT messages to the designated topics to control the robot arm, monitor its status, and perform various actions.

## Configuration
- **MQTT Broker Settings**: Configure the MQTT broker address, port, username, and password in the script.
- **Hardware Configuration**: Adjust hardware-related parameters such as motor ports, sensor ports, and movement factors (if needed) in the script.
- **Topic Configuration**: Define MQTT topics for communication with the robot arm and customize message formats as required.

## Contributing
Contributions to the EV3 Robot Arm Control System project are welcome! If you have suggestions for improvements, bug fixes, or new features, please feel free to submit pull requests or open issues on the GitHub repository.

## License
This project is not licensed.

## Acknowledgments
- This project was inspired by the need for a flexible and extensible control system for robotic arms in educational and hobbyist settings.
- Special thanks to the contributors and maintainers of the Pybricks and umqtt.simple libraries, which made it possible to interface with the LEGO Mindstorms EV3 platform and MQTT protocol effectively.
