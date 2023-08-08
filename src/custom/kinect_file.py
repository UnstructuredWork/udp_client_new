import cv2
import csv
import h5py
import time
import pickle
import numpy as np

from src.parallel import thread_method
from datetime import datetime, timedelta

import pyk4a
from pyk4a import Config, PyK4A

class RgbdStreamer:
    def __init__(self, cfg):
        self.openCL = False

        if cv2.ocl.haveOpenCL():
            cv2.ocl.setUseOpenCL(True)
            self.openCL = True

        self.cfg = cfg

        self.fps_list = {"30": pyk4a.FPS.FPS_30,
                         "15": pyk4a.FPS.FPS_30,
                         "5": pyk4a.FPS.FPS_30}

        self.resolution_list = {"3072": pyk4a.ColorResolution.RES_3072P,
                                "2160": pyk4a.ColorResolution.RES_2160P,
                                "1536": pyk4a.ColorResolution.RES_1536P,
                                "1440": pyk4a.ColorResolution.RES_1440P,
                                "1080": pyk4a.ColorResolution.RES_1080P,
                                "720": pyk4a.ColorResolution.RES_720P}

        self.k4a = PyK4A(
            Config(
                color_resolution=self.resolution_list[str(self.cfg.SIZE[1])],
                depth_mode=pyk4a.DepthMode.WFOV_2X2BINNED,
                camera_fps=self.fps_list[str(self.cfg.FPS)]
            )
        )

        self.result = {"imu": None,
                       "rgb": None,
                       "depth": None}

        self.current_time = time.time()
        self.preview_time = time.time()

        self.sec = 0

        self.set()

        self.started  = False

        self.vid = cv2.VideoWriter('RGB.avi', cv2.VideoWriter_fourcc(*'DIVX'), self.cfg.FPS, (self.cfg.SIZE[0], self.cfg.SIZE[1]))
        self.hdf5 = h5py.File('DEPTH.h5', 'w')
        # self.csv = open('IMU.csv', 'w', newline='')
        # self.csv_wr = csv.writer(self.csv)
        self.index = 0

        self.record_duration = timedelta(minutes=5)
        self.s_time = datetime.now()
        self.e_time = self.s_time + self.record_duration

    def set(self):
        self.k4a.start()
        self.k4a.whitebalance = 4500
        assert self.k4a.whitebalance == 4500
        self.k4a.whitebalance = 4510
        assert self.k4a.whitebalance == 4510

    @thread_method
    def run(self):
        # self.imu_update()
        self.frame_update()

        self.started = True

        print("[INFO] Kinect connection is complete.")

        self.str = time.time()

    def stop(self):
        self.started = False

        self.k4a._stop_imu()
        self.k4a.stop()

        print("[INFO] Kinect stopped.")

    @thread_method
    def imu_update(self):
        while True:
            if self.started:
                acc_xyz = self.k4a.get_imu_sample().pop("acc_sample")
                gyro_xyz = self.k4a.get_imu_sample().pop("gyro_sample")
                self.result["imu"] = pickle.dumps([acc_xyz, gyro_xyz])

                if datetime.now() < self.e_time:
                    self.csv_wr.writerow([acc_xyz, gyro_xyz])
                else:
                    print('----------------------------Record IMU----------------------------')
                    self.csv.close()

    @thread_method
    def frame_update(self):
        while True:
            if self.started:
                self.result["rgb"] = self.k4a.get_capture().color[:, :, :3]
                self.result["depth"] = self.k4a.get_capture().transformed_depth

                if datetime.now() < self.e_time:
                    self.vid.write(self.result["rgb"])
                    self.hdf5[str(self.index)] = self.result['depth']
                    self.index += 1
                else:
                    print('----------------------------Record RGBD----------------------------')
                    self.vid.release()
                    self.hdf5.close()

    def fps(self):
        self.current_time = time.time()
        self.sec = self.current_time - self.preview_time
        self.preview_time = self.current_time
        if self.sec > 0:
            fps = round((1/self.sec), 1)
        else:
            fps = 1

        return fps