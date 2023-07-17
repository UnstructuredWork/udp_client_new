import cv2
import time
import pickle
import subprocess

from src.parallel import thread_method

import pyk4a
from pyk4a import Config, PyK4A
from nvjpeg import NvJpeg
from turbojpeg import TurboJPEG

class RgbdStreamer:
    def __init__(self, cfg, meta):
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

        if subprocess.check_output(['nvidia-smi']):
            self.comp = NvJpeg()
        else:
            self.comp = TurboJPEG()

        self.started  = False

    def set(self):
        self.k4a.start()
        self.k4a.whitebalance = 4500
        assert self.k4a.whitebalance == 4500
        self.k4a.whitebalance = 4510
        assert self.k4a.whitebalance == 4510

    def run(self):
        self.imu_update()
        self.frame_update()

        self.started = True

        print("[INFO] Kinect connection is complete.")

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

    @thread_method
    def frame_update(self):
        while True:
            if self.started:
                self.result["rgb"] = self.k4a.get_capture().color[:, :, :3]
                self.result["depth"] = self.k4a.get_capture().transformed_depth


    def fps(self):
        self.current_time = time.time()
        self.sec = self.current_time - self.preview_time
        self.preview_time = self.current_time
        if self.sec > 0:
            fps = round((1/self.sec), 1)
        else:
            fps = 1

        return fps