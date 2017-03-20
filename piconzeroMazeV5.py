#======================================================================
#
# Python Module to handle an HC-SR04 Ultrasonic Module 
# Aimed at use on Picon Zero
#
#======================================================================

import RPi.GPIO as GPIO, time
import piconzero as pz
import VL53L0X

# Using VL53L0X Time of Flight sensor with pins to turn each off and on
# GPIO for ToF Sensor 1 shutdown pin
sensorFront_shutdown = 16
# GPIO for ToF Sensor 2 shutdown pin
sensorLeft_shutdown = 20
# GPIO for ToF Sensor 3 shutdown pin
sensorRight_shutdown = 21

sensoronright = 0   # set to 1 if on right 0 if on left
piwidth = 100 # width of pi robot in cm
runwidth = 540  # width of speed test run in cm
# frontDistanceTurn = 140 # 200
mediumturndistance = 200 # distance from wall for medium turn
fastturndistance = 100   # distance from wall for fast turn
turnleft = 180
turnright = 120
hardturnleft = 220
hardturnright = 80
sensordeltaforturn = 5 # turn if difference between sensors in greater (mm)
mediumspeed = 40   # slow speed for medium turn 15
fastspeed = 50     # slow speed for fast turn   20
speed = 100        # normal speed
spinSpeed = 60
speedLeft = speed
speedRight = speed 
mediumspeedLeft = 25
mediumspeedRight = 25
fastspeedLeft = 40
fastspeedRight = 40
rightwheel = 1      # wheel number for setMotor function
leftwheel = 0
frontturndistance =  200    # maze walls are 360 mm apart so aim for middle 210
stopTurningDistance = 200

#======================================================================
# General Functions
#
def init():
    GPIO.setwarnings(False)
#    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    # Setup GPIO for shutdown pins on each VL53L0X
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(sensorFront_shutdown, GPIO.OUT)
    GPIO.setup(sensorLeft_shutdown, GPIO.OUT)
    GPIO.setup(sensorRight_shutdown, GPIO.OUT)

    # Set all shutdown pins low to turn off each VL53L0X
    GPIO.output(sensorFront_shutdown, GPIO.LOW)
    GPIO.output(sensorLeft_shutdown, GPIO.LOW)
    GPIO.output(sensorRight_shutdown, GPIO.LOW)

    # Keep all low for 500 ms or so to make sure they reset
    time.sleep(0.50)
    pz.init()

def cleanup():
    GPIO.cleanup()

init() # initialise the boards
time.sleep(2)   # wait for pi to settle down

# VL53L0X_GOOD_ACCURACY_MODE      = 0   # Good Accuracy mode
# VL53L0X_BETTER_ACCURACY_MODE    = 1   # Better Accuracy mode
# VL53L0X_BEST_ACCURACY_MODE      = 2   # Best Accuracy mode
# VL53L0X_LONG_RANGE_MODE         = 3   # Longe Range mode
# VL53L0X_HIGH_SPEED_MODE         = 4   # High Speed mode

# Create one object per VL53L0X passing the address to give to
# each.
tofFront = VL53L0X.VL53L0X(address=0x2B)
tofLeft = VL53L0X.VL53L0X(address=0x2D)
tofRight = VL53L0X.VL53L0X(address=0x2E)

# Set shutdown pin high for the first front VL53L0X then 
# call to start ranging 
GPIO.output(sensorFront_shutdown, GPIO.HIGH) # front
time.sleep(0.50)
tofFront.start_ranging(VL53L0X.VL53L0X_HIGH_SPEED_MODE)

# Set shutdown pin high for the second VL53L0X then 
# call to start ranging 
GPIO.output(sensorLeft_shutdown, GPIO.HIGH) # left
time.sleep(0.50)
tofLeft.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

# Set shutdown pin high for the third VL53L0X then 
# call to start ranging 
#GPIO.output(sensorRight_shutdown, GPIO.HIGH) # right
#time.sleep(0.50)
#tofRight.start_ranging(VL53L0X.VL53L0X_HIGH_SPEED_MODE)

# find gap between ToF readings
timing = tofFront.get_timing()
if (timing < 20000):
    timing = 20000
print ("Timing %d ms" % (timing/1000))
interval = timing/1000000.00
#interval = 0.05
print(interval)

# initial distance for front sensor
distanceFront = tofFront.get_distance() 
if (distanceFront > 0):
    print ("sensor front %d - %d cm" % (tofFront.my_object_number, distanceFront))
else:
    print ("%d - Error" % tofFront.my_object_number)

# initial distance for side sensor
distanceSide = tofLeft.get_distance() 
if (distanceSide > 0):
    print ("sensor side %d - %d cm" % (tofLeft.my_object_number, distanceSide))
else:
    print ("%d - Error" % tofLeft.my_object_number)

time.sleep(interval)
time.sleep(2)
lastDistanceFront = distanceFront # used to work out delta between consecutive readings
lastDistanceSide = distanceSide

pz.setMotor(leftwheel, speedLeft)
pz.setMotor(rightwheel, speedRight) # go go go
count = 0

try:
    while False:    
#    while distanceSide <= 350:   # run 1 go forward 122 cm and turn right
                        # run 2 go forward 204 cm and turn right
                        # run 3 go forward 72 cm and turn right
        # get new sensor value and add to range to calculate average
        distanceFront = tofFront.get_distance()
        distanceSide =  tofLeft.get_distance()  # get distance from VL53

        print("Front distance", int(frontturndistance), int(distanceFront), int(lastDistanceFront))
        if distanceFront >= 2000: # if distance reading over 2 metres then discard as greater than distance between walls
            print("Faulty front distance reading", distanceFront)      
            distanceFront = lastDistanceFront
        print("Side distance", int(distanceSide), int(lastDistanceSide))
        lastDistanceFront = distanceFront
#        pz.setMotor(leftwheel, speedLeft)
#        pz.setMotor(rightwheel, speedRight)  # set speed back to default. will be overwritten if need for turn     

        if (distanceFront <= frontturndistance): # about to hit corner so turn right
            pz.spinRight(spinSpeed)
#            pz.setMotor(leftwheel, speedLeft)
#            pz.setMotor(rightwheel, speedRight - cornerSpeed)
            print("Corner ... spin right", distanceFront)
            time.sleep(interval)
            distanceFront = tofFront.get_distance() 
            
            while (distanceFront <= stopTurningDistance):   # keep turning until longer reading from side wall
                distanceFront = tofFront.get_distance() 
                time.sleep(interval)
                print("Corner turning ...", distanceFront)

            # now check side wall until //
            distanceSide = tofLeft.get_distance()
            lastDistanceSide = distanceSide
            time.sleep(interval)
            distanceSide = tofLeft.get_distance()
            print(distanceSide, lastDistanceSide)
            while (distanceSide <= lastDistanceSide):   # keep turning until parallel reading from side wall
                time.sleep(interval)
                lastDistanceSide = distanceSide
                distanceSide = tofLeft.get_distance() # get distance from VL53
                print("Corner turning still ...", distanceSide, lastDistanceSide)

            pz.setMotor(leftwheel, speedLeft)
            pz.setMotor(rightwheel, speedRight)

        # check if need to turn - slow down wheel on side to turn
        elif (distanceSide >= (lastDistanceSide + sensordeltaforturn)): # heading left so turn right
            pz.setMotor(rightwheel, speedRight)
            pz.setMotor(leftwheel, speedLeft - fastspeedLeft)
            print("Turning Left 2", distanceSide, lastDistanceSide)
        elif (distanceSide <= (lastDistanceSide - sensordeltaforturn)):  # heading right so turn left
            pz.setMotor(rightwheel, speedRight - fastspeedRight)
            pz.setMotor(leftwheel, speedLeft)
            print("Turning Right 2", distanceSide, lastDistanceSide)
        elif distanceSide >= hardturnleft: # if too near wall then fast turn
            pz.setMotor(rightwheel, speedRight)
            pz.setMotor(leftwheel, speedLeft - fastspeedLeft)
            print("Hard Left", distanceSide, lastDistanceSide)
        elif distanceSide <= hardturnright:  # if too near wall then fast turn
            pz.setMotor(rightwheel, speedRight - fastspeedRight)
            pz.setMotor(leftwheel, speedLeft)
            print("Hard Right", distanceSide, lastDistanceSide)
        elif distanceSide >= turnleft: # if close to wall then turn
            pz.setMotor(rightwheel, speedRight)
            pz.setMotor(leftwheel, speedLeft - mediumspeedLeft)
            print("Bare Left", distanceSide, lastDistanceSide)
        elif distanceSide <= turnright:  # if close to wall then turn
            pz.setMotor(leftwheel, speedLeft)
            pz.setMotor(rightwheel, speedRight - mediumspeedRight)
            print("Bare Right", distanceSide, lastDistanceSide)
        else:
            pz.setMotor(leftwheel, speedLeft)   # set speed back to default. w
            pz.setMotor(rightwheel, speedRight)

        time.sleep(interval)
        lastDistanceSide = distanceSide     # set distance for checking movement to/from wall

    print("New Run ..................................", distanceSide)

    # Set shutdown pin high for the third VL53L0X then 
    # call to start ranging
    
# VL53L0X_GOOD_ACCURACY_MODE      = 0   # Good Accuracy mode
# VL53L0X_BETTER_ACCURACY_MODE    = 1   # Better Accuracy mode
# VL53L0X_BEST_ACCURACY_MODE      = 2   # Best Accuracy mode
# VL53L0X_LONG_RANGE_MODE         = 3   # Longe Range mode
# VL53L0X_HIGH_SPEED_MODE         = 4   # High Speed mode

    tofLeft.stop_ranging()
    GPIO.output(sensorLeft_shutdown, GPIO.LOW)
    GPIO.output(sensorRight_shutdown, GPIO.HIGH) # right
    time.sleep(0.50)
    tofRight.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
    distanceSide =  tofRight.get_distance()  # get distance from VL53 using right now
    lastDistanceSide = distanceSide
    
    while True:   # run 4 go forward 72 cm and turn left
        # get new sensor value and add to range to calculate average

        # update distance as we are looking at right hand side now
        turnleft = 120
        turnright = 180
        hardturnleft = 100
        hardturnright = 250
        spinspeed = 70
        time.sleep(interval)
        distanceFront = tofFront.get_distance()
        distanceSide =  tofRight.get_distance()  # get distance from VL53 using right now

        print("Front distance", int(frontturndistance), int(distanceFront), int(lastDistanceFront))
        if distanceFront >= 2000: # if distance reading over 2 meters then discard as greater than distance between walls
            print("Faulty front distance reading", distanceFront)      
            distanceFront = lastDistanceFront
        
        print("Side distance", int(distanceSide), int(lastDistanceSide))
        lastDistanceFront = distanceFront
#        pz.setMotor(leftwheel, speedLeft)
#        pz.setMotor(rightwheel, speedRight)
        
        if (distanceFront <= frontturndistance): # about to hit corner so turn Left
            pz.spinLeft(spinSpeed)
            print("Corner ... spin Left", distanceFront)
            lastDistanceFront = distanceFront
            time.sleep(interval)
            distanceFront = tofFront.get_distance() 
            
            while (distanceFront <= stopTurningDistance):   # keep turning until bad reading from side wall
                time.sleep(interval)
                distanceFront = tofFront.get_distance() 
                print("Corner turning ...", distanceFront)

            # now check side wall until //
            distanceSide = tofRight.get_distance() 
            lastDistanceSide = distanceSide
            time.sleep(interval)
            distanceSide = tofRight.get_distance()
            while (distanceSide <= lastDistanceSide):   # keep turning until good reading from side wall
                time.sleep(interval)
                lastDistanceSide = distanceSide
                distanceSide = tofRight.get_distance() # get distance from VL53
                print("Corner turning still ...", distanceSide, lastDistanceSide)

            pz.setMotor(leftwheel, speedLeft)
            pz.setMotor(rightwheel, speedRight)

         # check if need to turn - slow down wheel on side to turn
        elif (distanceSide >= (lastDistanceSide + sensordeltaforturn)): # heading left so turn right
            pz.setMotor(rightwheel, speedRight - fastspeedRight)
            pz.setMotor(leftwheel, speedLeft)
            print("Turning Right 2", distanceSide, lastDistanceSide)
        elif (distanceSide <= (lastDistanceSide - sensordeltaforturn)):  # heading right so turn left
            pz.setMotor(rightwheel, speedRight)
            pz.setMotor(leftwheel, speedLeft - fastspeedLeft)
            print("Turning Left 2", distanceSide, lastDistanceSide)
        elif distanceSide <= hardturnleft: # if too near wall then fast turn
            pz.setMotor(rightwheel, speedRight)
            pz.setMotor(leftwheel, speedLeft - fastspeedLeft)
            print("Hard Left", distanceSide, lastDistanceSide, hardturnleft)
        elif distanceSide >= hardturnright:  # if too near wall then fast turn
            pz.setMotor(rightwheel, speedRight - fastspeedRight)
            pz.setMotor(leftwheel, speedLeft)
            print("Hard Right", distanceSide, lastDistanceSide, hardturnright)
        elif distanceSide <= turnleft: # if close to wall then turn
            pz.setMotor(rightwheel, speedRight)
            pz.setMotor(leftwheel, speedLeft - mediumspeedLeft)
            print("Bare Left", distanceSide, lastDistanceSide, turnleft)
        elif distanceSide >= turnright:  # if close to wall then turn
            pz.setMotor(leftwheel, speedLeft)
            pz.setMotor(rightwheel, speedRight - mediumspeedRight)
            print("Bare Right", distanceSide, lastDistanceSide, turnright)
        else:
            pz.setMotor(leftwheel, speedLeft)   # set speed back to default. w
            pz.setMotor(rightwheel, speedRight)
           
        lastDistanceSide = distanceSide     # set distance for checking movement to/from wall

        
except KeyboardInterrupt:
    print ("KeyBoard Interrupt")

finally:
    pz.cleanup()
    tofFront.stop_ranging()
    GPIO.output(sensorFront_shutdown, GPIO.LOW)
    tofLeft.stop_ranging()
    GPIO.output(sensorLeft_shutdown, GPIO.LOW)
    tofRight.stop_ranging()
    GPIO.output(sensorRight_shutdown, GPIO.LOW)
