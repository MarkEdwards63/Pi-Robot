# Picon Zero Motor Test
# Moves: Forward, Reverse, turn Right, turn Left, Stop - then repeat
# Press Ctrl-C to stop
#
# To check wiring is correct ensure the order of movement as above is correct

import piconzero as pz, time

#======================================================================
# Reading single character by forcing stdin to raw mode
import sys
import tty
import termios

def readchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    if ch == '0x03':
        raise KeyboardInterrupt
    return ch

def readkey(getchar_fn=None):
    getchar = getchar_fn or readchar
    c1 = getchar()
    if ord(c1) != 0x1b:
        return c1
    c2 = getchar()
    if ord(c2) != 0x5b:
        return c1
    c3 = getchar()
    return chr(0x10 + ord(c3) - 65)  # 16=Up, 17=Down, 18=Right, 19=Left arrows

# End of single character reading
#======================================================================

speed = 60
leftSpeed = speed
rightSpeed = speed

print ("Tests the motors by using the arrow keys to control")
print ("Use z or x to slow down or speed up left wheel")
print ("Use < or > to slow down or speed up right wheel")
print("Use up or down arrow for forward or backwards and space to stop")
print ("Speed changes take effect when the next arrow key is pressed")
print ("Press Ctrl-C to end")
print ()

pz.init()

# main loop
try:
    while True:
        keyp = readkey()
        if ord(keyp) == 16:
            pz.setMotor(0, leftSpeed)
            pz.setMotor(1, rightSpeed)
            print ('Forward', leftSpeed, rightSpeed)
        elif ord(keyp) == 17:
            pz.setMotor(0, -leftSpeed)
            pz.setMotor(1, -rightSpeed)
            print ('Reverse', leftSpeed, rightSpeed)
        elif keyp == '>':
            rightSpeed = min(100, rightSpeed + 1)
            print ('Right plus', leftSpeed, rightSpeed)
        elif keyp == '<':
            rightSpeed = max(0, rightSpeed - 1)
            print ('Right minus', leftSpeed, rightSpeed)
        elif keyp == 'x':
            leftSpeed = min(100, leftSpeed + 1)
            print ('Left plus', leftSpeed, rightSpeed)
        elif keyp == 'z':
            leftSpeed = max(0, leftSpeed - 1)
            print ('Left minus', leftSpeed, rightSpeed)
        elif keyp == ' ':
            pz.stop()
            print ('Stop')
        elif ord(keyp) == 3:
            break

except KeyboardInterrupt:
    print ()

finally:
    pz.cleanup()
    
