#======================================================================
#
# Python Module to handle an HC-SR04 Ultrasonic Module 
# Aimed at use on Picon Zero
#
#======================================================================

import RPi.GPIO as GPIO, time
import piconzero as pz

# Define Sonar Pin (Uses same pin for both Ping and Echo on piconzero dedicated pins)
sonar1trig = 13 # spare pins on piconzero
sonar1echo = 15
sonar2trig = 38 # dedicated pin on piconzero for sonar trig and echo
sonar2echo = 38 
samples = 5         # number of samples for average
variance = 0.5     # ignore readings 25% different to current average
interval = 0.1     # interval between readings in seconds
distancesamples1 = [20, 20, 20, 20, 20] # setup initial readings 
distancesamples2 = distancesamples1

sensoronright = 0   # set to 1 if on right 0 if on left
piwidth = 10   # width of pi robot in cm
runwidth = 70  # width of speed test run in cm
mediumturndistance = 30 # distance from wall for medium turn
fastturndistance = 15   # distance from wall for fast turn
turnleft = 35
turnright = 25
hardturnleft = 45
hardturnright = 10
sensordeltaforturn = 2 # turn if difference between sensors in greater (cm)
mediumspeed = 15   # slow speed for medium turn
fastspeed = 30     # slow speed for fast turn  
speed = 60         # normal speed

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
init()

# get initial set of readings before we start the motors
for x in range(samples):
    distancesamples1[x] = getDistance(sonar1trig, sonar1echo)    
averagedistance1 = sum(distancesamples1) /samples

for x in range(samples):
    distancesamples2[x] = getDistance(sonar2trig, sonar2echo)    
averagedistance2 = sum(distancesamples2) / samples

pz.forward(speed)   # go go go

try:
    while True:
        # get new sensor value and add to range to calculate average
        for x in range(samples):
            time.sleep(interval)
            distance = getDistance(sonar1trig, sonar1echo)
            if (distance < (averagedistance1 * (1 + variance))) and (distance > (averagedistance1 * (1 - variance))):
                del(distancesamples1[0])    # replace oldest sample with newest
                distancesamples1.append(distance)
            else:
                print("Variance too much", distance, averagedistance1)
            averagedistance1 = sum(distancesamples1) / samples
            print("Sonar 1", int(distance), distancesamples1, int(averagedistance1))

        # use average of both sensors
        averagedistance = (averagedistance1 + averagedistance2) / 2
        pz.forward(speed)   # set speed back to default. will be overwritten if need for turn
  
        if averagedistance >= hardturnleft: # if too near wall then fast turn
            pz.setMotor(0, speed - fastspeed)
            print("Hard Left")
        elif averagedistance >= turnleft: # if close to wall the turn
            pz.setMotor(0, speed - mediumspeed)
            print("Left")

        if averagedistance <= hardturnright:
            pz.setMotor(1, speed - fastspeed)
            print("Hard Right")
        elif averagedistance <= turnright:
            pz.setMotor(1, speed - mediumspeed)
            print("Right")

        for x in range(samples):
            time.sleep(interval)
            distance = getDistance(sonar2trig, sonar2echo)
            if (distance < (averagedistance2 * (1 + variance))) and (distance > (averagedistance2 * (1 - variance))):
                del(distancesamples2[0])
                distancesamples2.append(distance)
            averagedistance2 = sum(distancesamples2) / samples
            print("Sonar 2", int(distance), distancesamples2, int(averagedistance2))

        averagedistance = (averagedistance1 + averagedistance2) / 2
        pz.forward(speed)
  
        if averagedistance >= hardturnleft:
            pz.setMotor(0, speed - fastspeed)
            print("Hard Left")
        elif averagedistance >= turnleft:
            pz.setMotor(0, speed - mediumspeed)
            print("Left")

        if averagedistance <= hardturnright:
            pz.setMotor(1, speed - fastspeed)
            print("Hard Right")
        elif averagedistance <= turnright:
            pz.setMotor(1, speed - mediumspeed)
            print("Right")
            
except KeyboardInterrupt:
    print ()

finally:
    pz.cleanup()
