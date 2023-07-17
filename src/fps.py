import time


class FPS:
    def __init__(self):
        self.sec = 0
        self.current_time = time.time()
        self.preview_time = time.time()

        self.fps_list = []
        self.fps_avg = 0
        self.fps = 0

    def update(self):
        self.current_time = time.time()
        self.sec = self.current_time - self.preview_time
        self.preview_time = self.current_time

        if self.sec > 0:
            fps = round((1 / self.sec), 1)

        else:
            fps = 1

        if len(self.fps_list) < 20:
            self.fps_list.append(fps)
        else:
            del self.fps_list[0]
            self.fps_list.append(fps)

        self.fps = fps

        if len(self.fps_list) > 0:
            self.fps_avg = sum(self.fps_list) / len(self.fps_list)

    def get(self):
        return self.fps_avg
