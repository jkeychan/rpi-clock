from custom_chars import custom_chars
import os
import time
import board
import busio
import adafruit_ht16k33.segments as segments
import requests
import json
import configparser

# Check if custom_chars.py exists, and if not, create a new one with default values
CUSTOM_CHARS_FILE = 'custom_chars.py'
DEFAULT_CUSTOM_CHARS = {
    'custom_chars': {
        'char1': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
        'char2': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    }
}

if not os.path.exists(CUSTOM_CHARS_FILE):
    print("No custom_chars.py file detected, creating custom_chars.py...")
    with open(CUSTOM_CHARS_FILE, 'w') as custom_chars_file:
        custom_chars_file.write("custom_chars = {\n")
        for char_name, char_values in DEFAULT_CUSTOM_CHARS['custom_chars'].items():
            custom_chars_file.write(f"    '{char_name}': {char_values},\n")
        custom_chars_file.write("}\n")

# Import the custom_chars.py module after ensuring it exists

# Helper function to display custom characters


def display_custom_chars(chars):
    display.print(chars)

# Helper function to display the temperature on the display


def display_temperature(temp, unit):
    temp_str = "{:.0f} {}".format(temp, unit)
    display.print(temp_str.rjust(7))

# Helper function to display the time on the display


def display_time():
    now = time.localtime()
    hour = now.tm_hour

    # Check the time format from the config file
    time_format = config.get('Display', 'TIME_FORMAT')

    if time_format == '12':
        # Convert to 12-hour format
        hour = hour % 12
        if hour == 0:
            hour = 12

    minute = now.tm_min

    time_str = "{:2d}{:02d}".format(hour, minute)
    display.print(time_str)


# Helper function to display the humidity on the display


def display_humidity(humidity):
    humidity_str = "{:02d}".format(round(humidity))
    display.print("rh{}".format(humidity_str))


CONFIG_FILE = 'config.ini'
DEFAULT_CONFIG = {
    'Weather': {
        'API_KEY': 'your_api_key_here',
        'ZIP_CODE': 'your_zip_code_here'
    },
    'Display': {
        'TIME_FORMAT': '12',
        'TEMP_UNIT': 'C'
    }
}

# Check if config.ini exists, and if not, create a new one with default values
if not os.path.exists(CONFIG_FILE):
    print("No configuration file detected, creating config.ini...")
    config = configparser.ConfigParser()
    config.read_dict(DEFAULT_CONFIG)

    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

# Read configuration from config.ini
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# Check if 'Weather' section exists, and if not, add it with default values
if 'Weather' not in config:
    config['Weather'] = DEFAULT_CONFIG['Weather']

# Check if 'ZIP_CODE' option exists in the 'Weather' section, and if not, add it with a default value
if 'ZIP_CODE' not in config['Weather']:
    config['Weather']['ZIP_CODE'] = DEFAULT_CONFIG['Weather']['ZIP_CODE']

# Write the final configuration to the file
with open(CONFIG_FILE, 'w') as configfile:
    config.write(configfile)

# Get the configuration values
api_key = config.get('Weather', 'API_KEY')
zip_code = config.get('Weather', 'ZIP_CODE')
time_format = config.get('Display', 'TIME_FORMAT')
temp_unit = config.get('Display', 'TEMP_UNIT')

# Initialize I2C bus and the display
i2c = busio.I2C(board.SCL, board.SDA)
display = segments.Seg7x4(i2c)

# OpenWeatherMap API endpoint
api_endpoint = "https://api.openweathermap.org/data/2.5/weather"

# Function to fetch weather data from OpenWeatherMap API


def fetch_weather(api_endpoint, zip_code, api_key, temp_unit):
    try:
        response = requests.get(api_endpoint, params={
            "zip": zip_code, "appid": api_key, "units": "metric"})
        response.raise_for_status()
        weather_data = json.loads(response.text)
        temperature = round(weather_data["main"]["temp"])
        feels_like = round(weather_data["main"]["feels_like"])
        humidity = round(weather_data["main"]["humidity"])

        if temp_unit == 'F':
            temperature = (temperature * 9/5) + 32
            feels_like = (feels_like * 9/5) + 32

        return temperature, feels_like, humidity

    except requests.exceptions.RequestException as e:
        print("Failed to get weather data:", e)
        return None


# Loop to display time and weather alternately
while True:
    # Display the time for 3 seconds (you can adjust the time as needed)
    for _ in range(6):
        display_time()
        display.colon = True  # Enable the colon for time display
        display.show()
        time.sleep(1)  # Keep the colon enabled for 1 second
        display.colon = False  # Disable the colon for time display
        display.show()
        time.sleep(1)  # Keep the colon disabled for 1 second

    # Fetch weather data from the OpenWeatherMap API
    weather_info = fetch_weather(api_endpoint, zip_code, api_key, temp_unit)

    # Display weather information if data is available
    if weather_info:
        temperature, feels_like, humidity = weather_info

        display.fill(0)  # Clear the display

        display.marquee('Out', delay=0.2, loop=False)
        time.sleep(2)

        display_temperature(temperature, temp_unit)
        display.show()
        time.sleep(5)

        display.marquee('feel', delay=0.2, loop=False)
        time.sleep(2)

        display_temperature(feels_like, temp_unit)
        display.show()
        time.sleep(5)

        display.fill(0)
        display_humidity(humidity)
        display.show()
        time.sleep(3)

        display.fill(0)
