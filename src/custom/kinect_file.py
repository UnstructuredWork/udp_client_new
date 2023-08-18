import cv2
import time

from src.parallel import thread_method

import pyk4a
from pyk4a import Config, PyK4A, PyK4ARecord

class RgbdStreamer:
    def __init__(self, cfg, side):
        self.openCL = False

        if cv2.ocl.haveOpenCL():
            cv2.ocl.setUseOpenCL(True)
            self.openCL = True

        self.cfg = cfg
        self.side = side
        self.device = 0

        self.fps_list = {"30": pyk4a.FPS.FPS_30,
                         "15": pyk4a.FPS.FPS_30,
                         "5": pyk4a.FPS.FPS_30}

        self.resolution_list = {"3072": pyk4a.ColorResolution.RES_3072P,
                                "2160": pyk4a.ColorResolution.RES_2160P,
                                "1536": pyk4a.ColorResolution.RES_1536P,
                                "1440": pyk4a.ColorResolution.RES_1440P,
                                "1080": pyk4a.ColorResolution.RES_1080P,
                                "720": pyk4a.ColorResolution.RES_720P}

        self.cam_cfg = Config(
            color_resolution=self.resolution_list[str(self.cfg.SIZE[1])],
            color_format=pyk4a.ImageFormat.COLOR_MJPG,
            depth_mode=pyk4a.DepthMode.WFOV_2X2BINNED,
            camera_fps=self.fps_list[str(self.cfg.FPS)])

        self.k4a = PyK4A(
            config=self.cam_cfg,
            device_id=self.device
        )

        self.result = {"imu": None,
                       "rgb": None,
                       "depth": None}

        self.current_time = time.time()
        self.preview_time = time.time()

        self.sec = 0

        self.record = PyK4ARecord(
            device=self.k4a,
            config=self.cam_cfg,
            path=str(self.side) + '.mkv'
        )

        self.set()
        self.started = False

        self.capture_count = 9000  # 30fps X 300 = 9000

    def set(self):
        self.k4a.start()
        self.k4a.whitebalance = 4500
        assert self.k4a.whitebalance == 4500
        self.k4a.whitebalance = 4510
        assert self.k4a.whitebalance == 4510
        self.record.create()

    @thread_method
    def run(self):
        self.started = True
        self.cam_update()

    def stop(self):
        self.started = False
        self.k4a.stop()
        self.record.flush()
        self.record.close()

    @thread_method
    def cam_update(self):
        if self.started:
            print(f"[INFO] {self.side} Recording...")
            while True:
                capture = self.k4a.get_capture()
                if self.record.captures_count != self.capture_count:
                    self.record.write_capture(capture)
                else:
                    print(f"[INFO] {self.side} Exiting.")
                    self.stop()
                    break

    def fps(self):
        self.current_time = time.time()
        self.sec = self.current_time - self.preview_time
        self.preview_time = self.current_time
        if self.sec > 0:
            fps = round((1/self.sec), 1)
        else:
            fps = 1

        return fps