import time
import board
import adafruit_veml7700
import adafruit_ahtx0

i2c = board.I2C()  # uses board.SCL and board.SDA
veml7700 = adafruit_veml7700.VEML7700(i2c)
sensor = adafruit_ahtx0.AHTx0(i2c)

while True:
    #place what you want to print here:
    time.sleep(2)
