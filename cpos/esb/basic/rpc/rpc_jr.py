# -*- coding: utf-8 -*-
"""
    原定进程管理是响应动作的一部分，由于单独实现的PM的管理方式，将其从JR中拆分出来
    接着使用JR的名字，也是可以的
"""
from cpos.esb.basic.resource.functools import get_hostname
from cpos.esb.basic.rpc import rpc
from cpos.esb.basic.config import settings
import copy
wqs_jr_timeout = settings.WQS_JR_TIMEOUT
wqs_jr = settings.WQS_JR


def get_local_wqsjr(wqsjr,hostname=None):
    """
        # jr是要进行本地信息监控的，每个jr进程都应该有自己的binding_key
    """
    if hostname is None:
        hostname = get_hostname() 
    wqsjr["binding_key"] += '.'+hostname
    # 在start_server时就会将binding_key和queue绑定
    wqsjr["queue"] += '.'+hostname
    return wqsjr


def start_jr_server (protocols = [] ,cb = None ,cp = None):
    wqs_list = []
    for protocol in protocols:
        wqs_jr_with_protocol = copy.deepcopy(wqs_jr)
        wqs_jr_with_protocol['queue'] += '.'+protocol
        wqs_jr_with_protocol['binding_key'] += '.'+protocol
        wqs_list.append(get_local_wqsjr(wqs_jr_with_protocol))
    return rpc.start_server(cb,cp,wqs_list = wqs_list )


def send_jr_reply (content, hostname, timeout_interval = wqs_jr_timeout ,protocol="jr" ):
    if not( isinstance(content, dict) or isinstance(content,str) ):
        raise TypeError('send_request expects dict or str')
    wqs_jr_with_protocol = copy.deepcopy(wqs_jr)
    wqs_jr_with_protocol['queue'] += '.'+protocol
    wqs_jr_with_protocol['binding_key'] += '.'+protocol
    r = rpc.req( content , get_local_wqsjr(wqs_jr_with_protocol ,hostname), timeout_interval)
    rm = rpc.sync_rpc([r ])
    if rm.total_responds() != 1:
        return None
    return rm.succeeded_requests()[0].getrespond().getcontent()

def send_jr_noreply (content, hostname, timeout_interval = wqs_jr_timeout ,protocol="jr" ):
    if not( isinstance(content, dict) or isinstance(content,str) ):
        raise TypeError('send_request expects dict or str')
    wqs_jr_with_protocol = copy.deepcopy(wqs_jr)
    wqs_jr_with_protocol['queue'] += '.'+protocol
    wqs_jr_with_protocol['binding_key'] += '.'+protocol
    r = rpc.req( content , get_local_wqsjr(wqs_jr_with_protocol ,hostname), timeout_interval)
    rpc.noreply_rpc([r ])



if __name__ == '__main__':
    # 进程测试
    # send_jr({'rwid':'001'})
    # shell 文件测试
    #send_jr({'rwid':'002'})
    # 数据分析任务测试
    #send_jr({'rwid':'003'})
    # 交易
    #send_jr({'rwid':'004'})
    # 业务处理_py文件
    #send_jr({'rwid':'005'})
    # 业务处理_内存函数
    from cpos.esb.basic.resource.logger import *
    send_jr_noreply({'rwid':'62f9a4c4d13b4a18b3a65e6542918111','source':'jy'},get_hostname())
    send_jr_noreply({'rwid':'62f9a4c4d13b4a18b3a65e6542918c3f','source':'shell'},get_hostname())
    send_jr_noreply({'rwid':'62f9a4c4d13b4a18b3a65e6542918222','source':'jcgl'},get_hostname())
