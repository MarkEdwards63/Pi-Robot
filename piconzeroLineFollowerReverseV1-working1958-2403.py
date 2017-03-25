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

# define motor speed values
leftMotor = 0   # set 0 or 1 for piconzero setMotor
rightMotor = 1
driveLeft = 0.5     # set initial values to move forward at half speed
driveRight = 0.5
oldDriveLeft = 0.5
oldDriveRight = 0.5
interval = 0.01  # interval in seconds between readings
# Setup the power limit
maxPower = 100
count = 0

# Setup pins for line following sensor
GPIO.setwarnings(False)         # disable warnings
GPIO.setmode(GPIO.BCM)          # Broadcom pin-numbering scheme
GPIO.setup(leftPin, GPIO.IN)    # set pins as inputs for GPIO
GPIO.setup(middlePin, GPIO.IN)
GPIO.setup(rightPin, GPIO.IN)

# Setup the piconzero
pz.init()

# make sure motors are off 
pz.stop()

# funtions

# read inputs from sensor which has three to check
def readInputs():
    left = 0    # default is off; overwirte to 1 if we see it
    middle = 0
    right = 0

    if GPIO.input(leftPin) == False:
#        print("left")
        left = 1

    if GPIO.input(middlePin) == False:
#        print("middle")
        middle = 1

    if GPIO.input(rightPin) == False:
#        print("right")
        right = 1

    returnValues = [left, middle, right]
    return returnValues

# main control loop
try:
    while True:
        line = readInputs() # call the read line following sensor function
        print(line)
        time.sleep(interval) # wait between readings
	count += 1
        # if line is on left turn right
        if (line == [1, 1, 0]) or (line == [1, 0, 0]):
            driveLeft = 1.0
            driveRight = -0.1
            print("Turn Right")
            
        # if line is central, power both motors
        elif (line == [1, 0, 1]):
            driveLeft = 1.0
            driveRight = 1.0
            print("Straight")
		 
        # if line is on right turn left
        elif (line == [0, 1, 1]) or (line == [0, 0, 1]):

            driveLeft = -0.1
            driveRight = 1.0
            print("Turn Left")

        # if can't see line, repeat last move
        elif (line == [1, 1, 1]):
            driveLeft = oldDriveLeft
            driveRight = oldDriveRight
            print("Repeat 1 1 1")
#             driveLeft = 1.0
#             driveRight = 1.0
#             print("Straight 1 1 1 ")
            
        # if see all the line, repeat last move
        elif (line == [0, 0, 0]):
            driveLeft = oldDriveLeft
            driveRight = oldDriveRight
            print("rEPEAT ")
        
        # save driveLeft and driveRight to oldDriveLeft and oldDriveRight
        oldDriveLeft = driveLeft
        oldDriveRight = driveRight
	
        # update motor values
        print("Power / Left / Right", count, maxPower, driveLeft, driveRight)	
        pz.setMotor(leftMotor, int(driveLeft * maxPower))
        pz.setMotor(rightMotor, int(driveRight * maxPower))

            
except KeyboardInterrupt:
    print ("Keyboard Interupt")
    
finally:
    print("Cleanup at end")
    pz.cleanup()
