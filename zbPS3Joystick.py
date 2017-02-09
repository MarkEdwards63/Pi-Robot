#!/usr/bin/env python
# coding: Latin-1

# Load library functions we want
import time
import os
import sys
import pygame
import ZeroBorg

# Re-direct our output to standard error, we need to ignore standard out to hide some nasty print statements from pygame
sys.stdout = sys.stderr

# Settings for the joystick
slowFactor = 0.5                        # Speed to slow to when the drive slowly button is held, e.g. 0.5 would be half speed
interval = 0.05                         # Time between updates in seconds, smaller responds faster but uses more processor time

# Setup pygame and wait for the joystick to become available
os.environ["SDL_VIDEODRIVER"] = "dummy" # Removes the need to have a GUI window
pygame.init()

pygame.display.set_mode((1,1))

# Setup the ZeroBorg
ZB = ZeroBorg.ZeroBorg()
#ZB.i2cAddress = 0x40                  # Uncomment and change the value if you have changed the board address
ZB.Init()
if not ZB.foundChip:
    boards = ZeroBorg.ScanForZeroBorg()
    if len(boards) == 0:
        print 'No ZeroBorg found, check you are attached :)'
    else:
        print 'No ZeroBorg at address %02X, but we did find boards:' % (ZB.i2cAddress)
        for board in boards:
            print '    %02X (%d)' % (board, board)
        print 'If you need to change the I²C address change the setup line so it is correct, e.g.'
        print 'ZB.i2cAddress = 0x%02X' % (boards[0])
    sys.exit()
#ZB.SetEpoIgnore(True)                 # Uncomment to disable EPO latch, needed if you do not have a switch / jumper
ZB.SetCommsFailsafe(False)
ZB.ResetEpo()

# Power settings
voltageIn = 8.4                         # Total battery voltage to the ZeroBorg (change to 9V if using a non-rechargeable battery)
voltageOut = 6.0                        # Maximum motor voltage

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

# Remote control commands
def Move(left, right):
    print '%0.2f | %0.2f' % (left, right)
    ZB.SetMotor1(-left * maxPower)
    ZB.SetMotor3(-left * maxPower)
    ZB.SetMotor2(right * maxPower)
    ZB.SetMotor4(right * maxPower)  

def MoveForward():
    Move(+1.0, +1.0)

def MoveBackward():
    Move(-1.0, -1.0)

def SpinLeft():
    Move(1.0, -1.0)

def SpinRight():
    Move(-1.0, 1.0)

def Stop():
    Move(0.0, 0.0)

def Shutdown():
    global running
    running = False

def forwards(speed):
    ZB.SetMotor1(speed)
    ZB.SetMotor2(speed)
    ZB.SetMotor3(speed)
    ZB.SetMotor4(speed)

def left(speed):
    ZB.SetMotor1(-speed)
    ZB.SetMotor2(speed)
    ZB.SetMotor3(-speed)
    ZB.SetMotor4(speed)

def right(speed):
    ZB.SetMotor1(speed)
    ZB.SetMotor2(-speed)
    ZB.SetMotor3(speed)
    ZB.SetMotor4(-speed)

def backwards(speed):
    ZB.SetMotor1(-speed)
    ZB.SetMotor2(-speed)
    ZB.SetMotor3(-speed)
    ZB.SetMotor4(-speed)

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

joystickName=joystick.get_name()
redJoystick = "Generic X-Box pad"
blueJoystick = "Performance Designed Products Wireless Controller for PS3"

print(joystickName)
if joystickName == redJoystick:     # buttons are different on different controllers!
    print("red")
    # Settings for the joystick 
    axisUpDown = 1                          # Joystick axis to read for up / down position
    axisUpDownInverted = False              # Set this to True if up and down appear to be swapped
    axisLeftRight = 3                       # Joystick axis to read for left / right position
    axisLeftRightInverted = False           # Set this to True if left and right appear to be swapped
    buttonResetEpo = 7                      # Joystick button number to perform an EPO reset (Start)
    buttonSlow = 4                          # Joystick button number for driving slowly whilst held (L2)
    buttonFastTurn = 5                      # Joystick button number for turning fast (R2)
    upButton = 0                            # Buttons for up/down/spin left/right
    downButton = 3
    leftButton = 2
    rightButton = 1
elif joystickName == blueJoystick:
    print("blue")
    # Settings for the joystick 
    axisUpDown = 1                          # Joystick axis to read for up / down position
    axisUpDownInverted = True               # Set this to True if up and down appear to be swapped
    axisLeftRight = 2                       # Joystick axis to read for left / right position
    axisLeftRightInverted = False           # Set this to True if left and right appear to be swapped
    buttonResetEpo = 9                      # Joystick button number to perform an EPO reset (Start)
    buttonSlow = 6                          # Joystick button number for driving slowly whilst held (L2)
    buttonFastTurn = 7                      # Joystick button number for turning fast (R2)
    upButton = 3                            # Buttons for up/down/spin left/right
    downButton = 1
    leftButton = 0
    rightButton = 2
else:
    print("Unknown Joystick")
    sys.exit()

# Hold the LED on for a couple of seconds to indicate we are ready
ZB.SetLedIr(False)
ZB.SetLed(True)
time.sleep(2.0)
ZB.SetLed(False)

try:
    print ('Press CTRL+C to quit')
    driveLeft = 0.0
    driveRight = 0.0
    running = True
    hadEvent = False
    upDown = 0.0
    leftRight = 0.0
    ZB.SetLedIr(True)

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
                    
                if joystick.get_button(upButton):
                    driveLeft = 1
                    driveRight = 1
                    print("Up")
                elif joystick.get_button(downButton):
                    driveLeft = -1
                    driveRight = -1
                    print("Down")
                elif joystick.get_button(leftButton):
                    driveLeft = -1
                    driveRight = 1
                    print("Left")
                elif joystick.get_button(rightButton):
                    driveLeft = 1
                    driveRight = -1
                    print("RIght")
                # Set the motors to the new speeds
                ZB.SetMotor1(int(driveRight * 100))
                ZB.SetMotor2(int(driveLeft * 100))
                ZB.SetMotor3(int(driveRight * 100))
                ZB.SetMotor4(int(driveLeft * 100))
                print(driveLeft, driveRight)
        # Change the LED to reflect the status of the EPO latch
        #PBR.SetLed(PBR.GetEpo())
        # Wait for the interval period
        time.sleep(interval)
    # Disable all drives
    Stop()
except KeyboardInterrupt:
    Stop()
    # CTRL+C exit, disable all driveStop()
print ('Motors off')
ZB.MotorsOff()


