# -*- coding: utf-8 -*-
"""
Descriptions
"""
from cpos.foundation.rpc.server import *
from cpos.foundation.rpc.client import *
from cpos.foundation.application.env import env_get
from cpos.esb.basic.resource.logger import logger
from cpos.esb.basic.config import settings
mqs_connection_parameter = settings.MQS_CONNECTION_PARAMETER
mqs_credential_descriptor = settings.MQS_CREDENTIAL_DESCRIPTOR
mqs_default_pool_size = settings.MQS_DEFAULT_POOL_SIZE

import time

__________GP__________ = None
#global_connection_pool
def gp (connection_parameter = None,credential_descriptor = None,pool_size = 0,connection_attempts=None):
    '''产生一个全局的ConnectionPool对象.
        
        如果不指定参数, 则使用config中
        mqs_connection_parameter 
        mqs_credential_descriptor 
        mqs_default_pool_size 
        这三个配置项的值
    '''
    global __________GP__________
    if __________GP__________ is not None:
        return __________GP__________
    
    if connection_parameter == None:
        connection_parameter = mqs_connection_parameter
    if credential_descriptor == None:
        credential_descriptor = mqs_credential_descriptor
    if pool_size == 0:
        pool_size = mqs_default_pool_size
    if connection_attempts == None:
        connection_attempts = connection_parameter['connection_attempts']
    cp = build_connection_parameter(connection_parameter['host'],connection_parameter['port'],
                                    connection_parameter['socket_timeout'],connection_attempts,
                                    mqs_credential_descriptor['user_name'],mqs_credential_descriptor['pass_word'])

    __________GP__________ = ConnectionPool(cp,pool_size)
    return __________GP__________


def req(content = {},wqs = None ,timeout_time = -1):
    '''构建request对象.
            
        Args:            
            content [dict] 要发送的数据.将会被序列化成为json发送到消息队列上.
            timeout_time [int]  等待返回消息的时间, 在使用需要等待返回的Client对象发送报文时,必须指定.
    '''
    if wqs == None:
        raise SJRPCExceptionBadCall('Calling [build_request()] is failed. WQS is acquired.')
    req = Request(content,wqs['exchange'],wqs['binding_key'],timeout_time)
    return req


def get_wqs_by_requests(requests):
    rs_requests = []
    for req in requests:
        wqs = {}
        wqs['exchange'] = req.getexchange()
        wqs['routing_key'] = req.get_routing_key()
        wqs['timeout_time'] = req.get_timeout_time()
        rs_requests.append(wqs)
    return rs_requests


def sync_rpc (requests = [],cp = None):
    logger.ods( 'requests: %s'%(get_wqs_by_requests(requests)),lv = 'info',cat = 'rpc.sync_rpc')
    cp = cp if cp else gp()
    client = SyncClient(cp)
    client.bind_requests(requests)
    client.rpc()
    return RequestManager(requests)
    

def async_rpc (requests = [],cp = None):
    logger.ods( 'requests: %s'%(get_wqs_by_requests(requests)),lv = 'info',cat = 'rpc.async_rpc')
    cp = cp if cp else gp()
    client = AsyncClient(cp)
    client.bind_requests(requests)
    client.rpc()
    return RequestManager(requests)

def noreply_rpc (requests = [],cp = None):
    logger.ods( 'requests: %s'%(get_wqs_by_requests(requests)),lv = 'info',cat = 'rpc.noreply_rpc')
    cp = cp if cp else gp()
    client = NoreplyClient(cp)
    client.bind_requests(requests)
    client.rpc()
    return RequestManager(requests)
    

def start_server_default (cb = None ,cp = None,wqs_list = [] ):
    cp = cp if cp else gp()
    server = PreConfServer(cp,wqs_list)
    while server.keep_running:
        server.run(cb)
        time.sleep(0 if server.keep_running else 2)


class EsbAppRpcServer(PreConfServer):
    def on_ticks (self):
        """
            这里是为了能够通过env停止rpcserver
        """
        if env_get("keep_running",True) == False:
            return False
        super(EsbAppRpcServer,self).on_ticks()

def start_server (cb = None ,cp = None,wqs_list = [] ):
    logger.ods( '将要启动的监听列表为: %s'%(wqs_list),lv = 'info',cat = 'rpc.start_server')
    cp = cp if cp else gp()
    server = EsbAppRpcServer(cp,wqs_list)
    while server.keep_running:
        server.run(cb)
        time.sleep(0 if server.keep_running else 2)


if __name__ == '__main__':
    pass
    #gp().spawn_connections(10)
    #while True:
    #    r = req( {'key':'value'} , wqs_transaction, 2)
    #    rm = async_rpc([r ])
    #    print ('total responds : ' + str(rm.total_responds()) )
