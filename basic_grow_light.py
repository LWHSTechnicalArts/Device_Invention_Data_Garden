# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT
# Modified by akleindolph 2022

"""CircuitPython Essentials NeoPixel example"""
import time
import board
import neopixel

pixel_pin = board.A2
num_pixels = 24

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.7, auto_write=False)

growcolor1 = (180, 0, 255)
growcolor2 = (180, 200, 255)

while True:
    pixels.fill(growcolor1)
    pixels.show()
    time.sleep(10)
    pixels.fill(growcolor2)
    pixels.show()
    time.sleep(10)
