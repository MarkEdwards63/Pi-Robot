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
sonar1 = 38 # old 38 or 23
sonar2 = 38 # old 38 or 23
samples = 5     # number of samples for average
variance = 1  # ignore readings 10% different to current average
interval = 0.1  # interval between readings
distancesamples1 = [10,10,10,10,10]
distancesamples2 = [10,10,10,10,10]

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
def getDistance(sonar):
    GPIO.setup(sonar, GPIO.OUT)
    # Send 10us pulse to trigger
    GPIO.output(sonar1, True)
    time.sleep(0.00001)
    GPIO.output(sonar1, False)
    start = time.time()
    count=time.time()
    GPIO.setup(sonar1,GPIO.IN)
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
    distancesamples1[x] = getDistance(sonar1)    
averagedistance1 = sum(distancesamples1) /samples

for x in range(samples):
    distancesamples2[x] = getDistance(sonar2)    
averagedistance2 = sum(distancesamples2) / samples



while True:
    for x in range(samples):
        time.sleep(interval)
        distance = getDistance(sonar1)
#    if (distance < variance * (1 + averagedistance)) and (distance > variance * (1 - averagedistance)):
        del(distancesamples1[0])
        distancesamples1.append(distance)
        averagedistance1 = sum(distancesamples1) / samples
        print("Sonar 1", int(distance), distancesamples1, int(averagedistance1))


    for x in range(samples):
        time.sleep(interval)
        distance = getDistance(sonar2)
#    if (distance < variance * (1 + averagedistance)) and (distance > variance * (1 - averagedistance)):
        del(distancesamples2[0])
        distancesamples2.append(distance)
        averagedistance2 = sum(distancesamples2) / samples
        print("Sonar 2", int(distance), distancesamples2, int(averagedistance2))
