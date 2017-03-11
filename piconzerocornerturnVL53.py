#======================================================================
#
# Python Module to handle an HC-SR04 Ultrasonic Module 
# Aimed at use on Picon Zero
#
#======================================================================

import RPi.GPIO as GPIO, time
import piconzero as pz
import VL53L0X

# Define Sonar Pin (Uses same pin for both Ping and Echo on piconzero dedicated pins)
sonar1trig = 38 #  dedicated pin on piconzero for sonar trig and echo
sonar1echo = 38
samples = 8         # number of samples for average
variance = 0.5     # ignore readings 25% different to current average
interval = 0.05     # interval between readings in seconds
distancesamplesSide = [20, 20, 20, 20, 20, 20, 20, 20] # setup initial readings 
distancesamplesFront = [20, 20, 20, 20, 20, 20, 20, 20]

sensoronright = 0   # set to 1 if on right 0 if on left
piwidth = 10 # width of pi robot in cm
runwidth = 54  # width of speed test run in cm
mediumturndistance = 20 # distance from wall for medium turn
fastturndistance = 15   # distance from wall for fast turn
turnleft = 35
turnright = 20
hardturnleft = 45
hardturnright = 10
sensordeltaforturn = 15 # turn if difference between sensors in greater (cm)
mediumspeed = 15   # slow speed for medium turn
fastspeed = 20     # slow speed for fast turn  
speed = 100         # normal speed
rightwheel = 1      # wheel number for setMotor function
leftwheel = 0
frontturndistance = 30

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

# Create a VL53L0X object
tof = VL53L0X.VL53L0X()

# Start ranging

# VL53L0X_GOOD_ACCURACY_MODE      = 0   # Good Accuracy mode
# VL53L0X_BETTER_ACCURACY_MODE    = 1   # Better Accuracy mode
# VL53L0X_BEST_ACCURACY_MODE      = 2   # Best Accuracy mode
# VL53L0X_LONG_RANGE_MODE         = 3   # Longe Range mode
# VL53L0X_HIGH_SPEED_MODE         = 4   # High Speed mode

tof.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

timing = tof.get_timing()
if (timing < 20000):
    timing = 20000
print ("Timing %d ms" % (timing/1000))
interval = timing/1000000.00

# get initial set of readings before we start the motors
for x in range(samples):
#    distancesamples1[x] = getDistance(sonar1trig, sonar1echo)
    distancesamplesSide[x] = tof.get_distance() / 10
    time.sleep(interval)
averagedistanceSide = sum(distancesamplesSide) /samples

for x in range(samples):
    distancesamplesFront[x] = getDistance(sonar1trig, sonar1echo)    
averagedistanceFront = sum(distancesamplesFront) / samples

lastdistanceSide = averagedistanceSide
lastdistanceFront = averagedistanceFront

pz.forward(speed)   # go go go

try:
    while True:
        # get new sensor value and add to range to calculate average

        time.sleep(interval)
        distanceSide = tof.get_distance() / 10 # get distance from VL53

        #if distance <= 150: # if distance reading over 100 then discard as greater than distance between walls
        del(distancesamplesSide[0])            # remove oldest value
        distancesamplesSide.append(distanceSide)   # append newest value
        averagedistanceSide = movingaverage(distancesamplesSide)  # get average of samples
        averagedistanceSide = distanceSide
        #else:
        #    print("Faulty distance reading 1", distance)      
        print("VL53 Side", int(distanceSide), int(averagedistanceSide), distancesamplesSide)

        distanceFront = getDistance(sonar1trig, sonar1echo)  # get distance from sonar 2
        
#        if distanceFront <= 55:   # if distance reading over 55 then discard as greater than distance between walls
        del(distancesamplesFront[0])    # remove oldest value
        distancesamplesFront.append(distanceFront) # append newest value
        averagedistanceFront = movingaverage(distancesamplesFront)  # get average of samples
#        else:
#            print("Faulty distance reading sonar", distanceFront)
#            distanceFront = lastdistanceFront
        print("Sonar Front", int(distanceFront), int(averagedistanceFront), distancesamplesFront)
        averagedistanceFront = distanceFront
        pz.forward(speed)   # set speed back to default. will be overwritten if need for turn     

        if (averagedistanceFront <= frontturndistance): # about to hit corner so turn right
            pz.spinRight(speed - mediumspeed)
            print("Corner ... spin right", averagedistanceFront)
            time.sleep(interval)
            distanceFront = getDistance(sonar1trig, sonar1echo)  # get distance from sonar 2
            
            while (distanceFront <= 55):   # keep turning until bad reading from side wall
                time.sleep(interval)
                distanceFront = getDistance(sonar1trig, sonar1echo) # get distance from sonar
                print("Corner turning ...", distanceFront)
            distanceSide = tof.get_distance() / 10

            lastdistanceSide = distanceSide
            while (distanceSide >= lastdistanceSide):   # keep turning until good reading from side wall
                time.sleep(interval)
                lastdistanceSide = distanceSide
                distanceSide = tof.get_distance() / 10 # get distance from VL53
                print("Corner turning stil ...", distanceSide, lastdistanceSide)
            pz.forward(speed)        # check if need to turn - slow down wheel on side to turn
        elif (averagedistanceSide >= (lastdistanceSide + sensordeltaforturn)): # heading left so turn right
            pz.setMotor(rightwheel, speed - mediumspeed)
            print("Turning Right 2", averagedistanceSide, lastdistanceSide)
        elif (averagedistanceSide <= (lastdistanceSide - sensordeltaforturn)):  # heading right so turn left
            pz.setMotor(leftwheel, speed - mediumspeed)
            print("Turning Left 2", averagedistanceSide, lastdistanceSide)    
        elif averagedistanceSide >= hardturnleft: # if too near wall then fast turn
            pz.setMotor(leftwheel, speed - fastspeed)
            print("Hard Left", averagedistanceSide, distanceSide)
        elif averagedistanceSide >= turnleft: # if close to wall then turn
            pz.setMotor(leftwheel, speed - mediumspeed)
            print("Left", averagedistanceSide, distanceSide)
        elif averagedistanceSide <= hardturnright:
            pz.setMotor(rightwheel, speed - fastspeed)
            print("Hard Right", averagedistanceSide, distanceSide)
        elif averagedistanceSide <= turnright:
            pz.setMotor(rightwheel, speed - mediumspeed)
            print("Right", averagedistanceSide, distanceSide)
        lastdistanceSide = distanceSide
            
except KeyboardInterrupt:
    print ()

finally:
    pz.cleanup()
