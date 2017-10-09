# -*- coding: utf-8 -*-
import threading
import copy
import time
from .env import *
from ..substrate.interfaces import *
from ..substrate.utils.logger import logger


class Application(Monitored):

    def __init__(self):
        self.procs = {}
        self.threads = []

    def on_start(self):
        logger.ods( 'App start!', lv='info', cat='foundation.application')

    def on_exit(self):
        logger.ods( 'APP exit!', lv='info', cat='foundation.application')

    def register_thread(self, name, proc):
        logger.ods( 'Register thread [%s] to the application.' % (name), lv='info', cat='foundation.application')
        self.procs[name] = self.safe_thread(proc)

    def start_procs(self):
        pps = self.procs.items()
        for p in pps:
            logger.ods( 'Starting thread [%s] in the application.' % (p[0]), lv='info', cat='foundation.application')
            p = threading.Thread(target=p[1], name=p[0])
            self.threads.append(p)
            p.start()

    def wait_procs(self):
        for t in self.threads:
            t.join()

    def run(self):
        self.on_start()
        self.start_procs()
        self.wait_procs()
        self.on_exit()

    def safe_thread(self, callback_func):
        """ 用于保证线程会一直存活,不会意外中断 """
        def _call():
            rs = False
            while rs != True:
                rs = callback_func()
        return _call
