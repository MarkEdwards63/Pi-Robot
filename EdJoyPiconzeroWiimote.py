5#!/usr/bin/env python
# coding: Latin-1

# Load library functions we want
import time
import os
import sys
import cwiid
# import EdBot
import piconzero as pz # ME 18-06-16 Added to use piconzero libary for motor

# Set variables for the GPIO motor pins
pinMotorAForwards = 10
pinMotorABackwards = 9
pinMotorBForwards = 8
pinMotorBBackwards = 7

# LeftMotor = EdBot.motor.one
# RightMotor = EdBot.motor.two


# Re-direct our output to standard error, we need to ignore standard out to hide some nasty print statements from pygame
sys.stdout = sys.stderr

# Settings for the joystick
axisUpDown = 3                          # Joystick axis to read for up / down position
axisUpDownInverted = True               # Set this to True if up and down appear to be swapped
axisLeftRight = 0                       # Joystick axis to read for left / right position
axisLeftRightInverted = False           # Set this to True if left and right appear to be swapped
buttonResetEpo = 9                      # Joystick button number to perform an EPO reset (Start)
buttonSlow = 6                          # Joystick button number for driving slowly whilst held (L2)
slowFactor = 0.5                        # Speed to slow to when the drive slowly button is held, e.g. 0.5 would be half speed
buttonFastTurn = 7                      # Joystick button number for turning fast (R2)
interval = 0.00                         # Time between updates in seconds, smaller responds faster but uses more processor time
button_delay = 0.1

# Power settings
voltageIn = 5.0                         # Total battery voltage to the PicoBorg Reverse
voltageOut = 5.0 * 0.95 #* 0.95         # Maximum motor voltage, we limit it to 95% to allow the RPi to get uninterrupted power

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

print 'Press 1 + 2 on your Wii Remote now ...'
time.sleep(1)

# Connect to the Wii Remote. If it times out
# then quit.
try:
  wii=cwiid.Wiimote()
except RuntimeError:
  print "Error opening wiimote connection"
  quit()

print 'Wii Remote connected...\n'
print 'Press some buttons!\n'
print 'Press PLUS and MINUS together to disconnect and quit.\n'

wii.rpt_mode = cwiid.RPT_BTN

try:
    print ('Press CTRL+C to quit')
    driveLeft = 0.0
    driveRight = 0.0
    running = True
    hadEvent = False
    upDown = 0.0
    leftRight = 0.0
    pz.setMotor(0, (98))
    pz.setMotor(1, (-97))
    time.sleep(1)
    pz.stop()
    # Loop indefinitely
    while running:
        buttons = wii.state['buttons']
        hadEvent = False

        # If Plus and Minus buttons pressed
        # together then rumble and quit.
        if (buttons - cwiid.BTN_PLUS - cwiid.BTN_MINUS == 0):  
            print '\nClosing connection ...'
            wii.rumble = 1
            time.sleep(1)
            wii.rumble = 0
            exit(wii)  
  
        # Check if other buttons are pressed by
        # doing a bitwise AND of the buttons number
        # and the predefined constant for that button.
        if (buttons & cwiid.BTN_LEFT):
            print 'Left pressed'
            hadEvent = True
            driveLeft = 1
            driveRight = -1
            time.sleep(button_delay)         

        if(buttons & cwiid.BTN_RIGHT):
            print 'Right pressed'
            hadEvent = True
            driveLeft = -1
            driveRight = 1
            time.sleep(button_delay)          

        if (buttons & cwiid.BTN_UP):
            print 'Up pressed'        
            hadEvent = True
            driveLeft = 1
            driveRight = 1
            time.sleep(button_delay)          
    
        if (buttons & cwiid.BTN_DOWN):
            print 'Down pressed'
            hadEvent = True
            driveLeft = -1
            driveRight = -1
            time.sleep(button_delay)

        if (buttons & cwiid.BTN_A):
            print 'A pressed'
            hadEvent = True
            driveLeft = 0
            driveRight = 0
            time.sleep(button_delay)

        if hadEvent:
 
            # Determine the drive power levels
            driveLeft = -upDown
            driveRight = -upDown
            if leftRight < -0.05:
                # Turning left
                driveLeft *= 1.0 + (2.0 * leftRight)
            elif leftRight > 0.05:
                # Turning right
                driveRight *= 1.0 - (2.0 * leftRight)

            # Set the motors to the new speeds
            pz.setMotor(0, int(-driveRight * maxPower * 100))
            pz.setMotor(1, int(driveLeft * maxPower * 100))

        time.sleep(interval)
    # Disable all drives
    pz.stop(0)
except KeyboardInterrupt:
    # CTRL+C exit, disable all drives
    pz.stop()
print ('Motors off')
pz.cleanup()
