import time
import ssl
import os
import socketpool
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from adafruit_io.adafruit_io import IO_MQTT
from random import randint
import board
import digitalio
import supervisor

# --- Button Setup ---
red = digitalio.DigitalInOut(board.A1)
green = digitalio.DigitalInOut(board.A5)
yellow = digitalio.DigitalInOut(board.A3)

for button in [red, green, yellow]:
    button.direction = digitalio.Direction.INPUT
    button.pull = digitalio.Pull.UP

# --- LED ---
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# --- Counters ---
redNum = 0
greenNum = 0
yellowNum = 0

# --- Connect to WiFi ---
print("Connecting to WiFi...")
wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
print("Connected to WiFi!")

# --- MQTT Setup ---
pool = socketpool.SocketPool(wifi.radio)
mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    username=os.getenv("ADAFRUIT_AIO_USERNAME"),
    password=os.getenv("ADAFRUIT_AIO_KEY"),
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
)
io = IO_MQTT(mqtt_client)

# --- Connection Callback ---
def connected(client):
    print("Connected to Adafruit IO!")

io.on_connect = connected

# --- Reconnect Logic ---
def reconnect_mqtt():
    retries = 0
    while retries < 5:
        try:
            if not wifi.radio.is_connected:
                print("WiFi dropped. Reconnecting...")
                wifi.radio.connect(os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD"))
                print("WiFi reconnected")

            if not io.is_connected:
                print("MQTT disconnected. Reconnecting...")
                io.reconnect()
                print("MQTT reconnected")
            return
        except Exception as e:
            print(f"Reconnect failed ({retries+1}/5):", e)
            retries += 1
            time.sleep(5)

    print("Failed to reconnect after multiple attempts. Restarting...")
    time.sleep(2)
    supervisor.reload()

# --- Initial Connect ---
try:
    io.connect()
except Exception as e:
    print("Initial MQTT connect failed:", e)
    reconnect_mqtt()

# --- Heartbeat Timer ---
heartbeat_interval = 60  # seconds
last_heartbeat = time.monotonic()

# --- Main Loop ---
while True:
    led.value = True

    # Check connection
    if not io.is_connected:
        print("MQTT not connected. Trying to reconnect...")
        reconnect_mqtt()

    # Heartbeat
    if time.monotonic() - last_heartbeat > heartbeat_interval:
        try:
            io.publish("heartbeat", time.time())
            print("Sent heartbeat")
            last_heartbeat = time.monotonic()
        except Exception as e:
            print("Heartbeat publish failed:", e)
            reconnect_mqtt()

    # Red button
    if not red.value:
        time.sleep(0.2)
        while not red.value:
            pass
        redNum += 1
        try:
            io.publish("RedRed", redNum)
            print(f"redNum: {redNum}")
        except Exception as e:
            print("Red publish failed:", e)
            reconnect_mqtt()

    # Green button
    if not green.value:
        time.sleep(0.2)
        while not green.value:
            pass
        greenNum += 1
        try:
            io.publish("Green", greenNum)
            print(f"greenNum: {greenNum}")
        except Exception as e:
            print("Green publish failed:", e)
            reconnect_mqtt()

    # Yellow button
    if not yellow.value:
        time.sleep(0.2)
        while not yellow.value:
            pass
        yellowNum += 1
        try:
            io.publish("Yellow", yellowNum)
            print(f"yellowNum: {yellowNum}")
        except Exception as e:
            print("Yellow publish failed:", e)
            reconnect_mqtt()

    time.sleep(0.1)  # Slight delay to avoid spamming loop
