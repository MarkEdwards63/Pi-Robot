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


# Define Sonar Pin (Uses same pin for both Ping and Echo)
sonar = 38 # old 38 or 23
samples = 5     # number of samples for average
variance = 1  # ignore readings 10% different to current average
interval = 0.1  # interval between readings
distancesamples = [10,10,10,10,10]

#======================================================================
# General Functions
#
def init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

def cleanup():
    GPIO.cleanup()

#======================================================================

#======================================================================
# UltraSonic Functions
#
# getDistance(). Returns the distance in cm to the nearest reflecting object. 0 == no object
def getDistance():
    GPIO.setup(sonar, GPIO.OUT)
    # Send 10us pulse to trigger
    GPIO.output(sonar, True)
    time.sleep(0.00001)
    GPIO.output(sonar, False)
    start = time.time()
    count=time.time()
    GPIO.setup(sonar,GPIO.IN)
    while GPIO.input(sonar)==0 and time.time()-count<0.1:
        start = time.time()
    count=time.time()
    stop=count
    while GPIO.input(sonar)==1 and time.time()-count<0.1:
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
    distancesamples[x] = getDistance()    
averagedistance = sum(distancesamples) / samples

while True:
    time.sleep(interval)   
    distance = getDistance()
#    if (distance < variance * (1 + averagedistance)) and (distance > variance * (1 - averagedistance)):
    del(distancesamples[0])
    distancesamples.append(distance)
    averagedistance = sum(distancesamples) / samples
    print(int(distance), distancesamples, int(averagedistance))
