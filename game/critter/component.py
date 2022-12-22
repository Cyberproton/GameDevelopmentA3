import time


class FlyTime:
    def __init__(self):
        self.start = time.time()

    def get_elapsed_time(self):
        return time.time() - self.start
