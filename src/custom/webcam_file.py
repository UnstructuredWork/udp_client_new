import cv2
import time

from src.parallel import thread_method
from src.webcam.webcam_set import CamSet

class StereoStreamer:
    def __init__(self, cfg, side):
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

        self.current_time = time.time()
        self.preview_time = time.time()

        self.sec = 0

        self.vid = cv2.VideoWriter(str(self.side) + '.avi', cv2.VideoWriter_fourcc(*'DIVX'),
                                   self.cfg.FPS, (self.cfg.SIZE[0], self.cfg.SIZE[1]))

        self.set()
        self.started = False

        self.count = 0
        self.capture_count = 18000 # 60fps X 300 = 18000

    def set(self):
        self.cam = CamSet(self.cfg)

    @thread_method
    def run(self):
        self.started = True
        self.cam_update()

    def stop(self):
        self.started = False
        self.cam.release()
        self.vid.release()

    @thread_method
    def cam_update(self):
        if self.started:
            print(f"[INFO] {self.side} Recording...")
            while True:
                ret, frame = self.cam.read()
                if ret:
                    if self.count != self.capture_count:
                        self.vid.write(frame)
                        self.count += 1
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
