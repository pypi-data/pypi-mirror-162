import time

class Timer:
    START_TIME = 0
    
    @staticmethod
    def start():
        Timer.START_TIME = time.time()

    @staticmethod
    def end():
        print(" -- %s (s) -- " % round(time.time() - Timer.START_TIME, 2))