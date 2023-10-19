import os
import cv2
import logging.handlers
from multiprocessing import Process, Value, Manager
from turbojpeg import TurboJPEG, TJFLAG_PROGRESSIVE

from src.process import *


# logger = logging.getLogger('__main__')

manager = Manager()
rgbd = manager.dict()


def _gen_meta():
    """
    :return: meta data dictionary
    """
    d = dict()
    d['use'] = Value('b', True)
    d['run'] = Value('b', False)
    d['fps'] = Value('f', 0.0)
    d['send'] = Value('b', False)

    return d


class Stream:
    def __init__(self, cfg):
        self.openCL = False

        if cv2.ocl.haveOpenCL():
            cv2.ocl.setUseOpenCL(True)
            self.openCL = True

        self.cfg = cfg.clone()

        self.proc_list = []

        self.jpeg = TurboJPEG()

        self.meta = dict()

        self.meta['CONNECT']  = Value('b', False)
        self.meta['LATENCY']  = Value('f', 0.0)

        # self.color = None
        # self.depth = None

        #####
        # meta를 이용하든, rgb, depth를 반환하든 해서 꺼내기

    def build_pipeline(self):
        if self.check_cam():
            self.proc_list.extend([1, Process(target=monitor, args=(self.cfg, self.meta))])
            self.proc_list.extend([1, Process(target=sync, args=(self.cfg, self.meta))])

            if self.cfg.HW_INFO.STEREO_L.USE:
                self.meta['STEREO_L'] = _gen_meta()
                self.proc_list.extend([1, Process(target=stream_sony, args=(self.cfg, self.meta, 'STEREO_L'))])

            if self.cfg.HW_INFO.STEREO_R.USE:
                self.meta['STEREO_R'] = _gen_meta()
                self.proc_list.extend([1, Process(target=stream_sony, args=(self.cfg, self.meta, 'STEREO_R'))])

            if self.cfg.HW_INFO.RGBD.USE:
                self.meta['RGBD'] = _gen_meta()
                self.proc_list.extend([1, Process(target=stream_kinect,
                                                  args=(self.cfg, self.meta, rgbd, 'RGBD'))])

            #### pipeline을 하나 더 만들어야하나?
        else:
            logger.info("No camera selected.")

    def run(self):
        print("")
        print("[INFO] Web camera stream service start.")
        print(f"[INFO] OpenCL activate: {self.openCL}")

        if self.proc_list:
            cores = self.proc_list[0::2]
            procs = self.proc_list[1::2]
            total_core = list(range(sum(cores)))

            used_core = 0

            # Start worker processes
            for core, proc in zip(cores, procs):
                proc.daemon = True
                proc.start()

                os.sched_setaffinity(proc.pid, total_core[used_core:used_core + core])
                used_core += core

            # Join the worker processes
            for proc in procs:
                proc.join()


    def check_cam(self):
        if self.cfg.HW_INFO.STEREO_L.USE or self.cfg.HW_INFO.STEREO_R.USE or self.cfg.HW_INFO.RGBD.USE:
            return True
        else:
            return False

    def bytescode(self):
        frame = rgbd['color']
        # frame = cv2.resize(frame, dsize=(out_width * 2, out_height), fx=0.5, fy=0.5,
        #                    interpolation=cv2.INTER_AREA)
        # frame = l_img
        # frame = cv2.resize(frame, dsize=(out_width*1, out_height), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)

        # if stat:
        #     cv2.rectangle(frame, (0, 0), (120, 30), (0, 0, 0), -1)
        #     fps = f"FPS : {str(fps())}"
        #     cv2.putText(frame, fps, (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1, cv2.LINE_AA)

        # return cv2.imencode(".jpg", frame)[1].tobytes()

        # val = self.jpeg.encode(frame, quality=80, flags=TJFLAG_PROGRESSIVE)

        print("jpeg")

        return self.jpeg.encode(frame, quality=50)  # , flags=TJFLAG_PROGRESSIVE)

    def __del__(self):
        if self.proc_list:
            for proc in self.proc_list[1::2]:
                proc.terminate()
