import time
import torch
import warnings
import numpy as np

class Depth:
    def __init__(self, cfg):
        self.cfg = cfg

        self.width  = None
        self.height = None

        self.device = None
        self.transform = None

        self.midas = None
        self.midas_transforms = None

        self.inf_time = 0

        self.ready = False

        self.set()

    def set(self):
        try:
            self.width  = self.cfg.HW_INFO.MONO_DEPTH.SIZE[0]
            self.height = self.cfg.HW_INFO.MONO_DEPTH.SIZE[1]

            self.midas = torch.hub.load('intel-isl/MiDaS', self.cfg.HW_INFO.MONO_DEPTH.WEIGHT)

            self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

            self.midas.to(self.device)
            self.midas.eval()

            self.midas_transforms = torch.hub.load('intel-isl/MiDaS', 'transforms')

            self.transform = self.midas_transforms.dpt_transform

            _ = self.get(np.ones((100, 100, 3), dtype=np.uint8))

            self.ready = True

        except Exception as e:
            print(e)

    def get(self, rgb):
        if rgb is not None:
            _s = time.time()

            input_batch = self.transform(rgb).to(self.device)

            warnings.simplefilter('ignore')

            with torch.no_grad():
                prediction = self.midas(input_batch)

                prediction = torch.nn.functional.interpolate(prediction.unsqueeze(1),
                                                             size=rgb.shape[:2],
                                                             mode='bicubic',
                                                             align_corners=False).squeeze()

            pred_depth = prediction.cpu().numpy()

            inverse_depth = (pred_depth * 255) / np.max(pred_depth)
            inverse_depth = inverse_depth.astype('uint8')

            _e = time.time()

            self.inf_time = (_e - _s) * 1000

            return inverse_depth
        else:
            return np.ones((self.height, self.width), dtype=np.uint8)