# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
from adafruit_seesaw.seesaw import Seesaw

i2c = board.I2C()

ss = Seesaw(i2c, addr=0x36)

while True:
    # read moisture level through capacitive touch pad
    touch = ss.moisture_read()

    print("moisture: " + str(touch))
    time.sleep(1)
