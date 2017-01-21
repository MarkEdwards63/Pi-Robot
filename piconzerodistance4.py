#======================================================================
#
# Python Module to handle an HC-SR04 Ultrasonic Module on a single Pin
# Aimed at use on Picon Zero
#
# Created by Gareth Davies, Mar 2016
# Copyright 4tronix
#
# This code is in the public domain and may be freely copied and used
# No warranty is provided or implied
#
#======================================================================

import RPi.GPIO as GPIO, sys, threading, time, os, subprocess
import piconzero as pz

# Define Sonar Pin (Uses same pin for both Ping and Echo)

sonartrig = 38 # old 38 or 23
sonarecho = 38 # old 38 or 23
samples = 5     # number of samples for average
variance = 1  # ignore readings 10% different to current average
interval = 0.1  # interval between readings
distancesamples = [10,10,10,10,10]

turnleft = 37.5
turnright = 12.5
hardturnleft = 44
hardturnright = 6

speed = 100

#======================================================================
# General Functions
#
def init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    pz.init()

def cleanup():
    GPIO.cleanup()

#======================================================================

#======================================================================
# UltraSonic Functions
#
# getDistance(). Returns the distance in cm to the nearest reflecting object. 0 == no object
def getDistance(trig, echo):
    GPIO.setup(trig, GPIO.OUT)
    # Send 10us pulse to trigger
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)
    start = time.time()
    count=time.time()
    GPIO.setup(echo,GPIO.IN)
    while GPIO.input(echo)==0 and time.time()-count<0.1:
        start = time.time()
    count=time.time()
    stop=count
    while GPIO.input(echo)==1 and time.time()-count<0.1:
        stop = time.time()
    # Calculate pulse length
    elapsed = stop-start
    # Distance pulse travelled in that time is time
    # multiplied by the speed of sound (cm/s)
    distance = elapsed * 34000
    # That was the distance there and back so halve the value
    distance = distance / 2
    return distance

# End of UltraSonic Functions    
#======================================================================
init()

for x in range(samples):
    distancesamples[x] = getDistance(sonartrig, sonarecho)    
averagedistance = sum(distancesamples) /samples

pz.forward(speed)

try:
    while True:
        for x in range(samples):
            time.sleep(interval)
            distance = getDistance(sonartrig, sonarecho)
#    if (distance < variance * (1 + averagedistance)) and (distance > variance * (1 - averagedistance)):
            del(distancesamples[0])
            distancesamples.append(distance)
            averagedistance = sum(distancesamples) / samples
            print("Sonar 1", int(distance), distancesamples, int(averagedistance))
        averagedistance = distance
        pz.forward(speed)
        if averagedistance >= hardturnleft:
            pz.setMotor(1, speed - 30)
            print("Hard Left")
        elif averagedistance >= turnleft:
            pz.setMotor(1, speed - 15)
            print("Left")

        if averagedistance <= hardturnright:
            pz.setMotor(0, speed - 30)
            print("Hard Right")
        elif averagedistance <= turnright:
            pz.setMotor(0, speed - 15)
            print("Right")


except KeyboardInterrupt:
    print ()

finally:
    pz.cleanup()
