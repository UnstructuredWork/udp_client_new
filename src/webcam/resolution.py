def get_resolution(res):
    width = None
    height = None

    if res == "4K" or res == "4k" or res == "UHD":
        width  = 3840
        height = 2160

    elif res == "1440" or res == "QHD":
        width  = 2560
        height = 1440

    elif res == "1080" or res == "FHD":
        width  = 1920
        height = 1080

    elif res == "720" or res == "HD":
        width  = 1280
        height = 720

    elif res == "540":
        width  = 960
        height = 540

    else:
        width  = 1920
        height = 1080

    return width, height