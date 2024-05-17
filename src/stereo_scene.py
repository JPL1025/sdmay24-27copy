import cv2
import numpy as np
import math

class StereoScene:

    def __init__(self, depth_map, color_map, ver_cells, hor_cells):
        """
        :param depth_map: (2D array) full depth matrix
        :param color_map: (2D array) full color matrix
        :param ver_cells: (int) vertical cells
        :param hor_cells: (int) horizontal cells
        """
        if np.shape(depth_map) < (1, 1):
            raise ValueError("Depth map must be a 2D array")

        self.ver_cells = ver_cells
        self.hor_cells = hor_cells

        self.depth_map = depth_map
        self.color_map = color_map

        self.dm_cells = None
        self.cm_cells = None
        self.points = None

    """ ===============================================================================
    StereoScene Modifiers - modifies the object
    =============================================================================== """

    def scene_reduce(self):
        """
        Reduce depth map shape radially until evenly divisible by cells.
        :param ver_cells: (int) cells vertically
        :param hor_cells: (int) cells horizontally
        :return: None
        """
        height, width = self.dm_get_shape()
        if self.ver_cells <= 0 or self.hor_cells <= 0 or (height, width) < (self.ver_cells, self.hor_cells):
            raise ValueError("Cells count must be greater than 0, and less than shape")

        lower = lambda l, f: math.ceil((l % f) / 2)  # calculates lower bound (length, factor)
        upper = lambda l, f: math.floor((l % f) / 2) * -1  # calculates upper bound (length, factor)
        check = lambda l, b: l if b == 0 else b  # catches upper bound if 0 (length, bound)
        # recduce depth map
        depth_map_out = []
        for row in self.depth_map[lower(height, self.ver_cells): check(height, upper(height, self.ver_cells))]:
            depth_map_out.append(row[lower(width, self.hor_cells): check(width, upper(width, self.hor_cells))])
        self.depth_map = np.array(depth_map_out)
        # reduce color map
        color_map_out = []
        for row in self.color_map[lower(height, self.ver_cells): check(height, upper(height, self.ver_cells))]:
            color_map_out.append(row[lower(width, self.hor_cells): check(width, upper(width, self.hor_cells))])
        self.color_map = np.array(color_map_out)

    def scene_compress(self, shape):
        """
        Compress depth map to shape by averaging point clumps.
        :param shape: ((int, int)) HEIGHT, WIDTH
        :return: None
        """
        self.depth_map = cv2.resize(self.depth_map, (shape[1], shape[0]), interpolation=cv2.INTER_NEAREST)

    """ =============================================================================== 
    StereoScene Returns - returns an object
    =============================================================================== """

    def dm_get_shape(self):
        """
        :return: ((int, int)) depth map dimensions as tuple - HEIGHT, WIDTH
        """
        return np.shape(self.depth_map)

    def get_cells(self):
        """
        Divides depth map into grid cells. Depth map shape must be divide cells evenly.
        :param ver_cells: (int) cells vertically
        :param hor_cells: (int) cells horizontally
        """
        height, width = self.dm_get_shape()
        if height % self.ver_cells != 0 or width % self.hor_cells != 0:
            raise ValueError("Shape must divide evenly by cells")

        cell_height = height // self.ver_cells
        cell_width = width // self.hor_cells

        # create depth map cells
        arr = np.array(self.depth_map)
        self.dm_cells = (arr.reshape(height // cell_height, cell_height, -1, cell_width)
                 .swapaxes(1, 2)
                 .reshape(-1, cell_height, cell_width))

        # remove depth shadows
        bound_cells = []
        for cell in self.dm_cells:
            threshold = 200 # .2 meters
            cell[cell < threshold] = np.average(cell)
            bound_cells.append(cell)
        self.dm_cells = bound_cells

        # create color map cells
        arr = np.array(self.color_map)
        self.cm_cells = (arr.reshape(height // cell_height, cell_height, -1, cell_width, 3)
                 .swapaxes(1, 2)
                 .reshape(-1, cell_height, cell_width, 3))

    def get_points(self):
        """
        Finds closest prominent depth point in a cell
        """
        self.points = []
        for cell in self.dm_cells:
            cell = np.array(cell).flatten()
            cell.sort()
            self.points.append(round(np.mean(cell[:round(len(cell) * 0.05)])))

    def template_match(self, prominence, threshold, step):
        """
        Creates a template matrix from one depth value of shape determined by the percentage of depth map inputted.
        Compares multiple template matrix's from max depth value to min depth value until match return value is
        below threshold when compared to depth matrix. If no match is below threshold, returns -1.
        The closer the match value is to zero, the more similarities there are between a template and depth map match.
        :param prominence: (float 0-1)percent of the depth map to create depth template
        :param threshold: (int >= 0) match threshold between depth template and depth map
        :param step: (int > 0) step size between max depth and min depth
        :return: a single depth point from depth map based on prominent mask algorithm,
                 template cords for visualization
        """
        height, width = self.dm_get_shape()
        template_shape = (math.ceil(height * prominence), math.ceil(width * prominence))

        for depth in range(self.dm_get_max(), self.dm_get_min(), -step):
            template = np.full(template_shape, depth)
            res = cv2.matchTemplate(self.depth_map.astype(np.float32), template.astype(np.float32), cv2.TM_SQDIFF)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if min_val <= threshold:
                return (depth, min_loc)
        return (-1, (0,0))

    """ ===============================================================================
    StereoScene Visualizers - visualizes StereoScene
    =============================================================================== """

    def visualize(self):
        # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(self.depth_map, alpha=0.03), cv2.COLORMAP_JET)

        # recolor depth points on color map
        for index in range(self.ver_cells * self.hor_cells):
            for ir, row in enumerate(self.dm_cells[index]):
                for ic, col in enumerate(row):
                    if col <= self.points[index]:
                        self.cm_cells[index][ir][ic] = [127, 0, 255] # b,g,r

        # build first horizontal strip
        recons_colormap = self.cm_cells[0]
        for index in range(1, self.hor_cells):
            recons_colormap = np.hstack((recons_colormap, self.cm_cells[index]))
        # add continual horizontal strips
        for start_cell in range(self.hor_cells, len(self.cm_cells), self.hor_cells):
            tmp = self.cm_cells[start_cell]
            for index in range(1, self.hor_cells):
                tmp = np.hstack((tmp, self.cm_cells[start_cell + index]))
            recons_colormap = np.vstack((recons_colormap, tmp))

        # Draw grid
        dim = (round(recons_colormap.shape[1]), recons_colormap.shape[0])
        cell_dim = (round(dim[0] / self.hor_cells), round(dim[1] / self.ver_cells))
        for x in range(self.hor_cells):
            for y in range(self.ver_cells):
                loc = (x * cell_dim[0], y * cell_dim[1])
                cv2.rectangle(recons_colormap, loc, (loc[0] + cell_dim[0], loc[1] + cell_dim[1]), (220,220,220), thickness=1)
                cv2.rectangle(depth_colormap, loc, (loc[0] + cell_dim[0], loc[1] + cell_dim[1]), (220,220,220), thickness=1)

        # Show maps
        cv2.namedWindow("Visual", cv2.WINDOW_AUTOSIZE)
        cv2.imshow("Visual", np.hstack((recons_colormap, depth_colormap)))
        cv2.waitKey(1)

    def print_ascii_map(self):
        remapped_points = []
        for point in self.points:
            if point >= 9999:
                remapped_points.append(" ")
            elif point > 8000:
                remapped_points.append("'")
            elif point > 6000:
                remapped_points.append("*")
            elif point > 4000:
                remapped_points.append(":")
            elif point > 2000:
                remapped_points.append("|")
            elif point > 0:
                remapped_points.append("X")
            else:
                remapped_points.append("?")
        print(np.array(remapped_points).reshape(self.ver_cells, self.hor_cells))
    
    def print_int_map(self):
        remapped_points = [point for point in self.points]
        print(np.array(remapped_points).reshape(self.ver_cells, self.hor_cells))

    def print_meter_map(self):
        remapped_points = ['{:.1f}'.format(round(point/1000, 1)) for point in self.points]
        print(np.array(remapped_points).reshape(self.ver_cells, self.hor_cells))

    def powermap(self, val):
        if val < 200:
            return 65000
        if val < 400:
            return 55000
        if val < 600:
            return 45000
        if val < 800:
            return 35000
        if val < 1000:
            return 25000
        return 0