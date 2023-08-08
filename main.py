import argparse

from src.config import get_cfg
from src.custom.kinect_file import RgbdStreamer
from src.custom.webcam_file import StereoStreamer

def main():
    args = get_parser()
    cfg = setup_cfg(args.config_file)

    s1 = StereoStreamer(cfg.HW_INFO, 'STEREO_L')
    s2 = StereoStreamer(cfg.HW_INFO, 'STEREO_R')
    r = RgbdStreamer(cfg.HW_INFO.RGBD)

    s1.run()
    s2.run()
    r.run()

def setup_cfg(cfg_file):
    cfg = get_cfg()
    cfg.merge_from_file(cfg_file)
    return cfg

def get_parser():
    parser = argparse.ArgumentParser(description="Cloud Server configs")
    parser.add_argument('-c', '--config-file',
                        default="./config/config.yaml",
                        help="A configuration custom of camera")
    return parser.parse_args()

if __name__ == "__main__":
    main()