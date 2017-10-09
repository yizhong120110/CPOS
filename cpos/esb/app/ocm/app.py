# -*- coding: utf-8 -*-
"""
    TCP短连接方式
    监听RMQ，根据获得的消息，决定调用哪个三方通讯的py文件
    仅传输报文
    python34 app.py -p 10010 -T shorttcp -t 3 -i 34 -w 30 ocm_file_get | ocm_file_put | ftp_file_get | ftp_file_put

    if __name__ == '__main__':
        import sys
        protocols = ['echo'] # for test
        if len(sys.argv) > 1:
            protocols = []

        for i in range(1, len(sys.argv)):
            protocols.append (sys.argv[i] )

        app = OCM(protocols)
        app.run()
    这段示例代码中，echo标明了一种类型，send_ocm(senddic,'echo')中需要对应上
"""
try:
    from . import loader
except:
    import loader
from cpos.esb.basic.application.app_rpclog import env_get ,env_set ,env_clone
from cpos.esb.basic.application.app_ctrle_rpclog import RpclogEApp ,get_shell_args
from cpos.esb.basic.resource.logger import logger
import cpos.esb.basic.rpc.rpc_ocm as rocm


# 获得启动参数
options ,args = get_shell_args()
ocpsname = args[-1]
# 仅仅是支持几个
if ocpsname in ("ocm_file_get","ocm_file_put","ftp_file_get","ftp_file_put"):
    exec("from %s import apply_request_on_ocps"%ocpsname)
else:
    raise RuntimeError("仅支持参数启动【ocm_file_get、ocm_file_put、ftp_file_get、ftp_file_put】")


def service (received):
    # 这里不能够输出日志，有可能存在文件，输出文件内容时会很大
    logger.ods("收到一条消息，准备处理" ,lv='info',cat = 'app.ocm_file')
    logger.ods(str(received.getcontent()) ,lv='dev',cat = 'app.ocm_file')
    return apply_request_on_ocps(received.getcontent()), env_get('keep_running',True)


def working_callback(msgload):
    """
        进程中工作线程的回调函数
    """
    try:
        rocm.start_ocm_server([ocpsname] ,service)
        logger.ods("working_callback处理结束" ,lv='info',cat = 'app.ocm_file')
    except:
        logger.oes("working_callback处理出现异常" ,lv='error',cat = 'app.ocm_file')
    return True


# 启动之初就激活E的工作线程
RpclogEApp(working_callback=working_callback,appname=ocpsname,startwork=True).run()

