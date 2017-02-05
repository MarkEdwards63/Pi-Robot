#!/usr/bin/env python
# coding: Latin-1

# Load library functions we want
import time
import os
import sys
import pygame
import piconzero as pz # ME 18-06-16 Added to use piconzero libary for motor

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
interval = 0.05                         # Time between updates in seconds, smaller responds faster but uses more processor time

# Setup pygame and wait for the joystick to become available
os.environ["SDL_VIDEODRIVER"] = "dummy" # Removes the need to have a GUI window
pz.init()
pygame.init()
pygame.display.set_mode((1,1))
time.sleep(5)
pz.setMotor(0, 50)  # quick wheel spin to show ready to connect controller
time.sleep(0.2)
pz.stop()

print ('Waiting for joystick... (press CTRL+C to abort)')
while True:
    try:
        try:
            pygame.joystick.init()
            # Attempt to setup the joystick
            if pygame.joystick.get_count() < 1:
                # No joystick attached, toggle the LED
                print('No Joystick attached')
                pygame.joystick.quit()
                time.sleep(0.5)
            else:
                # We have a joystick, attempt to initialise it!
                joystick = pygame.joystick.Joystick(0)
                break
        except pygame.error:
            # Failed to connect to the joystick, toggle the LED
            print('Failled to connect to joystick')
            pygame.joystick.quit()
            time.sleep(0.5)
    except KeyboardInterrupt:
        # CTRL+C exit, give up
        print ('\nUser aborted')

        sys.exit()
print ('Joystick found')
joystick.init()


try:
    print ('Press CTRL+C to quit')
    driveLeft = 0.0
    driveRight = 0.0
    running = True
    hadEvent = False
    upDown = 0.0
    leftRight = 0.0

    # Loop indefinitely
    while running:
        # Get the latest events from the system
        hadEvent = False
        events = pygame.event.get()
        # Handle each event individually
        for event in events:
            if event.type == pygame.QUIT:
                # User exit
                running = False
            elif event.type == pygame.JOYBUTTONDOWN:
                # A button on the joystick just got pushed down
                hadEvent = True
            elif event.type == pygame.JOYAXISMOTION:
                # A joystick has been moved
                hadEvent = True
            if hadEvent:
                # Read axis positions (-1 to +1)
                if axisUpDownInverted:
                    upDown = joystick.get_axis(axisUpDown)
                else:
                    upDown = -joystick.get_axis(axisUpDown)
                if axisLeftRightInverted:
                    leftRight = -joystick.get_axis(axisLeftRight)
                else:
                    leftRight = joystick.get_axis(axisLeftRight)
                # Apply steering speeds
                if not joystick.get_button(buttonFastTurn):
                    leftRight *= 0.5
                # Determine the drive power levels
                driveLeft = -upDown
                driveRight = -upDown
                if leftRight < -0.05:
                    # Turning left
                    driveLeft *= 1.0 + (2.0 * leftRight)
                elif leftRight > 0.05:
                    # Turning right
                    driveRight *= 1.0 - (2.0 * leftRight)
                # Check for button presses
                if joystick.get_button(buttonResetEpo):
                    print('reset')
                if joystick.get_button(buttonSlow):
                    driveLeft *= slowFactor
                    driveRight *= slowFactor
                # Set the motors to the new speeds
                pz.setMotor(0, int(driveRight * 100))
                pz.setMotor(1, int(driveLeft * 100))
                print(driveLeft, driveRight)
        # Change the LED to reflect the status of the EPO latch
        #PBR.SetLed(PBR.GetEpo())
        # Wait for the interval period
        time.sleep(interval)
    # Disable all drives
    pz.stop(0)
except KeyboardInterrupt:
    # CTRL+C exit, disable all drives
    pz.stop()
print ('Motors off')
pz.cleanup()
