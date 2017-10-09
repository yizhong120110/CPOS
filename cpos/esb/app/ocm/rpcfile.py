# -*- coding: utf-8 -*-
"""
    将stfp的文件上传、下载操作进行封装
"""
from cpos.esb.basic.config import settings
import os


def get_fesb_filename(file_name):
    # 防止file_name的相对路径从“/”开始
    file_name = file_name.strip('/\\')
    return os.path.abspath(os.path.join(settings.RPC_FILE_ROOT, file_name))


def fesbopen(file_name ,**kwd):
    """
        将文件操作函数做封装，只能写到固定的目录下
        fesbopen("/test",mode='ab').write("想静静".encode('utf8'))
        fesbopen("/test",mode='rb').read()
    """
    try:
        full_path = get_fesb_filename(file_name)
        os.makedirs(os.path.dirname(full_path) , exist_ok = True)
        file_object = open(full_path, **kwd)
        return file_object
    except:
        return None
