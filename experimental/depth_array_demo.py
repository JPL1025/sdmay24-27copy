import numpy as np
import cv2
from matplotlib import pyplot as plt
import math


def depth_array_demo(capture_name, capture_format):
    capture_left = cv2.imread(f'../assets/captures/{capture_name}L.{capture_format}', 0)
    capture_right = cv2.imread(f'../assets/captures/{capture_name}R.{capture_format}', 0)

    # initiate and StereoBM object
    stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)

    # compute the disparity map
    disparity = stereo.compute(capture_left, capture_right)
    height, width = disparity.shape

    disparity_grid = blockfy(disparity, math.ceil(height / 4), math.ceil(width / 4))
    depth_array = list(grid.mean() for grid in disparity_grid)
    min_depth = min(depth_array)
    max_depth = max(depth_array)
    percentage_depth_array = list(round((depth - min_depth) / (max_depth - min_depth) * 100) for depth in depth_array)

    print("Raw mean depth per grid")
    print(np.array(depth_array).reshape((4, 4)))
    print()
    print("Relative percentage per grid")
    print(np.array(percentage_depth_array).reshape((4, 4)))

    plt.imshow(disparity, 'gray')
    plt.show()


def blockfy(array, row_size, column_size):
    m = array.shape[0]  # image row size
    n = array.shape[1]  # image column size

    # pad array with NaNs so it can be divided by p row-wise and by q column-wise
    bpr = ((m - 1) // row_size + 1)  # blocks per row
    bpc = ((n - 1) // column_size + 1)  # blocks per column
    M = row_size * bpr
    N = column_size * bpc

    A = np.nan * np.ones([M, N])
    A[:array.shape[0], :array.shape[1]] = array

    block_list = []
    for row_block in range(bpc):
        previous_row = row_block * row_size
        for column_block in range(bpr):
            previous_column = column_block * column_size
            block = A[previous_row:previous_row + row_size, previous_column:previous_column + column_size]
            # remove nan columns and nan rows
            nan_cols = np.all(np.isnan(block), axis=0)
            block = block[:, ~nan_cols]
            nan_rows = np.all(np.isnan(block), axis=1)
            block = block[~nan_rows, :]
            # append
            if block.size:
                block_list.append(block)

    return block_list


if __name__ == '__main__':
    capture_name = 'room'
    capture_format = 'png'
    depth_array_demo(capture_name, capture_format)
