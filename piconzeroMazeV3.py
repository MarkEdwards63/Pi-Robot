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
sensor1_shutdown = 16
# GPIO for ToF Sensor 2 shutdown pin
sensor2_shutdown = 20

sensoronright = 0   # set to 1 if on right 0 if on left
piwidth = 100 # width of pi robot in cm
runwidth = 540  # width of speed test run in cm
frontDistanceTurn = 200
mediumturndistance = 200 # distance from wall for medium turn
fastturndistance = 100   # distance from wall for fast turn
turnleft = 180
turnright = 150
hardturnleft = 250
hardturnright = 80
sensordeltaforturn = 5 # turn if difference between sensors in greater (mm)
mediumspeed = 40   # slow speed for medium turn 15
fastspeed = 50     # slow speed for fast turn   20
speed = 100         # normal speed
speedLeft = speed
speedRight = speed - 8
mediumspeedLeft = 25
mediumspeedRight = 25
fastspeedLeft = 40
fastspeedRight = 40
rightwheel = 1      # wheel number for setMotor function
leftwheel = 0
frontturndistance = 210     # maze walls are 360 mm apart so aim for middle
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
    GPIO.setup(sensor1_shutdown, GPIO.OUT)
    GPIO.setup(sensor2_shutdown, GPIO.OUT)

    # Set all shutdown pins low to turn off each VL53L0X
    GPIO.output(sensor1_shutdown, GPIO.LOW)
    GPIO.output(sensor2_shutdown, GPIO.LOW)

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
tof1 = VL53L0X.VL53L0X(address=0x2B)
tof2 = VL53L0X.VL53L0X(address=0x2D)

# Set shutdown pin high for the first front VL53L0X then 
# call to start ranging 
GPIO.output(sensor1_shutdown, GPIO.HIGH)
time.sleep(0.50)
tof1.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

# Set shutdown pin high for the second VL53L0X then 
# call to start ranging 
GPIO.output(sensor2_shutdown, GPIO.HIGH)
time.sleep(0.50)
tof2.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

# find gap between ToF readings
timing = tof2.get_timing()
if (timing < 20000):
    timing = 20000
print ("Timing %d ms" % (timing/1000))
interval = timing/1000000.00
#interval = 0.05

# initial distance for front sensor
distanceFront = tof1.get_distance() 
if (distanceFront > 0):
    print ("sensor %d - %d cm" % (tof1.my_object_number, distanceFront))
else:
    print ("%d - Error" % tof1.my_object_number)

# initial distance for side sensor
distanceSide = tof2.get_distance() 
if (distanceSide > 0):
    print ("sensor %d - %d cm" % (tof2.my_object_number, distanceSide))
else:
    print ("%d - Error" % tof2.my_object_number)

time.sleep(interval)

lastDistanceFront = distanceFront # used to work out delta between consecutive readings
lastDistanceSide = distanceSide

pz.setMotor(leftwheel, speedLeft)
pz.setMotor(rightwheel, speedRight) # go go go
count = 0

try:
    onRun = 1
    while onRun <= 3:   # run 1 go forward 122 cm and turn right
                        # run 2 go forward 204 cm and turn right
                        # run 3 go forward 72 cm and turn right
        # get new sensor value and add to range to calculate average
        distanceFront = tof1.get_distance()
        distanceSide =  tof2.get_distance()  # get distance from VL53

        print("Front distance", int(frontturndistance), int(distanceFront), int(lastDistanceFront))
        if distanceFront >= 2000: # if distance reading over 2 metres then discard as greater than distance between walls
            print("Faulty front distance reading", distanceFront)      
            distanceFront = lastDistanceFront

        pz.setMotor(leftwheel, speedLeft)
        pz.setMotor(rightwheel, speedRight)  # set speed back to default. will be overwritten if need for turn     

        if (distanceFront <= frontturndistance): # about to hit corner so turn right
            pz.spinRight(speed)
#            pz.setMotor(leftwheel, speedLeft)
#            pz.setMotor(rightwheel, speedRight - cornerSpeed)
            print("Corner ... spin right", distanceFront)
            time.sleep(interval)
            distanceFront = tof1.get_distance() 
            
            while (distanceFront <= stopTurningDistance):   # keep turning until longer reading from side wall
                time.sleep(interval)
                distanceFront = tof1.get_distance() 
                print("Corner turning ...", distanceFront)

            # now check side wall until //
            distanceSide = tof1.get_distance() 
            lastDistanceSide = distanceSide
            while (distanceSide <= lastDistanceSide):   # keep turning until parallel reading from side wall
                time.sleep(interval)
                lastDistanceSide = distanceSide
                distanceSide = tof1.get_distance() # get distance from VL53
                print("Corner turning still ...", distanceSide, lastDistanceSide)

            pz.setMotor(leftwheel, speedLeft)
            pz.setMotor(rightwheel, speedRight)
            onRun += 1 # finished that run so on to next

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

    while onRun <= 20:   # run 4 go forward 72 cm and turn left
        # get new sensor value and add to range to calculate average
        print("New Run ..................................")
        time.sleep(interval)
        distanceFront = tof1.get_distance()
        distanceSide =  tof2.get_distance()  # get distance from VL53

        print("Front distance", int(frontturndistance), int(distanceFront), int(lastDistanceFront))
        if distanceFront >= 2000: # if distance reading over 2 meters then discard as greater than distance between walls
            print("Faulty front distance reading", distanceFront)      
            distanceFront = lastDistanceFront
        
        if distanceSide >= 360: # if distance reading over 36 cm then change 
            turnleft = 490
            turnright = 440
            hardturnleft = 560
            hardturnright = 400
            print("Change side distance", distanceSide)
        else: # back to original settings
            turnleft = 180
            turnright = 150
            hardturnleft = 250
            hardturnright = 80
            print("Original side distance", distanceSide)
        
        print("Side distance", int(turnleft), int(distanceSide))
        pz.setMotor(leftwheel, speedLeft)
        pz.setMotor(rightwheel, speedRight)
        
        if (distanceFront <= frontturndistance): # about to hit corner so turn Left
            pz.spinLeft(speed)
            print("Corner ... spin Left", distanceFront)
            time.sleep(interval)
            lastDistanceFront = distanceFront
            distanceFront = tof1.get_distance() 
            
            while (distanceFront <= 200):   # keep turning until bad reading from side wall
                time.sleep(interval)
                distanceFront = tof1.get_distance() 
                print("Corner turning ...", distanceFront)
            distanceSide = tof1.get_distance() 

            lastDistanceSide = distanceSide
            while (distanceSide <= lastDistanceSide):   # keep turning until good reading from side wall
                time.sleep(interval)
                lastDistanceSide = distanceSide
                distanceSide = tof1.get_distance() # get distance from VL53
                print("Corner turning still ...", distanceSide, lastDistanceSide)
            pz.setMotor(leftwheel, speedLeft)
            pz.setMotor(rightwheel, speedRight)
            onRun += 1 # finished that run so on to next

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
           
        lastDistanceSide = distanceSide     # set distance for checking movement to/from wall

        
except KeyboardInterrupt:
    print ("KeyBoard Interript")

finally:
    pz.cleanup()
    tof1.stop_ranging()
    GPIO.output(sensor1_shutdown, GPIO.LOW)
    tof2.stop_ranging()
    GPIO.output(sensor2_shutdown, GPIO.LOW)
