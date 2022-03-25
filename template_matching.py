import os
import math
import matplotlib.pyplot as plt
import numpy as np
from plot import plot_ar, plot_xy, plot_eval
from datasets import extract_from_csv



# Input: LocX, LocY, Sigma, Lidar data
# Output: Highest Pr(location | data)

DATA_FILE = "data/12202021/lidar_data_3m.csv"
EPSILON = 10e-6

CONE_DIAMETER = 0.23
POINTS_PER_DEGREE = 3

SIGMA =

# Pr(data) should depend on the state of the vehicle and GPS
# But for now we are using 1 as its value
PR_DATA = 1

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


def get_distance(point1, point2):
    return pow(pow(point1[0] - point2[0], 2) + pow(point1[1] - point2[1], 2), 0.5)

def get_k_nearest_points(points, center, k):
    sorted_points = sorted(points, key=lambda point: get_distance(point, center))
    return sorted_points[:k]

# returns MSE
def mean_squared_error(a, b):
    assert len(a) > 0, "Input length has to be greater than 0"
    assert len(a) == len(b), "Input arrays must have the same lengths"
    return sum([pow(diff, 2) for diff in a - b]) / len(a)


def get_pr_data_loc(data, samples):
    result = []
    data = toxy(data)
    for point in samples:
        # get k nearest points
        visual_angle = 2 * math.tan((CONE_DIAMETER / 2) / point[1]) * 180 / math.pi
        num_ideal_points = int(visual_angle * POINTS_PER_DEGREE)

        point = toxy(point)
        nearest_points = get_k_nearest_points(data, point, num_ideal_points)
        nearest_points = np.array(nearest_points)
        d_ideal_points = np.zeros(len(nearest_points))
        d_ideal_points.fill(CONE_DIAMETER / 2)
        d_nearest_points = [get_distance(p, point) for p in nearest_points]

        mse = mean_squared_error(d_ideal_points, d_nearest_points)
        result.append(mse)
    return result

def plot_points(points):
    for p in points:
        plt.scatter(p[0], p[1])
    plt.show()


def extract_data_points():
    dataset = extract_from_csv(DATA_FILE)

    # scan -- [[Angle, Range, Intensity] x N]
    # Angle vaule range: -pi ~ pi (radians)
    scan = dataset[0]

    data_points = []

    # scan -- [[Angle, Range] x N]
    scan = [point[:2] for point in scan]

    # plot_ar(scan)
    # extract points at 0 degree with a bias of 0.25 radian
    # we are only doing this step to limit the number of points for experiment
    print(np.shape(scan))
    for point in scan:
        if -0.25 < point[0] < 0.25 and point[1] != 0.0:
            data_points.append(point)

    print("Number of Center Points", len(data_points))

    # Examine Center Points
    # plot_ar(center_points)
    # plot_xy(toxy(center_points))

    return data_points


def evaluate_results(preds, labels):
    print("Evaluating results ...")
    assert len(preds) > 0, "Input length must be greater than 0"
    assert len(preds) == len(labels), "Inputs must have the same lengths"
    if labels is not np.ndarray:
        labels = np.array(labels)
    if preds is not np.ndarray:
        preds = np.array(preds)

    distance = [get_distance(preds[idx], labels[idx]) for idx in range(len(preds))]
    mse = mean_squared_error(distance, np.zeros_like(distance))
    print("MSE =", mse)


def get_prediction_from_point():
    pass

def template_matching(LocX, LocY, Sigma, lidar_data):
    pass

def main():
    data_points = extract_data_points()
    data_points_xy = toxy(data_points)

    # working on one center point for now
    predictions = []

    sample_range = CONE_DIAMETER  # suppose to be 3 * standard deviation, now we use cone diameter instead
    sample_gap = 0.05  # how far each sample is from each other

    for data_point in data_points:
        center_point_xy = toxy([data_point])

        # create sample points
        sample_points_xy = []

        n = int(sample_range * 2 // sample_gap)

        temp_x = center_point_xy[0][0] - sample_range
        temp_y = center_point_xy[0][1] - sample_range
        for i in range(n):
            for j in range(n):
                sample_points_xy.append([temp_x + i * sample_gap, temp_y + j * sample_gap])

        sample_points = toar(sample_points_xy)

        '''
        # Plot sampled points
        plot_xy(center_point_xy, sample_points_xy)
        plot_ar(center_point, sample_points)
        '''

        pr_data_loc = get_pr_data_loc(data_points, sample_points)

        # Pr(Location) should be dependent on standard deviation
        # But for now we are using constant values
        pr_loc = np.zeros(len(pr_data_loc))
        pr_loc.fill(1)

        pr_loc_data = pr_data_loc * pr_loc / PR_DATA

        pred = sample_points[np.argmin(pr_loc_data)]
        predictions.append(pred)

    print(predictions)
    data_points.append([0, 0])
    plot_ar(predictions, data_points)
    plot_xy(toxy(predictions), data_points_xy)
    # plot_eval(sample_points, pr_loc_data)

    cone_labels = np.array([[0.0, 3.0]] * len(predictions))

    evaluate_results(predictions, cone_labels)

if __name__ == "__main__":
    main()