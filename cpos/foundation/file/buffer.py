# -*- coding: utf-8 -*-
"""
    使用缓冲区的方式来写文件
"""
import threading
import time
from ..system import locker


class BufferFile(object):

    def __init__(self, filename):
        # 向哪个文件中写数据，文件一直打开着，保证文件是UTF8格式的
        self.fb = open(filename, 'ab')
        locker.lock(self.fb, locker.LOCK_EX)
        # 文件名，用于之后的文件重命名
        self.filename = filename
        # 最大缓冲数量
        self.max_buffer_length = 10
        # 最大缓冲时间 秒
        self.max_buffer_time = 30
        # 缓冲开始时间
        self.start_buffer = time.time()
        self.__________FW__________ = []
        self.__________FW__________GUARD = threading.RLock()

    def write(self, msgstr):
        """
            先缓冲文件之后再写
        """
        try:
            self.__________FW__________GUARD.acquire()
            self.__________FW__________.append(msgstr)
        finally:
            self.__________FW__________GUARD.release()

        if time.time() - self.start_buffer >= self.max_buffer_time or len(self.__________FW__________) >= self.max_buffer_length:
            # 满足任一条件，就需要写文件
            self.flush()

    def flush(self):
        """
            将缓冲区的内容写到文件中
        """
        try:
            self.__________FW__________GUARD.acquire()
            for msgstr in self.__________FW__________:
                self.fb.write(msgstr)
            self.fb.flush()
            # 写完文件了，清空缓冲区
            self.__________FW__________ = []
            self.start_buffer = time.time()
        finally:
            self.__________FW__________GUARD.release()

    def close(self):
        try:
            self.flush()
            self.fb.close()
        except:
            pass

    def close_noflush(self):
        """
            进程池中，子进程会copy父进程的状态，对于子进程，需要先关闭父进程维护的缓冲区
        """
        try:
            try:
                self.__________FW__________GUARD.acquire()
                # 清空缓冲区
                self.__________FW__________ = []
                self.start_buffer = time.time()
            finally:
                self.__________FW__________GUARD.release()
            self.fb.close()
        except:
            pass

    def __del__(self):
        """
            销毁前需要写文件
        """
        try:
            if self.fb:
                self.close()
        except:
            pass


def test():
    # 测试时，flush部分需要修改一下“fileobj.write(str(time.time()) + '|' + msgstr)”
    bf = BufferFile(r'F:\Projects_TEMP\aaaaa', 'a')
    cnt = 0
    while True:
        cnt += 1
        print(cnt)
        bf.write(str(cnt)+'\n')
        if cnt > 6:
            time.sleep(5)
        if cnt > 30:
            break

if __name__ == "__main__":
    test()
