import os
import math
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
from plot import plot_ar, plot_xy, plot_eval
from utils import toxy, toar, normalize
from datasets import extract_from_csv

EPSILON = 10e-6    # This number is used to avoid division by 0

CONE_DIAMETER = 0.23
POINTS_PER_DEGREE = 1      # This number should be 3 based on previous calculation, but 1 seem to be more accurate in practice

# Pr(data) should depend on the state of the vehicle and GPS
# But for now we are using 1 as its value
PR_DATA = 1


# Returns the distance between two points, point => (x, y)
def get_distance(point1, point2):
    return pow(pow(point1[0] - point2[0], 2) + pow(point1[1] - point2[1], 2), 0.5)


# points is an array of points in xy form, center is a point in xy form, k is an integer
def get_k_nearest_points(data, center, k):
    sorted_points = sorted(data, key=lambda point: get_distance(point, center))
    return sorted_points[:k]


# returns MSE of arrays a and b
def mean_squared_error(a, b):
    assert len(a) > 0, "Input length has to be greater than 0"
    assert len(a) == len(b), "Input arrays must have the same lengths"
    return sum([pow(diff, 2) for diff in a - b]) / len(a)


# returns pr(data | location), the result has the same length as input samples
def get_pr_data_loc(data, samples):
    result = []
    for s_point in samples:
        # get k nearest points
        visual_angle = 2 * math.tan((CONE_DIAMETER / 2) / s_point[1]) * 180 / math.pi
        num_ideal_points = int(visual_angle * POINTS_PER_DEGREE)

        s_point = toxy(s_point)
        nearest_points = get_k_nearest_points(data, s_point, num_ideal_points)
        nearest_points = np.array(nearest_points)

        d_ideal_points = np.zeros(len(nearest_points))
        d_ideal_points.fill(CONE_DIAMETER / 2)
        d_nearest_points = [get_distance(n_point, s_point) for n_point in nearest_points]

        mse = mean_squared_error(d_ideal_points, d_nearest_points)

        result.append(1 / mse)
    return result


def get_pr_loc(LocX, LocY, sigma, sampled_points_xy):
    # pr_loc is calculated using methods in this website: https://www.askpython.com/python/normal-distribution
    # The pr(location) is calculated by subtracting the probability from 1:
    #     Upper limit(prob at distance) - lower limit(prob at 0)
    #     Multiply by 2 (it was only half of the probability)
    #     1 - the above result

    distances = [get_distance([LocX, LocY], sampled_point) for sampled_point in sampled_points_xy]
    # Plot normal distribution
    # pdf = norm.pdf(distances, loc=0, scale=sigma)
    # plt.plot(distances, pdf)
    # plt.xlabel("Distance From Center")
    # plt.ylabel("Probability Density")
    # plt.show()

    lower_limit = norm(loc=0, scale=sigma).cdf(0)
    result = [1 - (norm(loc=0, scale=sigma).cdf(distance) - lower_limit) * 2 for distance in distances]
    return result

def plot_points(points):
    for p in points:
        plt.scatter(p[0], p[1])
    plt.show()


def extract_data_points(data_path):
    dataset = extract_from_csv(data_path)
    # scan -- [[Angle, Range, Intensity] x N]
    # Angle vaule range: -pi ~ pi (radians)
    scan = []

    # scan -- [[Angle, Range] x N]
    for data_point in dataset[0]:
        if data_point[1] > 0:
            scan.append(data_point[:2])
    return scan


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


def get_new_sigma(new_center, points, pr_loc_data, sigma, threshold):
    if type(points) is not np.ndarray:
        points = np.array(points)
    if type(pr_loc_data) is not np.ndarray:
        pr_loc_data = np.array(pr_loc_data)
    possible_points = points[np.where(pr_loc_data > threshold)[0]]
    distances = np.sort(np.array([get_distance(new_center, point) for point in possible_points]))
    min_distance = distances[1] # skips the first element, which is the distance to center point itself
    return min_distance / (3 * sigma)


# Input: LocX, LocY, Sigma, Lidar data
# Output: New_LocX, New_LocY, New_Sigma, PrDetect
def template_matching(LocX, LocY, sigma, lidar_data, eval_mode=False):
    # data_points = extract_data_points()
    data_points = lidar_data
    data_points_xy = toxy(data_points)

    sample_range = 3 * sigma
    sample_gap = 0.05  # how far each sample is from each other

    center_point_xy = [LocX, LocY]

    # create sample points
    sample_points_xy = []

    n = int(sample_range * 2 / sample_gap)

    temp_x = center_point_xy[0] - sample_range
    temp_y = center_point_xy[1] - sample_range
    for i in range(n):
        for j in range(n):
            sample_points_xy.append([temp_x + i * sample_gap, temp_y + j * sample_gap])

    sample_points = toar(sample_points_xy)

    pr_data_loc = np.array(get_pr_data_loc(data_points_xy, sample_points))
    pr_loc = np.array(get_pr_loc(LocX, LocY, sigma, sample_points_xy))
    pr_loc_data = normalize(pr_data_loc * pr_loc / PR_DATA)
    pr_detect = np.amax(pr_loc_data)
    pred = toxy(sample_points[np.argmax(pr_loc_data)])
    new_LocX, new_LocY = pred

    new_sigma = get_new_sigma(pred, sample_points_xy, pr_loc_data, sigma, 0.5)

    if eval_mode:
        print(pred)
        print(pr_data_loc)
        data_points.append([0, 0])
        # plot_eval(sample_points, pr_data_loc)
        # plot_eval(sample_points, pr_loc)
        plot_ar(pred, data_points)
        plot_xy(toxy(pred), data_points_xy, True)
        plot_eval(sample_points, pr_loc_data)
        cone_label = [[0.0, 3.0]]

        evaluate_results([pred], cone_label)

    return new_LocX, new_LocY, new_sigma, pr_detect

if __name__ == "__main__":
    # template_matching(3, 0, 0.35, extract_data_points("data/12202021/lidar_data_3m.csv"), True)
    template_matching(2.0, 0, 0.35, extract_data_points("data/12202021/lidar_data_noisy_3m_2.csv"))
