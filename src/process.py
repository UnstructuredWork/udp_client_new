import logging.handlers
import time

from src.play import *
from src.client import *
from src.config import get_latency

logger = logging.getLogger('__main__')

def play_avi(cfg, side):
    f = SingleImage('src/data/' + side + '.avi')
    f.run()

    c = SingleDataClient(cfg.SERVER, side)
    while True:
        if f.result is not None:
            c.run(f.result)

def play_mkv(cfg, side):
    f = MultipleData('src/data/' + side + '.mkv')
    f.run()

    c = MultipleDataClient(cfg.SERVER, side)
    while True:
        if f.result["rgb"] is not None and f.result["depth"] is not None:
            c.run(f.result)

def play_h5(cfg, side):
    f = H5Player('src/data/' + side + '.h5', side)
    f.run()

    c = SingleDataClient(cfg.SERVER, side)
    while True:
        if f.result is not None:
            c.run(f.result)

def sync(cfg, meta):
    server_conn = False

    while True:
        try:
            latency = get_latency(cfg.SYSTEM.SYNC.SERVER)

            if isinstance(latency, float):
                meta['CONNECT'].value = True
                meta['LATENCY'].value = latency

                if not server_conn:
                    logger.info('Connected to sync server.')
                    server_conn = True

                if cfg.SYSTEM.SYNC.RESTART and abs(latency) > cfg.SYSTEM.SYNC.TOLERANCE:
                    logger.info(f"High latency: {latency:.2f} ms")

                    try:
                        logger.info(f"Restart sync service.")
                        time.sleep(5)
                    except Exception as e:
                        logger.warning(f"Failed to restart sync service. {e}")
            else:
                meta['CONNECT'].value = False
                meta['LATENCY'].value = 999999

                if server_conn:
                    server_conn = False
                    logger.info('Disconnected to sync server.')
                    logger.info('Getting sleep mode.')

                logger.warning(f"Failed to get latency. {latency}")

        except Exception as e:
            logger.warning(e)

        time.sleep(1)
