# -*- coding: utf-8 -*-
from cpos.esb.basic.rpc.rpc_jr import send_jr_reply
from ops.core.logger import traceback2


def send_jr(content, hostname ,source='qt'):
    # 提供给运维系统的向响应动作队列中存放消息
    content['source'] = source
    try:
        rs = send_jr_reply (content, hostname)
        if rs:
            # 有返回值，即可认为是执行成功了
            return "ok"
        else:
            return "命令执行失败"
    except:
        exc_msg = traceback2.format_exc( show_locals = True )
        return str(exc_msg)


def send_pm(content, hostname ,source='pm'):
    # 提供给管理平台，用于进程管理
    content['source'] = source
    try:
        rs = send_jr_reply (content, hostname ,protocol="pm")
        if rs:
            # 有返回值，即可认为是执行成功了
            return "ok"
        else:
            return "命令执行失败"
    except:
        exc_msg = traceback2.format_exc( show_locals = True )
        return str(exc_msg)


# send_jr 的测试代码
if __name__=="__main__":
    from cpos.esb.basic.resource.functools import get_hostname
    content = { 'param':[r'MD E:\aaatest'] }
    print(send_jr( content, get_hostname() ))
