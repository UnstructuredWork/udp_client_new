import cv2
import csv
import h5py
import time
import pickle

from src.parallel import thread_method

class FilePlay:
    def __init__(self, side, file_path):
        self.img = None
        self.side = side
        self.file = file_path
        self.result = {"imu": None,
                       "rgb": None,
                       "depth": None}

        self.curr_time = 0
        self.prev_time = 0

    @thread_method
    def run(self):
        if self.side == 'STEREO_L' or self.side == 'STEREO_R':
            self.rgb_update()
        elif self.side == 'RGBD':
            self.rgbd_update()
            self.imu_update()

    @thread_method
    def rgb_update(self):
        video = cv2.VideoCapture(self.file)
        frame_duration = 1 / video.get(cv2.CAP_PROP_FPS)

        self.curr_time = time.perf_counter()

        while video.isOpened():
            elapsed_time = self.curr_time - self.prev_time
            if elapsed_time > frame_duration:
                ret, frame = video.read()

                if ret:
                    self.img = frame

                self.prev_time = time.perf_counter()
            else:
                self.curr_time = time.perf_counter()

            if video.get(cv2.CAP_PROP_POS_FRAMES) == video.get(cv2.CAP_PROP_FRAME_COUNT):
                video.open(self.file)

        video.release()
        cv2.destroyAllWindows()

    @thread_method
    def rgbd_update(self):
        video = cv2.VideoCapture(self.file[0])
        frame_duration = 1 / video.get(cv2.CAP_PROP_FPS)

        hdf5  = h5py.File(self.file[1], 'r')
        index = 0

        self.curr_time = time.perf_counter()

        while True:
            elapsed_time = self.curr_time - self.prev_time
            if elapsed_time > frame_duration:
                ret, frame0 = video.read()
                frame1 = hdf5[str(index)][:]

                if not ret:
                    break

                self.result["rgb"] = frame0
                self.result["depth"] = frame1
                self.prev_time = time.perf_counter()
                index += 1
            else:
                self.curr_time = time.perf_counter()

            if video.get(cv2.CAP_PROP_POS_FRAMES) == video.get(cv2.CAP_PROP_FRAME_COUNT):
                video.open(self.file[0])

                hdf5 = h5py.File(self.file[1], 'r')
                index = 0

        video.release()
        cv2.destroyAllWindows()

    @thread_method
    def imu_update(self):
        imu = csv.reader(open(self.file[2], "r"))

        while True:
            for row in imu:
                acc_xyz = eval(row[0])
                gyro_xyz = eval(row[1])
                self.result["imu"] = pickle.dumps([acc_xyz, gyro_xyz])

            imu = csv.reader(open(self.file[2], "r"))