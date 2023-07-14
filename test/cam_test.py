import cv2

from src.load_cfg import LoadConfig
from src.webcam.webcam_set import CamSet

config = LoadConfig("./config/config.yaml")

l_cam = CamSet(config.info, "left")
r_cam = CamSet(config.info, "right")

while True:
    ret1, frame1 = l_cam.read()
    ret2, frame2 = r_cam.read()

    frame = cv2.hconcat(([frame1, frame2]))

    cv2.imshow("1", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cv2.destroyAllWindows()

def __exit__():
    l_cam.release()
    r_cam.release()
