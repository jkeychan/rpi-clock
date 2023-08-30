import os
import time
import board
import busio
import adafruit_ht16k33.segments as segments
import requests
import configparser
import ntplib

API_REFRESH_CYCLES = 10
cached_weather_info = None
api_endpoint = "https://api.openweathermap.org/data/2.5/weather"
CONFIG_FILE = 'config.ini'

DEFAULT_CONFIG = {
    'Weather': {
        'API_KEY': 'your_api_key_here',
        'ZIP_CODE': 'your_zip_code_here'
    },
    'Display': {
        'TIME_FORMAT': '12',
        'TEMP_UNIT': 'C'
    },
    'NTP': {
        'PREFERRED_SERVER': '127.0.0.1'
    },
    'Cycle': {
        'time_display': '2',
        'temp_display': '3',
        'feels_like_display': '3',
        'humidity_display': '2'
    }
}

config = configparser.ConfigParser()
config.read_dict(DEFAULT_CONFIG)
config.read(CONFIG_FILE)

api_key = config['Weather']['API_KEY']
zip_code = config['Weather']['ZIP_CODE']
time_format = config['Display']['TIME_FORMAT']
temp_unit = config['Display']['TEMP_UNIT']
preferred_ntp_server = config['NTP']['PREFERRED_SERVER']
time_display = config.getint('Cycle', 'time_display')
temp_display = config.getint('Cycle', 'temp_display')
feels_like_display = config.getint('Cycle', 'feels_like_display')
humidity_display = config.getint('Cycle', 'humidity_display')

i2c = busio.I2C(board.SCL, board.SDA)
display = segments.Seg7x4(i2c)


def celsius_to_fahrenheit(celsius):
    """Convert Celsius temperature to Fahrenheit."""
    return (celsius * 9/5) + 32


def display_temperature(temp, unit):
    """Display the temperature on the 7-segment display."""
    temp_str = "{:.0f} {}".format(temp, unit)
    display.print(temp_str.rjust(7))


def display_time():
    """Display the current time on the 7-segment display."""
    now = time.localtime()
    hour = now.tm_hour
    if time_format == '12':
        hour = hour % 12
        if hour == 0:
            hour = 12
    minute = now.tm_min
    time_str = "{:2d}{:02d}".format(hour, minute)
    display.print(time_str)


def display_humidity(humidity):
    """Display the relative humidity on the 7-segment display."""
    humidity_str = "rH{:02d}".format(round(humidity))
    display.print(humidity_str)


def fetch_weather(api_endpoint, zip_code, api_key, temp_unit):
    """Fetch weather information from OpenWeatherMap."""
    try:
        response = requests.get(api_endpoint, params={
            "zip": zip_code, "appid": api_key, "units": "metric"})
        response.raise_for_status()
        weather_data = response.json()

        temperature = round(weather_data["main"]["temp"])
        feels_like = round(weather_data["main"]["feels_like"])
        humidity = round(weather_data["main"]["humidity"])

        if temp_unit == 'F':
            temperature = celsius_to_fahrenheit(temperature)
            feels_like = celsius_to_fahrenheit(feels_like)

        return temperature, feels_like, humidity

    except requests.exceptions.RequestException as e:
        print("Failed to get weather data:", e)
        return None


def get_current_time():
    """Get current time using an NTP server or system time if NTP fails."""
    try:
        ntp_client = ntplib.NTPClient()
        response = ntp_client.request(
            preferred_ntp_server, version=3, timeout=5)
        return time.localtime(response.tx_time)

    except Exception as e:
        print("Failed to get time from NTP server:", e)
        return time.localtime()


def display_metric_with_message(message, display_function, *args, delay=2):
    """Display a message followed by a metric value on the 7-segment display."""
    display.fill(0)
    display.marquee(message, delay=0.2, loop=False)
    time.sleep(delay)
    display_function(*args)
    display.show()


def main_loop():
    """Run the main loop to display time and weather information."""
    cycle_counter = 0
    while True:
        for _ in range(time_display):
            display_time()
            display.colon = True
            display.show()
            time.sleep(1)
            display.colon = False
            display.show()
            time.sleep(1)

        if cycle_counter == 0 or cached_weather_info is None:
            cached_weather_info = fetch_weather(
                api_endpoint, zip_code, api_key, temp_unit)

        weather_info = cached_weather_info

        if weather_info:
            temperature, feels_like, humidity = weather_info
            display_metric_with_message(
                'Out', display_temperature, temperature, temp_unit)
            time.sleep(temp_display)
            display_metric_with_message(
                'feel', display_temperature, feels_like, temp_unit)
            time.sleep(feels_like_display)
            display_humidity(humidity)
            time.sleep(humidity_display)

        cycle_counter = (cycle_counter + 1) % API_REFRESH_CYCLES


if __name__ == "__main__":
    main_loop()
