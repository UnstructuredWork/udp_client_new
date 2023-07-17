import time
import logging.handlers


logger = logging.getLogger('__main__')

class LogPrinter:
    def __init__(self, cfg):
        self.cfg = cfg
        self.data = None

        self.print_cycle = cfg.SYSTEM.LOG.PRINT_PERIOD
        self.server_conn = False

        time.sleep(1)

    def update(self, data):
        self.show(data)

        time.sleep(self.print_cycle)

    def show(self, data):
        if data['CONNECT'].value:
            if not self.server_conn:
                self.server_conn = True
                self.print_cycle = self.cfg.SYSTEM.LOG.PRINT_PERIOD

            logger.info(
                f"Sync server conn: {data['CONNECT'].value}. Sync latency: {data['LATENCY'].value:.2f} ms"
            )

            for k, v in data.items():
                if k in ['STEREO_L', 'STEREO_R', 'RGBD']:
                    logger.info(f"{k:<8} - RUN: {bool(v['run'].value)}. "
                                f"Send: {bool(v['send'].value)}. FPS: {int(v['fps'].value):>2}.")

        else:
            self.server_conn = False
            logger.info("Waiting for connection with sync server...")

            self.print_cycle = 60
