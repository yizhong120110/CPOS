# -*- coding: utf-8 -*-
"""
    在进程中加载后，可以忽略子进程的运行状态
    避免出现[python34] <defunct>
"""
import os
import signal
from .logger import logger


def signal_func():
    try:
        guname = os.uname().sysname.lower()
        if guname.find('linux') != -1 or guname.find('darwin') != -1:
            logger.ods('Linux or MacOS detected, set signal(SIGCHLD, SIG_IGN) to avoid zombie processes.', lv='info', cat='signal.signal')
            signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    except:
        pass
