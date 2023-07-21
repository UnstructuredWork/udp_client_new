import cv2
import pyudev

def serial2port(subsystem, serial):
    context = pyudev.Context()

    port = None

    for device in context.list_devices(subsystem=subsystem):
        if not port:
            if int(device.get("ID_SERIAL_SHORT")) == int(serial):
                test_port = int(device.get("DEVNAME")[-1])

                cap = cv2.VideoCapture(test_port)

                if cap.read()[0]:
                    port = test_port

                cap.release()

    if port is None:
        raise Exception(
            f"[ERROR] Serial number of device is error!!! Check the device serial number. not [{serial}]\n"
            f"[ERROR] Command:\n"
            f"\t\tudevadm info --name=/dev/video*")

    return port