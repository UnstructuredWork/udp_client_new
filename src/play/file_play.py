from src.parallel import thread_method

class FilePlay:
    def __init__(self, file_path):
        self.file = file_path

        self.result = None

        self.curr_time = 0
        self.prev_time = 0

    @thread_method
    def run(self):
        self.update()

    def update(self):
        pass
