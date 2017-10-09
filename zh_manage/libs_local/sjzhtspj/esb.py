# -*- coding: utf-8 -*-
"""
    调用核心函数模块
"""

from ops.core.nosql import memcache_data_del
from ops.core.rpc import send_jr
from ops.core.rpc import transaction_test
from ops.core.nosql import readlog
from ops.core.rpc import call_jy_reply
from ops.core.rdb_jr import get_lsh2con
from ops.core.rpc import send_pm
from ops.core.rpc import sftp_put
from ops.trans.utils import call_jy_asy

import os
try:
    guname = os.uname().sysname.lower()
    if guname.find('linux') != -1 or guname.find('darwin') != -1:
        import signal
        signal.signal(signal.SIGCHLD,signal.SIG_DFL) 
except:
    pass