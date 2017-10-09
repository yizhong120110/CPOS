# -*- coding: utf-8 -*-
import time


class TimeoutInterval(object):

    def __init__(self, timeout_interval=-1):
        self.interval = timeout_interval
        self.first_step = 0
        self.time_delta = 0

    def step(self, sleep=None):
        self.first_step = time.time() if self.first_step == 0 else self.first_step
        if sleep:
            time.sleep(sleep)
        self.time_delta = time.time() - self.first_step
        if self.time_delta >= self.interval and self.interval != -1:
            return None
        else:
            return self.time_delta


# test
#
gb = ''


def buffered_func(ti, buffer):
    global gb
    gb += buffer
    if not ti.step():  # timeout
        print('buffered_func called, buffer is ' + str(gb))
        gb = ''
        return True
    print('buffered_func called, but not shows effect.')
    return False


if __name__ == "__main__":
    # 2mods supports.

    # 1   clock, do a job in every 1 second , and timeout in 5 seconds.
    ti = TimeoutInterval(5)
    while ti.step(1):
        print('not yet.' + str(ti.time_delta))
    print('time out!')

    # 2   reentry a function many times .
    ti = TimeoutInterval(5)
    while True:
        time.sleep(1)
        if(buffered_func(ti, '1')):
            ti = TimeoutInterval(5)  # reset timer
