# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import ssl
import socketpool
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT

import board
import adafruit_ahtx0
from adafruit_seesaw.seesaw import Seesaw

from adafruit_motorkit import MotorKit

kit = MotorKit(i2c=board.I2C())
i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = adafruit_ahtx0.AHTx0(i2c)
ss = Seesaw(i2c, addr=0x36)

kit.motor1.throttle = 0  #turn motor off
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

# Setup a feed named 'pump' for subscribing to changes
pump_feed = secrets["aio_username"] + "/feeds/pump"

### Code ###

# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
def connected(client, userdata, flags, rc):
    # This function will be called when the client is connected
    # successfully to the broker.
    print("Connected to Adafruit IO! Listening for topic changes on %s" % pump_feed)
    # Subscribe to all changes on the onoff_feed.
    client.subscribe(pump_feed)


def disconnected(client, userdata, rc):
    # This method is called when the client is disconnected
    print("Disconnected from Adafruit IO!")


def message(client, topic, message):
    # This method is called when a topic the client is subscribed to
    # has a new message.
    print("New message on topic {0}: {1}".format(topic, message))

    if (topic == pump_feed) and (message == '1'): 
        print('motor on')
        kit.motor1.throttle = 1
    else:
        print('motor off')
        kit.motor1.throttle = 0

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
        if (i!=0) and (i<data_interval):
            time.sleep(1)
            print(str(data_interval-i) + ' secs to data drop')
        else:
            print("\nTemperature: %0.1f C" % sensor.temperature)
            print("Humidity: %0.1f %%" % sensor.relative_humidity)
            temp_value = sensor.temperature
            humidity_value = sensor.relative_humidity
            moist_value = ss.moisture_read()/10
            print("moisture: " + str(moist_value))

            # Send a new message
            mqtt_client.publish(temperature_feed, temp_value)
            mqtt_client.publish(humidity_feed, humidity_value)
            mqtt_client.publish(soil_feed, moist_value)
            print("Sent!")
