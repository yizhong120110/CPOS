# -*- coding: utf-8 -*-
# 用于OCM监听RMQ
from cpos.esb.basic.rpc.rpc_ocm import start_ocm_server

from cpos.esb.app.ocm.ocm_file_put import upload_to_ocm
# 使用示例：参数1为文件流，参数2为文件名（相对路径，从核心settings.RPC_FILE_ROOT开始）
# upload_to_ocm(open(r"F:\Projects_TEMP\test.pdf",'rb').read() ,'/test/new.pdf')


from cpos.esb.app.ocm.ocm_file_get import download_from_ocm
# 使用示例：文件名（相对路径，从核心settings.RPC_FILE_ROOT开始），获取的是文件内容流
# download_from_ocm('/test/software.zip')


from cpos.esb.app.ocm.ftp_file_put import upload_by_ftp
# 使用示例：参数1为ftpIP，参数2为ftp端口，参数3为ftp用户名，参数4为ftp用户密码，参数5为ftp远程路径，参数6为文件名， 参数7为文件流，参数8为底层通讯超时时间（默认为5s）
# upload_by_ftp( '46.17.189.236', 21, 'uniplat', 'uniplat', '/home/uniplat/tmp', 'test.txt', open('/home/yw/tmp/test.txt','rb').read(), '20' )


from cpos.esb.app.ocm.ftp_file_get import download_by_ftp
# 使用示例：参数1为ftpIP，参数2为ftp端口，参数3为ftp用户名，参数4为ftp用户密码，参数5为ftp远程路径，参数6为文件名，参数7为通讯超时时间（默认为5s），获取的是文件内容流
# download_by_ftp("46.17.189.236" ,21 ,"oa_manage_sj" ,"oa" ,"/home/oa_manage_sj/src" ,"counter.txt" ,30)


# 用于向指定类型的ocm发消息
from cpos.esb.basic.rpc.rpc_ocm import send_buff_to_ocm
def message_to_ocm(senddic,protocol,timeout_interval):
    """
        向OCM发送消息的部分，提供给运维使用
        senddic 交由protocol对应函数处理的字典
        protocol 通讯协议类型名 用于连接RMQ
        使用示例：
        senddic = dict(comtype = 'jnltdsf_comm' ,buf="This is a test.234344444" ,ip='127.0.0.1' ,port='5503',timeout='50')
        print( message_to_ocm(senddic,'ocm_short_tcp') )
    """
    rs = send_buff_to_ocm(senddic,protocol,timeout_interval)
    return rs["rsbuff"] if rs else rs


# 使用方式同系统自带的open一致，仅将文件的根目录指向了settings.RPC_FILE_ROOT
from cpos.esb.app.ocm.rpcfile import fesbopen


from cpos.esb.app.ocm.rpcfile import get_fesb_filename
# 用于将文件的根目录指向了settings.RPC_FILE_ROOT


# 方便使用
from cpos.esb.app.ocm.sftp import SFTP
from cpos.esb.app.ocm.FTP import FTP


from cpos.esb.app.ocm.sftp_utils import sftp_put
# 使用示例：参数1为sftpIP，参数2为sftp端口，参数3为sftp用户名，参数4为sftp用户密码，
# 参数5为sftp远程路径，参数6为文件名，参数7为本地的文件目录位置，获取的是True/False
# sftp_put("46.17.189.233" ,22 ,"sjdev" ,"sjdev" ,"/home/sjdev/tmp" ,"test.txt" ,get_fesb_filename('/'))
from cpos.esb.app.ocm.sftp_utils import sftp_get
# 使用示例：参数1为sftpIP，参数2为sftp端口，参数3为sftp用户名，参数4为sftp用户密码，
# 参数5为sftp远程路径，参数6为文件名，参数7为本地的文件目录位置，参数8为本地保存的文件名，获取的是True/False
# sftp_get("46.17.189.233" ,22 ,"sjdev" ,"sjdev" ,"/home/sjdev/tmp" ,"test.txt" ,get_fesb_filename('/tmp') ,"new.txt")
