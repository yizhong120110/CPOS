# -*- coding: utf-8 -*-
"""
    将文件块写到ocm所在主机上
"""
from cpos.esb.basic.config import settings
from cpos.esb.basic.rpc.rpc_ocm import send_file_to_ocm
from cpos.esb.basic.resource.logger import logger
import base64
import os
import sys


def prepare_file (chunk,chunk_type,file_name ,file_root=settings.RPC_FILE_ROOT):
    #only process 'file' type chunk. return full_path if its a file , return '' when its a buffer needs to be transfered.
    # raise any possible exception while processing the file.
    try:
        if chunk_type.upper() == 'FILE':
            #logger.ods("ocm中待处理的内容为：\n chunk [%s] \n chunk_type [%s] \n file_name [%s]"%(repr(chunk),repr(chunk_type),repr(file_name)) ,lv='info',cat = 'app.ocm_file_put')
            decoded_chunk = chunk # not need base64.b85decode(chunk)
            # 防止file_name的相对路径从“/”开始
            file_name = file_name.strip('/\\')
            full_path = os.path.abspath(os.path.join(file_root, file_name))
            logger.ods("将要存储的文件绝对路径为：%s"%str(full_path) ,lv='info',cat = 'app.ftp_file_put')

            os.makedirs(os.path.dirname(full_path) , exist_ok = True)
            file_object = open(full_path, 'wb')
            file_object.write(decoded_chunk)
            file_object.close()
            return file_name ,None
        return "" ,None
    except:
        exc_msg = str(sys.exc_info())
        logger.ods("本地文件保存失败:"+exc_msg ,lv='warning',cat = 'app.ftp_file_put')
        return None ,exc_msg


# {type:x , message:x , chunk:x, chunk_type:file/buffer/none, file_name:only valid when chunk_type = file , other_paramters....}
def apply_request_on_ocps (comm_message):
    res ,exc_msg = prepare_file(comm_message['chunk'],comm_message['chunk_type'],comm_message['file_name'])
    # 返回值必须是字典的形式
    return {"full_path":res}


def upload_to_ocm(chunk ,file_name):
    """
        向ocm上上传文件
        chunk 文件内容流
        file_name 文件名，相对路径
    """
    rs = send_file_to_ocm(chunk ,file_name,'ocm_file_put')
    return rs["full_path"] if rs else rs


if __name__=="__main__":
    print(upload_to_ocm(b"this is a test","test.txt"))
