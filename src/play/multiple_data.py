import cv2

from .file_play import FilePlay
from pyk4a import PyK4APlayback, ImageFormat

class MultipleData(FilePlay):
    def __init__(self, file_path):
        super().__init__(file_path)

        self.play = None
        self.result = {"rgb": None,
                       "depth": None}

    def color(self, color_format: ImageFormat, color_image):
        if color_format == ImageFormat.COLOR_MJPG:
            color_image = cv2.imdecode(color_image, cv2.IMREAD_COLOR)
        elif color_format == ImageFormat.COLOR_NV12:
            color_image = cv2.cvtColor(color_image, cv2.COLOR_YUV2BGRA_NV12)
        elif color_format == ImageFormat.COLOR_YUY2:
            color_image = cv2.cvtColor(color_image, cv2.COLOR_YUV2BGRA_YUY2)
        return color_image

    def update(self):
        self.play = PyK4APlayback(self.file)
        self.play.open()

        while True:
            try:
                capture = self.play.get_next_capture()
                if capture.color is not None:
                    self.result["rgb"] = self.color(self.play.configuration["color_format"], capture.color)
                if capture.depth is not None:
                    self.result["depth"] = capture.transformed_depth
            except EOFError:
                self.play.close()
                self.play.open()

        self.play.close()
        cv2.destroyAllWindows()