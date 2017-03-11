#!/usr/bin/env python
# coding: Latin-1

# some of the code in this program is from the example code by PiBorg.
# more imformation can be found here.
# https://github.com/piborg/zeroborg/
#
# the joy of open source code :-D

# import libraries required
import piconzero as pz
import RPi.GPIO as GPIO
import time

# define pins for the line following sensor
leftPin = 18
middlePin = 27
rightPin = 22

# Setup pins for line following sensor
GPIO.setwarnings(False)         # disable warnings
GPIO.setmode(GPIO.BCM)          # Broadcom pin-numbering scheme
GPIO.setup(leftPin, GPIO.IN)    # set pins as inputs for GPIO
GPIO.setup(middlePin, GPIO.IN)
GPIO.setup(rightPin, GPIO.IN)

# Setup the piconzero
pz.init()

# Setup the power limit
maxPower = 100

# define motor  values
leftMotor = 0   # set 0 or 1 for piconzero setMotor
rightMotor = 1
driveLeft = 0.5     # set initial values to move forward at half speed
driveRight = 0.5
oldDriveLeft = 0.5
oldDriveRight = 0.5
interval = 0.1  # interval in seconds between readings

# make sure motors are off 
pz.stop()

# funtions

# read inputs from sensor which has three to check
def readInputs():
    left = 0    # default is off; overwrite to 1 if we see it
    middle = 0
    right = 0

    if GPIO.input(leftPin) == False:
        print("left")
        left = 1

    if GPIO.input(middlePin) == False:
        print("middle")
        middle = 1

    if GPIO.input(rightPin) == False:
        print("right")
        right = 1

    returnValues = [left, middle, right]
    return returnValues

# main control loop
try:
    while True:
        line = readInputs() # call the read line following sensor function
        print("Left - Middle - Right", line)
        time.sleep(interval) # wait between readings

#--------- example 1 adjust left or right ---------------
        # if line is on right turn left
        if (line == [1, 1, 0])
            driveLeft = 0.6
            driveRight = -0.6
            print("Turn Left")
 
        pz.setMotor(leftMotor, int(-driveLeft * maxSpeed))
        pz.setMotor(rightMotor, int(-driveRight * maxSpeed))

#--------- example 1 spin left or right or forward ---------------
        # if line is on right spin left
        if (line == [1, 1, 0])
            pz.spinleft(speed)
            print("Spin Left")
           
except KeyboardInterrupt:
    print ("Keyboard Interupt")
    
finally:
    print("Cleanup at end")
    pz.cleanup()
