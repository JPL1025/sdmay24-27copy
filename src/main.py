from stereo_scene import StereoScene

import sys
sys.path.insert(1, '/home/sdmay24-27/librealsense/release')
import pyrealsense2 as rs

import numpy as np
import cv2

import time
import math
import os

import board
import busio
import adafruit_pca9685

from adafruit_pca9685 import PCA9685


def config():
    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()

    # Get device product line for setting a supporting resolution
    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()
    device_product_line = str(device.get_info(rs.camera_info.product_line))

    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

    if device_product_line == "L500":
        config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
    else:
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start streaming
    pipeline.start(config)

    # Initialize the PCA9685 using the default address (0x40)
    i2c = busio.I2C(board.SCL, board.SDA)
    hat = adafruit_pca9685.PCA9685(i2c)
    pwm = PCA9685(i2c)
    pwm.frequency = 100  # in Hertz
 
    return pipeline, pwm


def capture(pipeline):
    # Wait for a coherent pair of frames: depth and color
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()

    # Convert images to numpy arrays
    depth_map = np.asanyarray(depth_frame.get_data())
    color_map = np.asanyarray(color_frame.get_data())

    # Set depth upperbound
    threshold = 9999 # ~10 meters
    depth_map[depth_map > threshold] = threshold

    #depth_map = np.fliplr(depth_map)  # flip on y axis
    scene = StereoScene(depth_map, color_map, VER_CELLS, HOR_CELLS) # create scene

    # process points
    scene.scene_reduce()
    scene.get_cells()
    scene.get_points()

    return scene


def haptic(scene, pwm):
    for index in range(VER_CELLS * HOR_CELLS):
        try:
            pwm.channels[index].duty_cycle = scene.powermap(scene.points[index])
        except:
            continue


def stattrack(visualize, scene):
    if visualize:
        scene.visualize()

    try:
        STATS[0] = round(1 / (time.time() - START_TIME), 1)
    except:
        STATS[0] = 60
    STATS[1] += STATS[0]
    STATS[2] += 1

    os.system("clear")
    scene.print_meter_map()
    print("------ %3.1f fps ----- %3.1f average fps ------" % (STATS[0], STATS[1] / STATS[2]))


def cleanup(pipeline, pwm):
    pipeline.stop()
    
    # stop motors
    for index in range(VER_CELLS * HOR_CELLS):
        try:
            pwm.channels[index].duty_cycle = 0
        except:
            continue
    pwm.deinit()


if __name__ == "__main__":
    VER_CELLS = 3
    HOR_CELLS = 5
    
    # current fps, total fps, total frames
    STATS = [0, 0, 0]

    pipeline, pwm = config()
    try:
        while True:
            START_TIME = time.time()
            scene = capture(pipeline)
            haptic(scene, pwm)
            stattrack(False, scene)
    except KeyboardInterrupt:
        cleanup(pipeline, pwm)