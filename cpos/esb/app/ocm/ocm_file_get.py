# -*- coding: utf-8 -*-
"""
    获得ocm所在主机上的文件，返回的是文件块
"""
from cpos.esb.basic.config import settings
from cpos.esb.basic.rpc.rpc_ocm import send_buff_to_ocm
from cpos.esb.basic.resource.logger import logger
import base64
import os
import sys


def prepare_file (file_name ,file_root=settings.RPC_FILE_ROOT ,isbase64=None):
    # 防止file_name的相对路径从“/”开始
    file_name = file_name.strip('/\\')
    full_path = os.path.abspath(os.path.join(file_root, file_name))
    logger.ods("要获得的文件绝对路径为：%s"%str(full_path) ,lv='info',cat = 'app.ocm_file_get')
    try:
        chunk = open(full_path, 'rb').read()
        if isbase64 is not None and isinstance(chunk, bytes):
            chunk = base64.b85encode(chunk)
        return chunk ,None
    except FileNotFoundError:
        logger.ods("未找到指定的文件【%s】"%(full_path) ,lv='warning',cat = 'app.ocm_file_get')
        return None ,"未找到指定的文件【%s】"%(full_path)
    except:
        logger.oes("读取文件内容失败：" ,lv='warning',cat = 'app.ocm_file_get')
        exc_msg = str(sys.exc_info())
        return None ,str(exc_msg)


# {type:x , message:x , chunk:x, chunk_type:file/buffer/none, file_name:only valid when chunk_type = file , other_paramters....}
def apply_request_on_ocps (comm_message):
    res ,exc_msg = prepare_file(**comm_message['buff'])
    logger.ods("apply_request_on_ocps end" ,lv='info',cat = 'app.ocm_file_get')
    # 返回值必须是字典的形式
    return {"chunk":res}


def download_from_ocm(file_name ,isbase64=None):
    """
        从ocm上下载文件
        file_name 文件名，相对路径
    """
    logger.ods("准备获取文件,isbase64[%s]：%s"%(isbase64 ,str(file_name)) ,lv='info',cat = 'app.ocm_file_get')
    d = dict(file_name=file_name)
    if isbase64 is not None:
        d["isbase64"] = isbase64
    rs = send_buff_to_ocm(d ,'ocm_file_get')
    logger.ods("download_from_ocm end" ,lv='info',cat = 'app.ocm_file_get')
    if not rs:
        return rs
    try:
        if isbase64 is not None:
            return base64.b85decode(rs["chunk"])
    except:
        logger.oes("base64 decode：" ,lv='warning',cat = 'app.download_from_ocm')
    return rs["chunk"]


if __name__=="__main__":
    print(download_from_ocm('/FILESDIR/1999999961070001_9999999961070005_10670211.zip'))
