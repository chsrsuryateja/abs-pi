import RPi.GPIO as GPIO

def relay_on(pin):
    GPIO.output(pin,GPIO.LOW)

def relay_off(pin):
    GPIO.output(pin,GPIO.HIGH)
