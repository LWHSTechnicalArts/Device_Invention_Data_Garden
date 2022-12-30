# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT
# Modified by akleindolph 2022

import time
import board
import neopixel

pixel_pin = board.A2
num_pixels = 24

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.4, auto_write=False, pixel_order=neopixel.GRBW)

growcolor1 = (255, 0, 140, 100)  #RGBW = red, green, blue, white
growcolor2 = (180, 200, 255, 0)

while True:
    pixels.fill(growcolor1)
    pixels.show()
    time.sleep(10)
    pixels.fill(growcolor2)
    pixels.show()
    time.sleep(10)
