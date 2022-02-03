import pigpio
import RPi.GPIO as GPIO

class pwmAccess:
    def __init__(self):
        self.range = 1000000
        self.frequency = 100
        self.leftLedPin = 12
        self.rightLedPin = 13
        self.electromagnetPin = 15
        self.isMagnetOn = False
        self.pi = pigpio.pi()
        self.pi.set_mode(self.leftLedPin, pigpio.OUTPUT)
        self.pi.set_mode(self.rightLedPin, pigpio.OUTPUT)
        self.pi.set_mode(self.electromagnetPin, pigpio.OUTPUT)
        self.pi.write(self.electromagnetPin, 0)

    def setNewControlValue(self, controlValue):
        val = int(controlValue * self.range)

        if (controlValue > 0):
            self.pi.hardware_PWM(self.leftLedPin,self.frequency,val)
            self.pi.hardware_PWM(self.rightLedPin,self.frequency, 0)
        else:
            self.pi.hardware_PWM(self.leftLedPin,self.frequency, 0)
            self.pi.hardware_PWM(self.rightLedPin,self.frequency, -val)

    def toggleElectronmagnet(self):
        if self.isMagnetOn:
            self.pi.write(self.electromagnetPin, 0)
        else:
            self.pi.write(self.electromagnetPin, 1)

        self.isMagnetOn = not self.isMagnetOn
        