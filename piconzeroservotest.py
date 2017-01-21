import piconzero as pz,time

pz.init()
pz.setOutputConfig(0, 2)
while True:
    pz.setOutput(0, 0)
    time.sleep(1)
    pz.setOutput(0, 90)
    time.sleep(1)
    pz.setOutput(0, 180)
    time.sleep(1)
    pz.setOutput(0, 90)
    time.sleep(1)
