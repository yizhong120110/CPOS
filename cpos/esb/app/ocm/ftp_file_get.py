# -*- coding: utf-8 -*-
"""
    从指定的ftp地址上下载文件，在ocm所在的主机上生成临时文件
    获得ocm所在主机上的文件，返回的是文件块
"""
from cpos.esb.basic.config import settings
from cpos.esb.basic.rpc.rpc_ocm import send_buff_to_ocm
from cpos.esb.app.ocm.ocm_file_get import prepare_file
from cpos.esb.basic.resource.logger import logger
from cpos.esb.app.ocm.FTP import FTP
import os
import sys
import time


def ftp_download_file(msgdic ,local_file_root):
    myftp = None
    try:
        ip = msgdic["ip"]
        port = msgdic["port"]
        user = msgdic["user"]
        pwd = msgdic["passwd"]
        path = msgdic["path"]
        pasv = msgdic["pasv"]
        file_name = msgdic["file_name"]
        logger.ods("pasv:%s ,准备从【%s@%s:%s/%s】获取文件：%s"%(pasv ,user ,ip ,port ,path ,file_name) ,lv='info',cat = 'app.ftp_file_get')
        myftp = FTP( ip, port, user, pwd, path, pasv )

        # 下载到本地后的文件
        local_file = os.path.abspath(os.path.join(local_file_root, file_name))
        os.makedirs(os.path.dirname(local_file) , exist_ok = True)

        flag = myftp.download(local_file_root ,file_name, isBin=True)
        if flag == False:
            return None ,"myftp.download error"
        return file_name ,None
    except TimeoutError:
        logger.ods("ftp连接超时，已断开" ,lv='warning',cat = 'app.ftp_file_get')
        return None ,"ftp连接超时，已断开" 
    except:
        exc_msg = str(sys.exc_info())
        logger.ods("ftp下载文件失败:"+exc_msg ,lv='warning',cat = 'app.ftp_file_get')
        return None ,exc_msg
    finally:
        if myftp:
            myftp.close()


# {type:x , message:x , chunk:x, chunk_type:file/buffer/none, file_name:only valid when chunk_type = file , other_paramters....}
def apply_request_on_ocps (comm_message):
    msgdic = comm_message['buff']
    # 根目录，为了复用代码
    local_file_root = os.path.join(settings.RPC_FILE_ROOT ,"get_%s_%s_%s"%(msgdic["ip"] ,msgdic["port"] ,msgdic["user"]) ,time.strftime("%Y%m%d%H%M%S"))
    local_file ,exc_msg = ftp_download_file(msgdic ,local_file_root)
    if local_file is None:
        return {"chunk":None ,"msg":exc_msg}
    # 是否直接返回文件的路径，而非文件的内容
    if msgdic.get("retPath",None) == 'yes':
        res = os.path.join(local_file_root ,local_file)
    else:
        res ,exc_msg = prepare_file(local_file ,local_file_root)
        # 返回值必须是字典的形式
        if res is None:
            return {"chunk":None ,"msg":exc_msg}
    return {"chunk":res ,"msg":"ok"}


def download_by_ftp(ip ,port ,user ,passwd ,path ,file_name ,rpc_timeout=None, pasv=1 ,retPath="no"):
    """
        通过ftp协议到指定的ip地址下载文件
        file_name 文件名，不支持相对路径
        download_by_ftp("46.17.189.236" ,21 ,"oa_manage_sj" ,"oa" ,"/home/oa_manage_sj/src" ,"counter.txt")
    """
    logger.ods("pasv:%s ,准备从【%s@%s:%s/%s】获取文件：%s"%(pasv ,user ,ip ,port ,path ,file_name) ,lv='info',cat = 'app.ftp_file_get')
    content = {"ip":ip ,"port":port ,"user":user ,"passwd":passwd ,"path":path ,"file_name":file_name ,"pasv":pasv ,"retPath":retPath}
    
    # rpc的超时时间，应该是int型的，如果不是，则取用系统默认值5秒
    if isinstance(rpc_timeout ,int) :
        rs = send_buff_to_ocm(content,'ftp_file_get',rpc_timeout)
    else:
        rs = send_buff_to_ocm(content,'ftp_file_get')
    return rs


if __name__=="__main__":
    print(download_by_ftp("46.17.189.231" ,21 ,"sjdev" ,"sjdev" ,"/home/sjdev/tmp" ,"a.py" ,30 ,retPath="no"))
