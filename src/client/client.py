from __future__ import division
import cv2
import math
import socket
import struct
import subprocess

from nvjpeg import NvJpeg
from turbojpeg import TurboJPEG

class Package:
    def __init__(self, cfg, side):
        self.cfg = cfg

        self.host = self.cfg.HOST

        self.side = side
        if self.side == 'STEREO_L':
            self.port = self.cfg.PORT.STEREO_L
            self.size = self.cfg.SIZE.STEREO_L
        elif self.side == 'STEREO_R':
            self.port = self.cfg.PORT.STEREO_R
            self.size = self.cfg.SIZE.STEREO_R
        else:
            self.port = self.cfg.PORT.RGBD
            self.size = self.cfg.SIZE.RGBD

        self.imu = None

        self.frame = None
        self.get_img_time = None

        self.header = None

class Client:
    def __init__(self, cfg, meta, side):
        self.sock = None
        self.sock_udp()

        self.img_num = 1

        self.duplicate_check = None

        self.prev_time = 0
        self.curr_time = 0

        self.frame_duration = 1 / 60

        self.MAX_IMAGE_DGRAM = 2 ** 16 - 256

        self.cfg = cfg

        self.side = side

        if subprocess.check_output(['nvidia-smi']):
            self.comp = NvJpeg()
        else:
            self.comp = TurboJPEG()

        if cfg.CLOUD.SEND:
            self.pack_cloud = Package(self.cfg.CLOUD, side)
        else:
            self.pack_cloud = None

        if cfg.UNITY.SEND:
            self.pack_unity = Package(self.cfg.UNITY, side)
        else:
            self.pack_unity = None

    def __del__(self):
        self.sock.close()

    def sock_udp(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def send_udp(self, package):
        size = len(package.frame)
        count = math.ceil(size / (self.MAX_IMAGE_DGRAM))
        total_count = count
        array_pos_start = 0
        if self.img_num > 99:
            self.img_num = 1

        while count:
            array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
            packet_num = (str(self.img_num).zfill(3) + '-' +
                          str(total_count) + '-' +
                          str(total_count - count + 1)).encode('utf-8')

            try:
                if package.imu is None:
                    self.sock.sendto(struct.pack("B", count) + b'end' +
                                     package.header + b'end' +
                                     packet_num + b'end' +
                                     package.get_img_time + b'end' +
                                     str(len(package.frame)).encode('utf-8') + b'end' +
                                     str(array_pos_start).encode('utf-8') + b'end' +
                                     package.frame[array_pos_start:array_pos_end], (package.host[0], package.port))
                else:
                    self.sock.sendto(struct.pack("B", count) + b'end' +
                                     package.header + b'end' +
                                     packet_num + b'end' +
                                     package.get_img_time + b'end' +
                                     str(len(package.frame)).encode('utf-8') + b'end' +
                                     str(array_pos_start).encode('utf-8') + b'end' +
                                     package.imu + b'end' +
                                     package.frame[array_pos_start:array_pos_end], (package.host[0], package.port))
            except OSError:
                pass

            array_pos_start = array_pos_end
            count -= 1

        self.img_num += 1

    def resize(self, frame, package):
        if frame.shape[0] == package.size[1]:
            return frame
        else:
            frame = cv2.resize(frame, dsize=(package.size), fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            return frame
