# rpi-clock

![Vector logo of a Raspberry made to look like it has a digital display and futuristic](rpi-clock-logo.png)

Displaying local time and weather from [OpenWeatherMap APIs](https://openweathermap.org/current/)

![Animated GIF of a 7-segment display cycling through displaying time, followed by outside temperature, heat index, and relative humidity values](rpi-clock.gif)


## Requirements

- Python 3
- A [Raspberry Pi 4](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) device using an [Adafruit 1.2" 7-Segment LED HT16K33 Backpack](https://learn.adafruit.com/adafruit-led-backpack/1-2-inch-7-segment-backpack/).
- You will also need to install the [Adafruit-circuitpython-ht16k33](https://github.com/adafruit/Adafruit_CircuitPython_HT16K33)
- An [Openweathermap account](https://home.openweathermap.org/users/sign_up/), but you can use the free _weather_ key for the purposes of this script.

## Instructions

Be sure to update the **[config.ini](config.ini)** file with your [Openweathermap API Key](https://openweathermap.org/api_keys/) and other details.

Then simply run `python3 clock.py`. You should see output on your [Adafruit 1.2" 7-Segment LED HT16K33 Backpack](https://learn.adafruit.com/adafruit-led-backpack/1-2-inch-7-segment-backpack/).






