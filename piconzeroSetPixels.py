#! /usr/bin/env python

# GNU GPL V3
# Test code for 4tronix Picon Zero

import piconzero as pz, time
import random 

lastPix = 0
numpixels = 8
brightness = 50

# define rgb values for colours
black = [0, 0, 0]
white = [255, 255, 255]
blue = [0,0,255]
red = [255, 0, 0]
lime = [0, 255, 0]
yellow = [255, 255, 0]
cyan = [0, 255, 255]
magenta = [255, 0, 255]
silver = [192, 192, 192]
gray = [128, 128, 128]
maroon = [128, 0, 0]
olive = [128, 128, 0]
green = [0, 128, 0]
purple = [128, 0, 128]
teal = [0, 128, 128]
navy = [0, 0, 128]
orangered = [255, 69, 0]
gold = [255, 215, 0]

colourList = [black,white,blue,red,lime,yellow,cyan,magenta,silver,gray,maroon,olive, green, purple,teal,navy,orangered,gold]
numofcolours = 20

pz.init()                   # initialise piconzero board
pz.setInputConfig(0, 1)     # set input 0 to Analog
pz.setOutputConfig(5, 3)    # set output 5 to WS2812 to control neopixels
rev = pz.getRevision()
pz.setBrightness(brightness)
print(rev[0], rev[1])

def setColourSolid(colour, boardNum):
    # boardNum is 0, 1 or 2
    startPixel = boardNum * 8
    numPixel = startPixel
#    print("solid", colour, boardNum, startPixel, numPixel)
    while (numPixel < (startPixel + 8)):
#        print(numPixel, colour)
        pz.setPixel(numPixel, colour[0], colour[1], colour[2], False)
        numPixel += 1
    pz.updatePixels()

def setColourFlash(colour1, colour2, boardNum, cycles, timeGap):
    # boardNum is 0, 1 or 2
    while cycles > 0:
        cycles -= 1
        setColourSolid(colour1, boardNum)
        time.sleep(timeGap)
        setColourSolid(colour2, boardNum)
        time.sleep(timeGap)

def setColourFlashHalf(colour1, colour2, boardNum, cycles, timeGap):
    # boardNum is 0, 1 or 2
    startPixel = boardNum * 8
    while cycles > 0:
        cycles -= 1
        numPixel = startPixel
#       print("solid", colour, boardNum, startPixel, numPixel)
        while (numPixel < (startPixel + 4)):
#            print(numPixel, colour)
            pz.setPixel(numPixel, colour1[0], colour1[1], colour1[2], False)
            pz.setPixel(numPixel+4, colour2[0], colour2[1], colour2[2], False)
            numPixel += 1
            pz.updatePixels()
        time.sleep(timeGap)

        # now swop colours
        startPixel = boardNum * 8
        numPixel = startPixel
#        print("solid", colour, boardNum, startPixel, numPixel)
        while (numPixel < (startPixel + 4)):
#            print(numPixel, colour)
            pz.setPixel(numPixel, colour2[0], colour2[1], colour2[2], False)
            pz.setPixel(numPixel+4, colour1[0], colour1[1], colour1[2], False)
            numPixel += 1
        pz.updatePixels()
        time.sleep(timeGap)

def setColourRunSolid(colour1, colour2, boardNum, cycles, timeGap):
    # boardNum is 0, 1 or 2
    while cycles > 0:
        cycles -= 1
        startPixel = boardNum * 8
        setColourSolid(colour2, boardNum)
        numPixel = startPixel
        while (numPixel < (startPixel + 8)):
            pz.setPixel(numPixel, colour1[0], colour1[1], colour1[2], True)
            numPixel += 1
            time.sleep(timeGap)

def setColourRunSolidReverse(colour1, colour2, boardNum, cycles, timeGap):
    # boardNum is 0, 1 or 2
    while cycles > 0:
        cycles -= 1
        startPixel = boardNum * 8 + 7
        setColourSolid(colour2, boardNum)
        numPixel = startPixel
        while (numPixel >= (startPixel - 7)):
            pz.setPixel(numPixel, colour1[0], colour1[1], colour1[2], True)
            numPixel -= 1
            time.sleep(timeGap)

def setColourRunReverse(colour1, colour2, boardNum, cycles, timeGap):
    # boardNum is 0, 1 or 2
    while cycles > 0:
        cycles -= 1
        startPixel = boardNum * 8 + 7
        setColourSolid(colour2, boardNum)
        numPixel = startPixel
        pz.setPixel(numPixel, colour1[0], colour1[1], colour1[2], True)
        print(numPixel, colour1)
        time.sleep(timeGap)
        while (numPixel > (startPixel - 7)):
            numPixel -= 1
            pz.setPixel(numPixel+1, colour2[0], colour2[1], colour2[2], True)
            pz.setPixel(numPixel, colour1[0], colour1[1], colour1[2], True)
            print(numPixel, colour1)
            time.sleep(timeGap)
        pz.setPixel(numPixel, colour2[0], colour2[1], colour2[2], True)

def setColourRun(colour1, colour2, boardNum, cycles, timeGap):
    # boardNum is 0, 1 or 2
    while cycles > 0:
        cycles -= 1
        startPixel = boardNum * 8
        setColourSolid(colour2, boardNum)
        numPixel = startPixel
        pz.setPixel(numPixel, colour1[0], colour1[1], colour1[2], True)
        print(numPixel, colour1)
        time.sleep(timeGap)
        while (numPixel > (startPixel+ 7)):
            numPixel += 1
            pz.setPixel(numPixel-1, colour2[0], colour2[1], colour2[2], True)
            pz.setPixel(numPixel, colour1[0], colour1[1], colour1[2], True)
            print(numPixel, colour1)
            time.sleep(timeGap)
        pz.setPixel(numPixel, colour2[0], colour2[1], colour2[2], True)

i = 0
try:
    while True:
#        print(i)
#        setColourSolid(colourList[i], 0)
#        setColourSolid(colourList[i+1], 1)
#        setColourSolid(colourList[i+2], 2)
#        if i < 18:
#            i += 1
#        else:
#            i = 0
#        time.sleep(2)
        setColourSolid(green, 0)
        setColourSolid(green, 1)
        setColourSolid(green, 2)
#        setColourFlash(yellow, red, 0, 3, 0.2)
#        setColourFlash(blue, gold, 1, 3, 0.3)
#        setColourFlash(red, green, 2, 5, 0.1)
#        time.sleep(1)
#        setColourFlashHalf(red, green, 0, 3, 0.5)
        setColourRunSolid(blue, red, 0, 1, 0.1)
        time.sleep(1)
        setColourRunSolid(blue, gold, 1, 1, 0.1)
        time.sleep(1)
        setColourRunSolid(blue, green, 2, 1, 0.1)
        time.sleep(1)
        setColourSolid(green, 0)
        setColourSolid(green, 1)
        setColourSolid(green, 2)
        setColourRun(blue, red, 0, 1, 0.1)
        setColourRun(blue, white, 1, 1, 0.1)
        setColourRun(blue, green, 2, 1, 0.1)
        time.sleep(1)
        setColourRunReverse(black, gold, 2, 1, 0.1)
        setColourRunReverse(black, green, 1, 1, 0.1)
        setColourRunReverse(black, green, 0, 1, 0.1)
        time.sleep(1)
        setColourRunSolid(black, red, 0, 3, 0.1)
        setColourRunSolid(blue, gold, 1, 3, 0.07)
        setColourRunSolid(red, green, 2, 3, 0.05)
        time.sleep(1)
        setColourRunSolidReverse(yellow, red, 0, 1, 0.5)
        time.sleep(1)
        setColourRunSolidReverse(blue, gold, 1, 1, 0.5)
        time.sleep(1)
        setColourRunSolidReverse(red, green, 2, 1, 0.5)
        time.sleep(1)
        
except KeyboardInterrupt:
    print
finally:
    time.sleep(2)
    pz.cleanup()

