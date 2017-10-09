# -*- coding: utf-8 -*-
import time


class Interval(object):

    """
        间隔运行任务，通过sleep实现
        调用方式：Interval().run(执行任务的间隔时间 ,是否停止运行)
            if __name__=="__main__":
                print(time.time())
                keep_running = True
                count = 0
                while interval.run(0.5 ,keep_running):
                    print(count,time.time())
                    count += 1
                    if count > 8:
                        keep_running = False
                print(time.time())
    """

    def __init__(self):
        # 睡眠时间
        self.tick_time = 1
        # 间隔多久工作一次
        self.interval_time = None

    def set_interval(self, interval_time):
        if isinstance(interval_time, float) or isinstance(interval_time, int):
            self.interval_time = interval_time
        else:
            raise RuntimeError("interval_time必须是int或者float类型")

    def on_ticks(self):
        # 每次的睡眠时间，默认等于间隔时间
        # 当最后一次的时候，应该用当前时间减掉起始时间
        sleep_time = min(self.interval_time, self.tick_time)
        time.sleep(sleep_time)
        self.interval_time -= sleep_time

    def run(self, interval_time, keep_running):
        self.set_interval(interval_time)
        # 记录启动时间
        if keep_running == False:
            return False
        while True:
            self.on_ticks()
            if 0 >= self.interval_time:
                return True

interval = Interval()

if __name__ == "__main__":
    print(time.time())
    keep_running = True
    count = 0
    while interval.run(0.5, keep_running):
        print(count, time.time())
        count += 1
        if count > 8:
            keep_running = False
    print(time.time())
