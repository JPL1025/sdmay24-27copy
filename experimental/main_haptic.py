from stereo_scene import StereoScene

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
    return pipeline


def capture(pipeline):
    # Wait for a coherent pair of frames: depth and color
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()

    # Convert images to numpy arrays
    depth_map = np.asanyarray(depth_frame.get_data())

    # Removing Shadows
    threshold = 200
    depth_map[depth_map< threshold] = 7000

    color_map = np.asanyarray(color_frame.get_data())

    return depth_map, color_map


def process(depth_map, color_map):
    depth_map = np.fliplr(depth_map)  # flip on y axis
    scene = StereoScene(depth_map, color_map)

    # create cells
    scene.scene_reduce(VER_CELLS, HOR_CELLS)
    cells = scene.dm_get_cells(VER_CELLS, HOR_CELLS)

    # create point array
    # points = [cell.dm_get_point(prominence=0.1, threshold=3000, step=30) for cell in cells]
    points = [cell.dm_get_point_fixed() for cell in cells]

    return scene, points


def haptics(points):
    i2c = busio.I2C(board.SCL, board.SDA)
    hat = adafruit_pca9685.PCA9685(i2c)

    # Initialize the PCA9685 using the default address (0x40).
    pwm = PCA9685(i2c)

    # Set the PWM frequency.
    pwm.frequency = 100  # in Hertz

    if points == None:
        pwm.channels[0].duty_cycle = 0
        pwm.channels[1].duty_cycle = 0
        pwm.channels[2].duty_cycle = 0
        pwm.channels[3].duty_cycle = 0
        return None

    power0 = points[0][0] * 100
    #if power0 > 55000:
    #    power0 = 55000
    power0 = abs(power0 - 55000) * 2

    power1 = points[1][0] * 100
    #if power1 > 55000:
    #    power1 = 55000
    power1 = abs(power1 - 55000) * 2

    power2 = points[2][0] * 100
    #if power2 > 55000:
    #    power2 = 55000
    power2 = abs(power2 - 55000) * 2

    power3 = points[3][0] * 100
    #if power3 > 55000:
    #    power3 = 55000
    power3 = abs(power3 - 55000) * 2

    print(power0)
    print(power1)
    print(power2)
    print(power3)

#    try:
#        pwm.channels[0].duty_cycle = power0
#        pwm.channels[1].duty_cycle = power1
#        pwm.channels[2].duty_cycle = power2
#        pwm.channels[3].duty_cycle = power3
#    except KeyboardInterrupt:
#         Clean up PCA9685 on Ctrl+C exit
#        pwm.deinit()


def visualize(show_window, scene, points):
    if show_window:
        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(scene.get_dm_root(), alpha=0.03), cv2.COLORMAP_JET)

        depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = scene.get_cm().shape

        # If depth and color resolutions are different, resize color image to match depth image for display
        if depth_colormap_dim != color_colormap_dim:
            resized_color_image = cv2.resize(
                scene.get_cm(),
                dsize=(depth_colormap_dim[1], depth_colormap_dim[0]),
                interpolation=cv2.INTER_AREA,
            )
            images = np.hstack((resized_color_image, depth_colormap))
        else:
            images = np.hstack((scene.get_cm(), depth_colormap))

        # Draw grid and template locations
        dim = (round(images.shape[1] / 2), images.shape[0])
        cell_dim = (round(dim[0] / HOR_CELLS), round(dim[1] / VER_CELLS))
        for x in range(HOR_CELLS):
            for y in range(VER_CELLS):
                loc = (x * cell_dim[0], y * cell_dim[1])
                # Grid
                cv2.rectangle(images, loc, (loc[0] + cell_dim[0], loc[1] + cell_dim[1]), (220,220,220), thickness=1)
                # Template
                t_cords = points[x + y][1]
                # cv2.rectangle(images, (loc[0] + t_cords[1], loc[1] + t_cords[0]), (loc[0] + t_cords[1] + round(cell_dim[0]*0.1), loc[1] + t_cords[0] + round(cell_dim[1]*0.1)), (0,0,255), thickness=2)

        # Show images
        cv2.namedWindow("RealSense", cv2.WINDOW_AUTOSIZE)
        cv2.imshow("RealSense", images)
        cv2.waitKey(1)

    # terminal output
    STATS[0] = round(1 / (time.time() - START_TIME), 1)
    STATS[1] += STATS[0]
    STATS[2] += 1

    os.system("clear")
    print(np.array(scene.divide_map(points)).reshape(VER_CELLS, HOR_CELLS))
    print("------ %3.1f fps ----- %3.1f average fps ------" % (STATS[0], STATS[1] / STATS[2]))
    #print("--- %5d local min --- %5d local max ---" % (min(points)[0], max(points)[0]))

    return STATS


if __name__ == "__main__":
    VER_CELLS = 1
    HOR_CELLS = 4
    
    # current fps, total fps, total frames
    STATS = [0, 0, 0]

    pipeline = config()
    try:
        while True:
            START_TIME = time.time()
            depth_map, color_map = capture(pipeline)
            scene, points = process(depth_map, color_map)
            haptics(points)
            visualize(True, scene, points)
    except KeyboardInterrupt:
        pipeline.stop()
        haptics(None)
