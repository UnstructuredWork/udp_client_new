import cv2
import time

from .file_play import FilePlay

class SingleImage(FilePlay):
    def __init__(self, file_path):
        super().__init__(file_path)

    def update(self):
        video = cv2.VideoCapture(self.file)
        frame_duration = 1 / video.get(cv2.CAP_PROP_FPS)

        while True:
            ret, frame = video.read()

            self.curr_time = time.perf_counter()

            elapsed_time = self.curr_time - self.prev_time
            if ret:
                if elapsed_time > frame_duration:
                    self.prev_time = time.perf_counter()
                    self.result = frame
                else:
                    self.result = None

            if video.get(cv2.CAP_PROP_POS_FRAMES) == video.get(cv2.CAP_PROP_FRAME_COUNT):
                video.open(self.file)

        video.release()
        cv2.destroyAllWindows()