import time
import board
import busio
import adafruit_pca9685

from adafruit_pca9685 import PCA9685

i2c = busio.I2C(board.SCL, board.SDA)
hat = adafruit_pca9685.PCA9685(i2c)

# Initialize the PCA9685 using the default address (0x40).
pwm = PCA9685(i2c)

# Set the PWM frequency.
pwm.frequency = 100  # in Hertz

try:
    while True:
        # Change duty cycle to vary the brightness of the LEDs
        for dc in range(0, 101, 5):
            pwm.channels[0].duty_cycle = 65000
            pwm.channels[1].duty_cycle = 65000
            pwm.channels[2].duty_cycle = 65000
            pwm.channels[3].duty_cycle = 60000

            kill = input("Enter 1 to kill: ")
            if kill == "1":
                break

        # Stop the loop if kill is "1"
        if kill == "1":
            break
            
    # Turn off all channels
    pwm.channels[0].duty_cycle = 0
    pwm.channels[1].duty_cycle = 0
    pwm.channels[2].duty_cycle = 0
    pwm.channels[3].duty_cycle = 0

except KeyboardInterrupt:
    # Clean up PCA9685 on Ctrl+C exit
    pwm.deinit()
