import cv2
import time
import h5py

from .file_play import FilePlay
from src.parallel import thread_method

class MultipleData(FilePlay):
    def __init__(self, file_path):
        super().__init__(file_path)

        self.result = {"rgb": None,
                       "depth": None}

    @thread_method
    def update(self):
        video = cv2.VideoCapture(self.file[0])
        frame_duration = 1 / video.get(cv2.CAP_PROP_FPS)
        hdf5 = h5py.File(self.file[1], 'r')
        index = 0

        while True:
            ret, frame0 = video.read()

            self.curr_time = time.perf_counter()

            elapsed_time = self.curr_time - self.prev_time
            if ret:
                if elapsed_time > frame_duration:
                    self.prev_time = time.perf_counter()

                    frame1 = hdf5[str(index)][:]
                    index += 1

                    self.result["rgb"] = frame0
                    self.result["depth"] = frame1
                else:
                    self.result = {"rgb": None,
                                   "depth": None}

            if video.get(cv2.CAP_PROP_POS_FRAMES) == video.get(cv2.CAP_PROP_FRAME_COUNT):
                video.open(self.file[0])

                hdf5 = h5py.File(self.file[1], 'r')
                index = 0

        video.release()
        cv2.destroyAllWindows()