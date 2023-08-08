import cv2
import time
import logging.handlers

from src.parallel import thread_method
from src.webcam.webcam_set import CamSet

logger = logging.getLogger('__main__')

class StereoStreamer:
    def __init__(self, cfg, meta, side):
        self.openCL = False
        if cv2.ocl.haveOpenCL():
            cv2.ocl.setUseOpenCL(True)
            self.openCL = True

        self.side = side
        if self.side == 'STEREO_L':
            self.cfg = cfg.STEREO_L
        else:
            self.cfg = cfg.STEREO_R

        self.cam = None
        self.cam_thread = None

        self.current_time = time.time()
        self.preview_time = time.time()

        self.sec = 0

        self.img = None

        w, h = self.cfg.SIZE

        self.out_width = w
        self.out_height = h

        self.frame_time = None

        self.started = False

    @thread_method
    def run(self):
        print("")
        logger.info("Web camera stream service start.")
        logger.info(f"[INFO] OpenCL activate: {self.openCL}")
        self.stop()

        self.cam = CamSet(self.cfg)
        if self.side == 'STEREO_L':
            logger.info(f"[INFO] Left  camera initialization complete.")
        else:
            logger.info(f"[INFO] Right camera initialization complete.")

        self.cam_update()

        self.started = True

        logger.info("[INFO] All camera connections are complete.")

    def stop(self):
        self.started = False

        if self.cam is not None:
            self.cam.release()

        logger.info("[INFO] All camera stopped.")

    @thread_method
    def cam_update(self):
        while True:
            if self.started:
                ret, frame = self.cam.read()

                if ret:
                    self.img = frame

    def fps(self):
        self.current_time = time.time()
        self.sec = self.current_time - self.preview_time
        self.preview_time = self.current_time

        if self.sec > 0:
            fps = round((1/self.sec), 1)

        else:
            fps = 1

        return fps

    def __exit__(self):
        logger.info("[INFO] Streamer class exit")
        self.cam.release()