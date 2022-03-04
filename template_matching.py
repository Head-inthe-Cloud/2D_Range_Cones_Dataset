import os
import math
import matplotlib.pyplot as plt
import numpy as np
from plot import plot_ar, plot_xy
from datasets import extract_from_csv

DATA_FILE = "data/12202021/lidar_data_3m.csv"


# [x, y] -> [angle, range]
def toar(point):
    if len(np.shape(point)) == 2:
        return [[math.tanh(p[1]/p[0]), math.sqrt(pow(p[0], 2) + pow(p[1], 2))] for p in point]
    else:
        return [math.tanh(point[1]/point[0]), math.sqrt(pow(point[0], 2) + pow(point[1], 2))]

# [angle, range] -> [x, y]
def toxy(point):
    if len(np.shape(point)) == 2:
        return [[p[1] * math.cos(p[0]), p[1] * math.sin(p[0])] for p in point]
    else:
        return [point[1] * math.cos(point[0]), point[1] * math.sin(point[0])]


def plot_points(points):
    for p in points:
        plt.scatter(p[0], p[1])
    plt.show()


def extract_center_points():
    dataset = extract_from_csv(DATA_FILE)

    # scan -- [[Angle, Range, Intensity] x N]
    # Angle vaule range: -pi ~ pi (radians)
    scan = dataset[0]
    center_points = []

    # scan -- [[Angle, Range] x N]
    scan = [point[:2] for point in scan]

    # plot_ar(scan)
    # extract points at 0 degree with a bias of 0.25 radian
    # we are only doing this step to limit the number of points for experiment
    print(np.shape(scan))
    for point in scan:
        if -0.25 < point[0] < 0.25 and point[1] != 0.0:
            center_points.append(point)

    print("Number of Center Points", len(center_points))

    # Examine Center Points
    # plot_ar(center_points)
    # plot_xy(toxy(center_points))

    return center_points


center_points = extract_center_points()

# working on one center point for now
center_point = center_points[0]
x, y = toxy(center_point)
center_point_xy = [x, y]


sample_range = 0.23 # suppose to be 3 * standard deviation, now we use cone diameter instead
sample_gap = 0.05 # how far each sample is from each other

sample_points = []

n = int(sample_range * 2 // sample_gap)

temp_x = x - sample_range
temp_y = y - sample_range
for i in range(n):
    for j in range(n):
        sample_points.append([temp_x + i * sample_gap, temp_y + j * sample_gap])

plot_xy(center_point_xy, sample_points)

'''
# change x, y to a, r
sample_points = [toar(_) for _ in sample_points]

# for each of the sample points
# Do the following

sample_point = [0.0, 3.0]
sample_a = sample_point[0]
sample_r = sample_point[1]
ConeDiam = 0.23

visual_angle = 2 * math.tan((ConeDiam/2)/sample_r) * 180/math.pi # degree, not radian

# making sure number of data equals to number of ideal data
visual_angle_range = [sample_a - visual_angle/180 * math.pi / 2, sample_a + visual_angle/180 * math.pi / 2]
visible_data = [_ for _ in scan if visual_angle_range[0] <= _[0] <= visual_angle_range[1]]

print(len(visible_data))

# TODO
# Points per degree is not integer, may need further improvement
Points_per_degree = len(scan) / 360
# print(Points_per_degree)
n_template = int(Points_per_degree * visual_angle)

print(n_template)

if n_template % 2 == 0:
    n_list = [_ for _ in range(0, n_template//2)] + [_ for _ in range(n_template//2 - 1, -1, -1)]
else:
    n_list = [_ for _ in range(0, (n_template + 1)//2)] + [_ for _ in range((n_template + 1)//2 - 2, -1, -1)]

ideal_data = []
visual_angle = visual_angle/180 * math.pi

for i, n in enumerate(n_list):
    ideal_data.append([visual_angle_range[0] + i * visual_angle/n_template, sample_r - math.sin(n * 180/n_template-1)*(ConeDiam/2)])


ideal_data = toxy(ideal_data)

plot_points(ideal_data)



# deviation with respect to range
D = []
for i in range(len(visible_data)):
    D.append(abs(visible_data[i][1] - ideal_data[i]))

print(D)
Pr_data_location = sum(D) / len(D)

print(Pr_data_location)
'''