import board
import busio
import adafruit_pca9685

from adafruit_pca9685 import PCA9685

def main():
    # Initialize the PCA9685 using the default address (0x40)
    i2c = busio.I2C(board.SCL, board.SDA)
    hat = adafruit_pca9685.PCA9685(i2c)
    pwm = PCA9685(i2c)
    pwm.frequency = 100  # in Hertz

    for index in range(100):
        try:
            pwm.channels[index].duty_cycle = 0
        except:
            continue

if __name__ == "__main__":
    main()