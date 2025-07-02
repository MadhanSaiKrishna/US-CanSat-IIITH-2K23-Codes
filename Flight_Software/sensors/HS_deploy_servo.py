import RPi.GPIO as GPIO
from time import sleep

HS_deploy_servo_pin = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(HS_deploy_servo_pin, GPIO.OUT)

pwm=GPIO.PWM(HS_deploy_servo_pin, 50)
pwm.start(0)

def setAngle(angle):
    duty = angle / 18 + 2
    GPIO.output(HS_deploy_servo_pin, True)
    pwm.ChangeDutyCycle(duty)
    # sleep(1)
    GPIO.output(HS_deploy_servo_pin, False)
    pwm.ChangeDutyCycle(duty)

count = 0
numLoops = 2

while count < numLoops:
    setAngle(0)
    # sleep(1)
        
    setAngle(90)
    # sleep(1)

    setAngle(135)
    # sleep(1)
    
    count=count+1

def HS_deploy_servo(angle):
    setAngle(angle)
    return

pwm.stop()
GPIO.cleanup()