import cv2
import time
import subprocess
import logging.handlers

from nvjpeg import NvJpeg
from turbojpeg import TurboJPEG

from src.parallel import thread_method
from src.fps import FPS
from src.webcam.webcam_set import CamSet


logger = logging.getLogger('__main__')

class StereoStreamer:
    def __init__(self, cfg, meta, side):
        if cv2.ocl.haveOpenCL():
            cv2.ocl.setUseOpenCL(True)

        self.side = side
        if self.side == 'STEREO_L':
            self.cfg = cfg.STEREO_L
        else:
            self.cfg = cfg.STEREO_R

        self.meta = meta

        self.cam = None
        self.fps = FPS()

        self.img = None

        if subprocess.check_output(['nvidia-smi']):
            self.comp = NvJpeg()
        else:
            self.comp = TurboJPEG()

        w, h = self.cfg.SIZE

        self.out_width = w
        self.out_height = h

        self.frame_time = None

        self.started = False

    def run(self):
        logger.info(f"Start streaming camera:  [{self.side}]")
        self.stop()

        self.cam = CamSet(self.cfg)
        logger.info(f"Complete initialize camera: [{self.side}]")

        self.cam_update()

        self.started = True
        self.meta[self.side]['run'].value = self.started

    def stop(self):
        self.started = False

        self.meta[self.side]['run'].value = self.started
        self.meta[self.side]['fps'].value = 0.0

        if self.cam is not None:
            self.cam.release()
            logger.info("All camera stopped.")

    @thread_method
    def cam_update(self):
        while True:
            if self.started:
                ret, frame = self.cam.read()

                if ret:
                    self.img = frame

                    self.fps.update()
                    self.meta[self.side]['fps'].value = self.fps.get()

    def __exit__(self):
        logger.info("[INFO] Streamer class exit.")
        self.cam.release()
