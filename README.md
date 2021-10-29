# Micro-AV Lidar

# Set up Environment 

- Open User Manual for YDLidar X4 on the [YDL official website](https://www.ydlidar.com/service_support.html) 
- Go to Section 3 - Linux ROS Operation, and follow steps 3.2:
	- [Download SDK driver](https://github.com/YDLIDAR/YDLidar-SDK)
	- Compile and Install YDLidar-SDK
	`$ git clone https://github.com/YDLIDAR/YDLidar-SDK.git`
	`$ cd YDLidar-SDK/build `
	`$ cmake ..`
	`$ make`
	`$ sudo make install`
- Install Dependencies
	`$ cd YDLidar-SDK`
	`$ pip install .` or `$ python setup.py build` + `$ python setup.py install`
	`$ pip install matplotlib`
- Open YDLidar-SDK/python/examples/plot_tof_test.py and change line 26 to this:
	`laser.setlidaropt(ydlidar.LidarPropSerialBaudrate, 128000)`
- Run
`$ cd YDLidar-SDK/python/examples/`
`$ python plot_tof_test.py`
- Your lidar should run and you can see a map on your screen
- Click the map and press 'q' to stop operation

# Getting .csv as result
- Download tof_test.py from this repo and replace the file in YDLidar-SDK/python/examples/
- run `python tof_test.py`
- Data will be stored in lidar_data.csv under the same folder
- See line 26 ~ 51 for the codes that output data to the file
