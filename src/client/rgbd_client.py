import cv2
import zlib
import struct

from .client import Client
from datetime import datetime
from src.parallel import thread_method

class RgbdClient(Client):
    def __init__(self, cfg, meta, side):
        super().__init__(cfg, meta, side)
        self.rgb       = None
        self.depth     = None
        self.cam_info  = None

    def bytescode(self, package):
        rgb = self.rgb
        depth = self.depth
        package.get_img_time = datetime.now().time().isoformat().encode('utf-8')
        package.cam_info = self.cam_info
        package.frame = self.comp.encode(self.resize(rgb, package), 40) + b'frame' + \
                        cv2.imencode('.png', self.resize(depth, package), [cv2.IMWRITE_PNG_COMPRESSION, 4])[1].tobytes()
        check = zlib.crc32(package.frame)
        if self.duplicate_check != check:
            self.duplicate_check = check
            package.header = struct.pack("!I", check)
            self.send_udp(package)

    @thread_method
    def run(self, data):
        self.rgb = data["rgb"]
        self.depth = data["depth"]
        self.cam_info = data["intrinsic"] + b'info' + data["imu"]
        if self.pack_cloud is not None:
            self.bytescode(self.pack_cloud)

        if self.pack_unity is not None:
            self.bytescode(self.pack_unity)