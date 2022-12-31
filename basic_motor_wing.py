# motor control
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Simple test for using adafruit_motorkit with a DC motor"""
import time
import board
from adafruit_motorkit import MotorKit

kit = MotorKit(i2c=board.I2C())

while True:
    kit.motor1.throttle = 1 #change to -1 to reverse the direction of the motor
    print('motor on')
    time.sleep(10.0)
    kit.motor1.throttle = 0
    print('motor off')
    time.sleep(10.0)
