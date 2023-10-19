import logging.handlers
import time
import pickle

from client import RgbdClient
from client import StereoClient
from src.log_printer import LogPrinter
from src.config import get_latency, restart_chrony
from src.webcam.webcam_stream import StereoStreamer
from kinect import Kinect

logger = logging.getLogger('__main__')

def stream_sony(cfg, meta, side):
    s = StereoStreamer(cfg.HW_INFO, meta, side)
    s.run()

    c = StereoClient(cfg.SERVER, meta, side)
    while True:
        while meta['CONNECT'].value:
            try:
                if s.img is not None:
                    c.run(s.img)
                    meta[side]['send'].value = True

            except Exception as e:
                logger.error(e)

        meta[side]['send'].value = False

        time.sleep(1)

def stream_kinect(cfg, meta, rgbd, side):
    r = Kinect()
    r.start(size=cfg.HW_INFO.RGBD.SIZE[1])

    c = RgbdClient(cfg.SERVER, meta, side)

    while True:
        while meta['CONNECT'].value:
            try:
                _ = r.get_data()
                intrinsic = r.intrinsic_color.tobytes()
                while True:
                    s = time.time()
                    color, depth = r.get_data()
                    imu = r.get_imu()
                    imu = pickle.dumps(imu)

                    rgbd['color'] = color
                    rgbd['depth'] = depth

                    result = dict()
                    result['rgb'] = color
                    result['depth'] = depth
                    result['intrinsic'] = intrinsic
                    result['imu'] = imu

                    e = time.time()
                    cycle = (e - s) * 1000
                    cycle = 1000 / cycle

                    meta[side]['run'].value = True
                    meta[side]['send'].value = True
                    meta[side]['fps'].value = cycle

                    c.run(result)

                    # if r.result["depth"] is not None:
                    #     meta[side]['run'].value = True
                    #     meta[side]['fps'].value = r.fps()
                    #     c.run(r.result)
                    #     meta[side]['send'].value = True

            except Exception as e:
                logger.error(f"Can't open the [{side}] camera: {e}")

        meta[side]['send'].value = False
        meta[side]['fps'].value = 0

        time.sleep(1)

def stream_kinect_flask(cfg, meta, rgbd, side):
    @app.route('/stream/kinect')
    def stream():
        def generate():
            try:
                print("[INFO] Connected sony cam streaming URL from remote.")

                while True:
                    # if s.meta['RGBD'] is not None:
                    # if s.color is not None:
                    frame = s.bytescode()

                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n'
                           b'Content-Length: ' + f"{len(frame)}".encode() + b'\r\n'b'\r\n' + frame + b'\r\n')

            except GeneratorExit:
                print("[INFO] Disconnected sony cam streaming URL from remote.")
                # streamer.stop()

        try:
            response = Response(stream_with_context(generate()),
                                mimetype='multipart/x-mixed-replace; boundary=frame')

            return response

        except Exception as e:

            print(e)

    @app.route('/')
    def index():
        latency_current_time = time.time()
        template_data = {'time': str(latency_current_time)}
        return render_template('index.html', **template_data)


def monitor(cfg, meta):
    m = LogPrinter(cfg)

    while True:
        m.update(meta)

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
                        restart_chrony()
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
