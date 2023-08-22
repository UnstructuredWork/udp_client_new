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
    d['use'] = Value('b', False)
    d['run'] = Value('b', False)
    d['fps'] = Value('f', 0.0)
    d['lat'] = Value('f', 0.0)

    return d


class Stream:
    def __init__(self, cfg):
        self.cfg = cfg.clone()

        self.proc_list = []

        self.meta = dict()

        self.meta['CONNECT']  = Value('b', False)
        self.meta['LATENCY']  = Value('f', 0.0)

    def build_pipeline(self):
        if self.cfg.SW_INFO.STEREO_L:
            self.proc_list.extend([1, Process(target=play_avi, args=(self.cfg, 'STEREO_L'))])

        if self.cfg.SW_INFO.STEREO_R:
            self.proc_list.extend([1, Process(target=play_avi, args=(self.cfg, 'STEREO_R'))])

        if self.cfg.SW_INFO.RGBD:
            self.proc_list.extend([1, Process(target=play_mkv, args=(self.cfg, 'RGBD'))])

        if self.cfg.SW_INFO.DETECTION:
            self.proc_list.extend([1, Process(target=play_h5, args=(self.cfg, 'DETECTION'))])

        if self.cfg.SW_INFO.MONO_DEPTH:
            self.proc_list.extend([1, Process(target=play_h5, args=(self.cfg, 'MONO_DEPTH'))])

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

                used_core += core

            # Join the worker processes
            for proc in procs:
                proc.join()

    def __del__(self):
        if self.proc_list:
            for proc in self.proc_list[1::2]:
                proc.terminate()
