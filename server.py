import RPi.GPIO as GPIO
import os
import configparser
import time
import requests
from datetime import datetime

# Get the full path to the configuration file
config_file_path = os.path.join('/home/pi/DoorContact', 'config.ini')

# Initialize the configparser
config = configparser.ConfigParser()

# Read the configuration file
config.read(config_file_path)

# Access configuration settings
alarm_gpio = config.getint('Settings', 'alarm_gpio')
button_gpio = config.getint('Settings', 'button_gpio')
button_gpio_power_supply_gpio = config.getint('Settings', 'button_gpio_power_supply_gpio')
door_contact_gpio = config.getint('Settings', 'door_contact_gpio')
door_contact_power_supply_gpio = config.getint('Settings', 'door_contact_power_supply_gpio')

use_SGEMS = config.getboolean('Settings', 'use_SGEMS')

# Setup GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(alarm_gpio, GPIO.OUT)
GPIO.setup(button_gpio, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(button_gpio_power_supply_gpio, GPIO.OUT)
GPIO.output(button_gpio_power_supply_gpio, GPIO.HIGH)
GPIO.setup(door_contact_gpio, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(door_contact_power_supply_gpio, GPIO.OUT)
GPIO.output(door_contact_power_supply_gpio, GPIO.HIGH)

def sendAlertToSGEMS():
    if(use_SGEMS):
        system_id = config.get('Settings', 'system_id')
        company_id = config.get('Settings', 'company_id')
        site_id = config.getint('Settings', 'site_id')
        user_id = config.getint('Settings', 'user_id')
        sensor_id = config.getint('Settings', 'sensor_id')

        if system_id not in ["sgems", "sgemsuat"]:
            baseURL = f"http://{system_id}"
        else:
            baseURL = f"https://{system_id}.logicsmartsoln.com"

        url = f"{baseURL}/{company_id}/api/recording/uploadSensorData"
        payload = {
            "site_id": site_id,
            "sensor_id": sensor_id,
            "user_id": user_id,
            "sensor_value": "1"
        }
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            print("Door Sensor Log has been sent to SGEMS Portal and SGEMS Notifier")
            return True
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return False

try:
    while True:
        if GPIO.input(door_contact_gpio) == GPIO.LOW:
            print("Door is open. Starting countdown...")

            countdown_time = 5  # Countdown time in seconds
            start_time = time.time()

            # Countdown loop
            while time.time() - start_time < countdown_time:
                remaining_time = countdown_time - int(time.time() - start_time)
                print(f"{remaining_time} seconds more to trigger the alarm...", end='\r')
                
                if GPIO.input(door_contact_gpio) == GPIO.HIGH:
                    print("\nDoor closed during countdown.")
                    break
                time.sleep(0.1)  # Check the door state with a small delay

            # If after the countdown the door is still open, trigger the alarm
            if GPIO.input(door_contact_gpio) == GPIO.LOW:
                print("\nAlarm triggered")
                GPIO.output(alarm_gpio, GPIO.HIGH)
                sendAlertToSGEMS()
                
                # Wait for button press or the door to close to stop the alarm
                while GPIO.input(button_gpio) == GPIO.LOW and GPIO.input(door_contact_gpio) == GPIO.LOW:
                    time.sleep(0.1)  # Check button state with a small delay

                # Button pressed, stop the alarm 
                print("Button pressed, stopping alarm")
                GPIO.output(alarm_gpio, GPIO.LOW)

        else:
            print(f"Door is closed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(1)  # Wait for 1 second before checking again

except KeyboardInterrupt:
    GPIO.output(alarm_gpio, GPIO.LOW)
    print("Exiting...")

finally:
    GPIO.cleanup()
    
# try:
#     while True:
#         if GPIO.input(door_contact_gpio) == GPIO.LOW:
#             print("Door is open...")
#             print("Starting countdown...")
#             # Countdown 1 minute
#             time.sleep(5)
            
#             # Trigger Alarm
#             print("Alarm triggered")
#             GPIO.output(alarm_gpio, GPIO.HIGH)
#             sendAlertToSGEMS()
            
#             # Wait for button press or the door to close to stop the alarm
#             while GPIO.input(button_gpio) == GPIO.LOW and GPIO.input(door_contact_gpio) == GPIO.LOW:
#                 time.sleep(0.1)  # Check button state with a small delay

#             # Button pressed, stop the alarm
#             print("Button pressed, stopping alarm")
#             GPIO.output(alarm_gpio, GPIO.LOW)

# except KeyboardInterrupt:
#     GPIO.output(alarm_gpio, GPIO.LOW)
#     print("Exiting...")

# finally:
#     GPIO.cleanup()
