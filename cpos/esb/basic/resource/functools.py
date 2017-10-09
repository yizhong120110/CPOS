# -*- coding: utf-8 -*-
from cpos.foundation.substrate import traceback2
from cpos.foundation.substrate.utils.functools import kill_process
import uuid
import socket
import os


def get_uuid():
    return uuid.uuid4().hex

def get_hostname():
    # 这里获取的是/etc/sysconfig/network文件中HOSTNAME的值
    return socket.gethostname()
#    return socket.gethostname()+'_'+str(os.environ['USER'])
