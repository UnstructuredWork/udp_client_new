import argparse
import time

from flask import Flask
from flask import Response
from flask import render_template
from flask import stream_with_context

from src.config import get_cfg, setup_logger, setup_chrony
from src import Stream

def setup_cfg(cfg_file):
    cfg = get_cfg()
    cfg.merge_from_file(cfg_file)
    return cfg

def get_parser():
    parser = argparse.ArgumentParser(description="Cloud Server configs")
    parser.add_argument('-c', '--config-file',
                        default="./config/config.yaml",
                        help="A configuration file of camera")
    return parser.parse_args()

app = Flask(__name__)

args = get_parser()
cfg = setup_cfg(args.config_file)
setup_logger(cfg.SYSTEM.LOG.SAVE)
setup_chrony(cfg.SYSTEM.SYNC.SERVER)

s = Stream(cfg)
s.build_pipeline()
s.run()

# NOW = str(datetime.now())

# @app.route('/stream/kinect')
# def stream():
#     def generate():
#         try:
#             print("[INFO] Connected sony cam streaming URL from remote.")
#
#             while True:
#                 # if s.meta['RGBD'] is not None:
#                 # if s.color is not None:
#                 frame = s.bytescode()
#
#                 yield (b'--frame\r\n'
#                         b'Content-Type: image/jpeg\r\n'
#                         b'Content-Length: ' + f"{len(frame)}".encode() + b'\r\n'b'\r\n' + frame + b'\r\n')
#
#         except GeneratorExit:
#             print("[INFO] Disconnected sony cam streaming URL from remote.")
#             # streamer.stop()
#
#     try:
#         response = Response(stream_with_context(generate()),
#                             mimetype='multipart/x-mixed-replace; boundary=frame')
#
#         return response
#
#     except Exception as e:
#
#         print(e)
#
#
# @app.route('/')
# def index():
#     latency_current_time = time.time()
#     template_data = {'time': str(latency_current_time)}
#     return render_template('index.html', **template_data)