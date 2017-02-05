#======================================================================
#
# Python Module to handle an HC-SR04 Ultrasonic Module 
# Aimed at use on Picon Zero
#
#======================================================================

import RPi.GPIO as GPIO, time
import piconzero as pz

# Define Sonar Pin (Uses same pin for both Ping and Echo on piconzero dedicated pins)
sonar1trig = 38 #  dedicated pin on piconzero for sonar trig and echo
sonar1echo = 38
sonar2trig = 13 # spare pins on piconzero
sonar2echo = 15 
samples = 8         # number of samples for average
variance = 0.5     # ignore readings 25% different to current average
interval = 0.05     # interval between readings in seconds
distancesamples1 = [20, 20, 20, 20, 20, 20, 20, 20] # setup initial readings 
distancesamples2 = [20, 20, 20, 20, 20, 20, 20, 20]

sensoronright = 0   # set to 1 if on right 0 if on left
piwidth = 10 # width of pi robot in cm
runwidth = 54  # width of speed test run in cm
mediumturndistance = 20 # distance from wall for medium turn
fastturndistance = 10   # distance from wall for fast turn
turnleft = 35
turnright = 20
hardturnleft = 45
hardturnright = 10
sensordeltaforturn = 1.5 # turn if difference between sensors in greater (cm)
mediumspeed = 10   # slow speed for medium turn
fastspeed = 15     # slow speed for fast turn  
speed = 50         # normal speed
rightwheel = 1      # wheel number for setMotor function
leftwheel = 0
frontturndistance = 15

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
#    print("trig", trig, "echo", echo)
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

# function to calculate moving average
# discards lowest and highest readings and returns average of the rest
def movingaverage(distancesamples):
    minsample = 55
    maxsample= 0
    for x in range(samples): 
        if distancesamples[x] > maxsample: # new high value
            maxsample = distancesamples[x]
        elif distancesamples[x] < maxsample: # new low value
            minsample = distancesamples[x]           
    averagedistance = (sum(distancesamples) - maxsample - minsample) / (samples - 2)
    print(averagedistance, minsample, maxsample)
    return averagedistance

init() # initialise the boards
time.sleep(2)   # wait for pi to settle down

# get initial set of readings before we start the motors
for x in range(samples):
    distancesamples1[x] = getDistance(sonar1trig, sonar1echo)    
averagedistance1 = sum(distancesamples1) /samples

for x in range(samples):
    distancesamples2[x] = getDistance(sonar2trig, sonar2echo)    
averagedistance2 = sum(distancesamples2) / samples

lastdistance = averagedistance2

pz.forward(speed)   # go go go

try:
    while True:
        # get new sensor value and add to range to calculate average

        time.sleep(interval)
        distance = getDistance(sonar1trig, sonar1echo)  # get distance from sonar 1
        
        #if distance <= 150: # if distance reading over 100 then discard as greater than distance between walls
        del(distancesamples1[0])    # remove oldest value
        distancesamples1.append(distance)   # append newest value
        averagedistance1 = movingaverage(distancesamples1)  # get average of samples
        #else:
        #    print("Faulty distance reading 1", distance)      
        print("Sonar 1", int(distance), int(averagedistance1), distancesamples1)

        time.sleep(interval)
        distance = getDistance(sonar2trig, sonar2echo)  # get distance from sonar 2
        
        if distance <= 55:   # if distance reading over 55 then discard as greater than distance between walls
            del(distancesamples2[0])    # remove oldest value
            distancesamples2.append(distance) # append newest value
            averagedistance2 = movingaverage(distancesamples2)  # get average of samples
        else:
            print("Faulty distance reading 2", distance)
            distance = lastdistance
        print("Sonar 2", int(distance), int(averagedistance2), distancesamples2)
         
        pz.forward(speed)   # set speed back to default. will be overwritten if need for turn     

        if (averagedistance1 <= frontturndistance): # about to hit corner so turn right
            pz.spinRight(speed - mediumspeed)
            print("Corner ... spin right", averagedistance1)
            time.sleep(interval)
            distance = getDistance(sonar2trig, sonar2echo)  # get distance from sonar 2
            while (distance >= 55):   # keep turning until good reading from side wall
                time.sleep(interval)
                distance = getDistance(sonar2trig, sonar2echo)  # get distance from sonar 2            
        # check if need to turn - slow down wheel on side to turn
        elif (averagedistance2 >= (lastdistance + sensordeltaforturn)): # heading left so turn right
            pz.setMotor(rightwheel, speed - mediumspeed)
            print("Turning Right 2", averagedistance2, lastdistance)
        elif (averagedistance2 <= (lastdistance - sensordeltaforturn)):  # heading right so turn left
            pz.setMotor(leftwheel, speed - mediumspeed)
            print("Turning Left 2", averagedistance2, lastdistance)    
        elif averagedistance2 >= hardturnleft: # if too near wall then fast turn
            pz.setMotor(leftwheel, speed - fastspeed)
            print("Hard Left", averagedistance2, distance)
        elif averagedistance2 >= turnleft: # if close to wall then turn
            pz.setMotor(leftwheel, speed - mediumspeed)
            print("Left", averagedistance2, distance)
        elif averagedistance2 <= hardturnright:
            pz.setMotor(rightwheel, speed - fastspeed)
            print("Hard Right", averagedistance2, distance)
        elif averagedistance2 <= turnright:
            pz.setMotor(rightwheel, speed - mediumspeed)
            print("Right", averagedistance2, distance)
        lastdistance = distance
            
except KeyboardInterrupt:
    print ()

finally:
    pz.cleanup()
