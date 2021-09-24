from nscopeapi import nScope
import time

ns = nScope()

ns.setSampleRateInHz(10000)
fs = ns.getSampleRateInHz()
print(fs)

def sendPulse():
    ns.setAXOn(1, True)
    ns.setAXFrequencyInHz(1, 2)
    ns.setAXAmplitude(1, 5)
    time.sleep(2)

    ns.setAXOn(1, False)

def init():
    # turn on analog input 1
    ns.setChannelsOn(True, False, False, False)
    ns.setSampleDateInHz()

def readSig():
    pass

sendPulse()
