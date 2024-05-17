import RPi.GPIO as GPIO
import time

# Set GPIO mode
GPIO.setmode(GPIO.BCM)

# Set PWM pin
pwm_pin = 13
GPIO.setup(pwm_pin, GPIO.OUT)

# Set PWM frequency
frequency = 100  # in Hertz
pwm = GPIO.PWM(pwm_pin, frequency)

# Start PWM with 50% duty cycle
duty_cycle = 50  # in percentage
pwm.start(duty_cycle)

try:
    while True:
        # Change duty cycle to vary the brightness of the LED
        for dc in range(0, 101, 5):
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.1)
        for dc in range(100, -1, -5):
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.1)

except KeyboardInterrupt:
    # Clean up GPIO on Ctrl+C exit
    pwm.stop()
    GPIO.cleanup()
