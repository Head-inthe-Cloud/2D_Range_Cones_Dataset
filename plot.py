import os
import ydlidar
import sys
from matplotlib.patches import Arc
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import csv

from datasets import extract_from_csv

RMAX = 32.0
NUM_SHOW = 2   # how many data in the file do you wish to see?

# Specify the data file path
DATA_FILE = 'data/12202021/lidar_data_3m.csv'


# Plot a frame with points in the form of [Angle, Rnage] or [Angle, Range, Intensity]
def plot_ar(frame):

        if np.shape(frame)[1] <= 3:
                frame = np.transpose(frame)

        '''
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(x = angle, y = ran)
        plt.show()
        '''
        # fig = plt.figure()
        # fig.canvas.set_window_title('YDLidar LIDAR Monitor')
        lidar_polar = plt.subplot(polar=True)
        lidar_polar = plt.subplot(polar=True)
        lidar_polar.autoscale_view(True,True,True)
        lidar_polar.set_rmax(RMAX)
        lidar_polar.grid(True)

        if len(frame) == 3:
                lidar_polar.scatter(frame[0], frame[1], c=frame[2], cmap='hsv', alpha=0.95)
        elif len(frame) == 2:
                lidar_polar.scatter(frame[0], frame[1], c='r', alpha=0.95)
        # lidar_polar.scatter(angle, ran, cmap='hsv', alpha=0.95)
        # lidar_polar.clear()
        # lidar_polar.scatter(angle, ran, alpha=0.95)
        plt.show()

def plot_xy(frame1, frame2=None):
        if len(np.shape(frame1)) == 2 and np.shape(frame1)[1] <= 3:
                frame1 = np.transpose(frame1)

        plt.plot(frame1[0], frame1[1], 'r.')

        if frame2:
                if np.shape(frame2)[1] <= 3:
                        frame2 = np.transpose(frame2)
                plt.plot(frame2[0], frame2[1], 'g.')
                
        plt.show()

if __name__ == "__main__":
        dataset = extract_from_csv(data_file, False)

        for i in range(NUM_SHOW):
                data = dataset[i]
                print(np.shape(data))
                plot_ar(data)