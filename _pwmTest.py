from dataAccess.pwmAccess import pwmAccess


pwm = pwmAccess()

while True:
    command = input()

    try:
        value = float(command) 
        print(value)
        pwm.setNewControlValue(value)
    except ValueError:
        pwm.toggleElectronmagnet()
        print("Electromagnet: ", pwm.isMagnetOn)

# import pigpio
# import RPi.GPIO as GPIO

# pi = pigpio.pi()

# pi.set_mode(18, pigpio.OUTPUT)
# pi.hardware_PWM(18, 100, 1)

# while  True:
#     val = input()
#     pi.hardware_PWM(18, 100, int(val))