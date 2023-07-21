import os
import logging.handlers
from multiprocessing import Process, Value

from src.process import *


logger = logging.getLogger('__main__')

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
        self.cfg = cfg.clone()

        self.proc_list = []

        self.meta = dict()

        self.meta['CONNECT']  = Value('b', False)
        self.meta['LATENCY']  = Value('f', 0.0)

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
                self.proc_list.extend([1, Process(target=stream_kinect, args=(self.cfg, self.meta, 'RGBD'))])
        else:
            logger.info("No camera selected.")

    def run(self):
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

    def __del__(self):
        if self.proc_list:
            for proc in self.proc_list[1::2]:
                proc.terminate()
