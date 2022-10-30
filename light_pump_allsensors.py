# by akleindolph based on code from...
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT


import time
import board
import ssl
import socketpool
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT

import adafruit_ahtx0
from adafruit_seesaw.seesaw import Seesaw
import adafruit_veml7700

from adafruit_motorkit import MotorKit
import neopixel


i2c = board.I2C()  # uses board.SCL and board.SDA

sensor = adafruit_ahtx0.AHTx0(i2c)  #temperature and humidity sensor
ss = Seesaw(i2c, addr=0x36)   #moisture sensor
veml7700 = adafruit_veml7700.VEML7700(i2c)  #light sensor

kit = MotorKit(i2c=board.I2C()) #motor variables
kit.motor1.throttle = 0  #start with motor off

pixel_pin = board.A2  #neopixel variables
num_pixels = 16
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.7, auto_write=False)
growcolor1 = (180, 0, 255)
growcolor2 = (180, 200, 255)
off = (0, 0, 0)

data_interval = 30

# Add a secrets.py to your filesystem that has a dictionary called secrets with "ssid" and
# "password" keys with your WiFi credentials. DO NOT share that file or commit it into Git or other
# source control.
# pylint: disable=no-name-in-module,wrong-import-order
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Set your Adafruit IO Username and Key in secrets.py
# (visit io.adafruit.com if you need to create an account,
# or if you need your Adafruit IO key.)
aio_username = secrets["aio_username"]
aio_key = secrets["aio_key"]

print("Connecting to %s" % secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!" % secrets["ssid"])
### Feeds ###

# Setup a feed named 'photocell' for publishing to a feed
temperature_feed = secrets["aio_username"] + "/feeds/temperature"
humidity_feed = secrets["aio_username"] + "/feeds/humidity"
soil_feed = secrets["aio_username"] + "/feeds/soil"
light_feed = secrets["aio_username"] + "/feeds/light"
grow_light_feed = secrets["aio_username"] + "/feeds/grow_light"

# Setup a feed named 'pump' for subscribing to changes
pump_feed = secrets["aio_username"] + "/feeds/pump"

### Code ###

# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
def connected(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    print("Connected to Adafruit IO! Listening for topic changes on %s" % pump_feed)
    print("Connected to Adafruit IO! Listening for topic changes on %s" % grow_light_feed)
    # Subscribe to all changes on the onoff_feed.
    client.subscribe(pump_feed)
    client.subscribe(grow_light_feed)


def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    print("Disconnected from Adafruit IO!")


def message(client, topic, message):
    # This method is called when a topic the client is subscribed to
    # has a new message.
    print("New message on topic {0}: {1}".format(topic, message))

    if (topic == 'femur/feeds/pump') and (message == '1'):
        print('motor on')
        kit.motor1.throttle = 1
    else:
        print('motor off')
        kit.motor1.throttle = 0

    if (topic == 'femur/feeds/grow_light') and (message == '1'):
        print('grow lights on')
        pixels.fill(growcolor1)
        pixels.show()
    if (topic == 'femur/feeds/grow_light') and (message == '0'):
        print('grow lights off')
        pixels.fill(off)
        pixels.show()

# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

# Set up a MiniMQTT Client
mqtt_client = MQTT.MQTT(
    broker=secrets["broker"],
    port=secrets["port"],
    username=secrets["aio_username"],
    password=secrets["aio_key"],
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
)

# Setup the callback methods above
mqtt_client.on_connect = connected
mqtt_client.on_disconnect = disconnected
mqtt_client.on_message = message

# Connect the client to the MQTT broker.
print("Connecting to Adafruit IO...")
mqtt_client.connect()

while True:
    # Poll the message queue
    for i in range(0,data_interval,1):
        try:
            mqtt_client.loop()
        except:
            print ("mqtt fail")
            time.sleep(5)
            pass
        if (i!=0) and (i<data_interval):
            time.sleep(1)
        else:
            temp_value = sensor.temperature
            print("\nTemperature: %0.1f C" % sensor.temperature)
            humidity_value = sensor.relative_humidity
            print("Humidity: %0.1f %%" % sensor.relative_humidity)
            moist_value = ss.moisture_read()/10
            print("moisture: " + str(moist_value))
            light_value = veml7700.light
            print("Ambient light:", veml7700.light)

            # Send a new message
            mqtt_client.publish(temperature_feed, temp_value)
            mqtt_client.publish(humidity_feed, humidity_value)
            mqtt_client.publish(soil_feed, moist_value)
            mqtt_client.publish(light_feed, light_value)
            print("Data Published!")
            print(str(data_interval) + ' seconds to next data drop')
        if (light_value < 7000):
            print('grow lights on')
            pixels.fill(growcolor1)
            pixels.show()
        else:
            print('grow lights off')
            pixels.fill(off)
            pixels.show()
    if (moist_value < 70):
        kit.motor1.throttle = 1
        time.sleep(20)
        kit.motor1.throttle = 0
