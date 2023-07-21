import argparse

from src.config import get_cfg, setup_logger, setup_chrony
from src import Stream


def main():
    args = get_parser()
    cfg = setup_cfg(args.config_file)

    setup_logger(cfg.SYSTEM.LOG.SAVE)
    setup_chrony(cfg.SYSTEM.SYNC.SERVER)

    s = Stream(cfg)
    s.build_pipeline()

    s.run()

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


if __name__ == "__main__":
    main()
