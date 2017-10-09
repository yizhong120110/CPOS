# -*- coding: utf-8 -*-
"""
    通过RMQ传递交易相关的信息
"""
import copy
from cpos.esb.basic.rpc import rpc
from cpos.esb.basic.config import settings
wqs_transaction = settings.WQS_TRANSACTION
wqs_transaction_java = settings.WQS_TRANSACTION_JAVA
wqs_transaction_timeout = settings.WQS_TRANSACTION_TIMEOUT


def start_trans_with_protocol (protocols = [] ,cb = None ,cp = None):
    """ 处理时间特别长的tp02部分 """
    wqs_list = []
    for protocol in protocols:
        wqs_with_protocol = copy.deepcopy(wqs_transaction)
        wqs_with_protocol['queue'] += '.'+protocol
        wqs_with_protocol['binding_key'] += '.'+protocol
        wqs_list.append(wqs_with_protocol)
    return rpc.start_server(cb,cp,wqs_list = wqs_list )


def send_trans_main (content,timeout_interval = wqs_transaction_timeout ,\
        try_once=False ,reply='yes', wqs_type=wqs_transaction):
    """
        try_once 仅尝试一次，为管理端的发起交易提供
        reply 是否需要返回值，仅"no"不提供返回值
    """
    if not( isinstance(content, dict) or isinstance(content,str) ):
        raise TypeError('send_request expects dict or str')
    r = rpc.req( content , wqs_type, timeout_interval)
    if try_once:
        cp = rpc.gp(pool_size=1 ,connection_attempts=-1)
    else:
        cp = None
    if reply == 'no':
        rm = rpc.noreply_rpc([r ] ,cp=cp)
    else:
        rm = rpc.sync_rpc([r ] ,cp=cp)
    if rm.total_responds() != 1:
        return None
    return rm.succeeded_requests()[0].getrespond().getcontent()


def send_trans_with_protocol (content,timeout_interval = wqs_transaction_timeout ,try_once=False ,reply='yes' ,protocol=""):
    """ 处理时间特别长的tp02部分 """
    wqs_with_protocol = copy.deepcopy(wqs_transaction)
    wqs_with_protocol['queue'] += '.'+protocol
    wqs_with_protocol['binding_key'] += '.'+protocol
    return send_trans_main(content, timeout_interval ,try_once ,reply, wqs_type=wqs_with_protocol)


def send_trans_java (content,timeout_interval = wqs_transaction_timeout ,wqs_type=wqs_transaction_java):
    if not( isinstance(content, bytes) ):
        raise TypeError('send_request expects bytes')
    r = rpc.req( content , wqs_type, timeout_interval)
#    cp = rpc.gp(pool_size=1 ,connection_attempts=-1)
    cp = None
    rm = rpc.sync_rpc([r ] ,cp=cp)
    if rm.total_responds() != 1:
        return None
    return rm.succeeded_requests()[0].getrespond().getcontent()


if __name__ == '__main__':
    print(send_trans_main({'kkk':'vvv'} ,try_once=True))
    send_trans_main({'kkk':'vvv'})
