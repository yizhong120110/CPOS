# -*- coding: utf-8 -*-
"""
    将文件块写到ocm所在主机上
    然后通过ftp协议上传到指定ip
"""
from cpos.esb.basic.config import settings
from cpos.esb.basic.rpc.rpc_ocm import send_ocm
from cpos.esb.app.ocm.ocm_file_put import prepare_file
from cpos.esb.basic.resource.logger import logger
from cpos.esb.app.ocm.FTP import FTP
import base64
import os
import time
import sys


def ftp_upload_file(msgdic ,local_file_root):
    myftp = None
    try:
        ip = msgdic["ip"]
        port = msgdic["port"]
        user = msgdic["user"]
        pwd = msgdic["passwd"]
        path = msgdic["path"]
        pasv = msgdic["pasv"]
        file_name = msgdic["file_name"]
        logger.ods("pasv:%s ,准备向【%s@%s:%s/%s】上传文件：%s"%(pasv ,user ,ip ,port ,path ,file_name) ,lv='info',cat = 'app.ftp_file_put')
        myftp = FTP( ip, port, user, pwd, path, pasv )

        # 本地的文件
        local_file = os.path.abspath(os.path.join(local_file_root, file_name))
        flag = myftp.upload(local_file_root ,file_name)
        if flag == False:
            return None ,"myftp.upload error"
        return file_name ,None
    except TimeoutError:
        logger.ods("ftp连接超时，已断开" ,lv='warning',cat = 'app.ftp_file_put')
        return None ,"ftp连接超时，已断开" 
    except:
        exc_msg = str(sys.exc_info())
        logger.ods("ftp上传文件失败:"+exc_msg ,lv='warning',cat = 'app.ftp_file_put')
        return None ,exc_msg
    finally:
        if myftp:
            myftp.close()


# {type:x , message:x , chunk:x, chunk_type:file/buffer/none, file_name:only valid when chunk_type = file , other_paramters....}
def apply_request_on_ocps (comm_message):
    msgdic = comm_message['buff']
    # 根目录，为了复用代码
    local_file_root = os.path.join(settings.RPC_FILE_ROOT ,"put_%s_%s_%s"%(msgdic["ip"] ,msgdic["port"] ,msgdic["user"]) ,time.strftime("%Y%m%d%H%M%S"))
    
    res ,exc_msg = prepare_file(comm_message['chunk'],comm_message['chunk_type'],msgdic['file_name'] ,file_root=local_file_root)
    if not res:
        # 返回值必须是字典的形式
        return {"full_path":res ,"msg":exc_msg}

    # 将文件上传到ftp端
    res ,exc_msg = ftp_upload_file(msgdic ,local_file_root)
    if res:
        return {"full_path":res ,"msg":"ok"}
    return {"full_path":res ,"msg":exc_msg}


def upload_by_ftp(ip ,port ,user ,passwd ,path ,file_name ,chunk ,rpc_timeout=None, pasv=1):
    """
        通过ftp协议到指定的ip地址上传文件
        file_name 文件名
        chunk 文件内容流
    """
    logger.ods("pasv:%s ,准备向【%s@%s:%s/%s】上传文件：%s"%(pasv ,user ,ip ,port ,path ,file_name) ,lv='info',cat = 'app.ftp_file_put')
    content = {"ip":ip ,"port":port ,"user":user ,"passwd":passwd ,"path":path ,"file_name":file_name ,"pasv":pasv}

    # rpc的超时时间，应该是int型的，如果不是，则取用系统默认值5秒
    if isinstance(rpc_timeout ,int) :
        rs = send_ocm({"buff":content} ,protocol="ftp_file_put" ,chunk=chunk ,chunk_type='file' ,timeout_interval=rpc_timeout)
    else:
        rs = send_ocm({"buff":content} ,protocol="ftp_file_put" ,chunk=chunk ,chunk_type='file')
    return rs


if __name__=="__main__":
    print(upload_by_ftp("46.17.189.236" ,21 ,"oa_manage_sj" ,"oa" ,"/home/oa_manage_sj/src" ,"test.txt" ,b"testtestets" ,30))
