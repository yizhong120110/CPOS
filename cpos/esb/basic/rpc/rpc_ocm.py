# -*- coding: utf-8 -*-
"""
    启动rpcserver时，会根据启动的protocol，来确定rpc中的exchange名称
"""
from cpos.esb.basic.rpc import rpc
from cpos.esb.basic.config import settings
wqs_ocm = settings.WQS_OCM
wqs_ocm_timeout = settings.WQS_OCM_TIMEOUT
import base64
import json
import copy

from cpos.esb.basic.resource.logger import logger

# supports like ['etc','xxx_type_service','xxxxx']   list would be the names of ICPs. 
#                                                    different ICPs need different WQS_settings respectively.               
# the types demoed above will be append to wqs.queue and binding_keys
def start_ocm_server (protocols = [] ,cb = None ,cp = None):
    wqs_list = []
    for protocol in protocols:
        wqs_list.append({   'exchange'  :   wqs_ocm['exchange'] , 'queue' : wqs_ocm['queue'] +'.'+ protocol , \
                            'binding_key' : wqs_ocm['binding_key'] +'.'+protocol , 'queue_durable':wqs_ocm['queue_durable']})
    return rpc.start_server(cb,cp,wqs_list = wqs_list )


def send_ocm (content,protocol = 'echo',chunk = None,chunk_type = 'none', file_name = 'unamed' ,timeout_interval = wqs_ocm_timeout):
    chunk_new = chunk
    if not (isinstance(chunk_new, bytes) or  \
            isinstance(chunk_new, bytearray) \
            ) and chunk_new is not None:
        #chunk_new = base64.b85encode(chunk).decode('utf-8')
        logger.ods( '[send_ocm] expects chunk parameter in bytes or bytearray'
                    ' or None, but received an unknow type. Ignored.',lv = 'error',
                    cat = 'basic.rpc.rpc_ocm')
    
    content_dict = copy.deepcopy(content) if isinstance(content, dict) else json.loads(content)
    content_dict['chunk'] = chunk_new
    content_dict['chunk_type'] = chunk_type
    content_dict['file_name'] = file_name

    wqs_ocm_with_protocol = copy.deepcopy(wqs_ocm)
    wqs_ocm_with_protocol['queue'] += '.'
    wqs_ocm_with_protocol['queue'] += protocol
    wqs_ocm_with_protocol['binding_key'] += '.'
    wqs_ocm_with_protocol['binding_key'] += protocol

    r = rpc.req( content_dict , wqs_ocm_with_protocol, timeout_interval)
    rm = rpc.sync_rpc([r ])
    if rm.total_responds() != 1:
        return None
    # 直接返回结果字典，不需要再取一次getcontent()
    return rm.succeeded_requests()[0].getrespond().getcontent()


# 向OCM发送消息的部分
def send_buff_to_ocm (content ,protocol ,timeout_interval = wqs_ocm_timeout):
    """
        content 要发送的内容，一个字典
        protocol 发送的目标，OCM的类型名称，启动时指定的
        timeout_interval 反馈超时设置
    """
    # buff才是二次开发者操作的变量，封装一下的目的是为了能够在之后直接透传给动态加载的函数
    return send_ocm({"buff":content} ,protocol=protocol, timeout_interval=timeout_interval)


# 向OCM发送文件的部分
def send_file_to_ocm (chunk ,file_name ,protocol ,timeout_interval = wqs_ocm_timeout):
    """
        chunk 文件内容块，二进制
        file_name 文件名，含相对路径
        protocol 发送的目标，OCM的类型名称，启动时指定的
        timeout_interval 反馈超时设置
    """
    return send_ocm({} ,protocol=protocol ,chunk=chunk ,chunk_type='file' ,file_name=file_name ,timeout_interval=timeout_interval)


if __name__ == '__main__':
    def test_service (x):
        pass
        
    #start_ocm_server(['demo_icp'],test_service)
    send_ocm(   {'type':'echo' , 'message':'this is a outbound message.' , 'extra':'xxxxxxx'}, \
                protocol = 'echo' , chunk = bytes([1,2,3,4,5,6,7,8,9]),  \
                chunk_type = 'file' , file_name = 'test.dat'
            )
