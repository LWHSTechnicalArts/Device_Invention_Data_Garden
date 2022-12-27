#moisture sensor example

import time
import board
from adafruit_seesaw.seesaw import Seesaw

i2c = board.I2C()

ss = Seesaw(i2c, addr=0x36)

while True:
    # read moisture level through capacitive touch pad
    moist_sense = ss.moisture_read()

    print("moisture: " + str(moist_sense))
    time.sleep(1)
