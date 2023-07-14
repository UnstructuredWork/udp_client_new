import os
import time
import subprocess

from src.load_cfg import LoadConfig
from ntplib import NTPClient, NTPException

current_dir = os.getcwd()
config_file = os.path.join(current_dir, "config/config.yaml")

class NtpClient():
    def __init__(self):
        self.cfg = LoadConfig(config_file).info
        self.offset = self.cfg["offset"]
        self.restart = self.cfg["restart"]
        self.ntp_client = NTPClient()
        self.ntp_server = self.cfg["ntp_server"]

    def chrony(self):
        print('[INFO] Restart chrony')
        subprocess.run(['sudo', 'systemctl', 'restart', 'chrony'])

    def run(self):
        while True:
            try:
                response = self.ntp_client.request(self.ntp_server, version=3)
                offset = response.offset * 1000
                if self.restart:
                    if abs(offset) < self.offset:
                        print('[INFO] Offset exceeds threshold { offset: ' + str(round(offset, 2)) + ' threshold: ' +
                              str(self.offset) + ' }')

                        self.chrony()

                        time.sleep(5)

                time.sleep(0.5)
            except NTPException as e:
                print("[INFO] " + str(e))