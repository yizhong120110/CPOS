# -*- coding: utf-8 -*-
"""
    单独将main函数拆分到一个py文件中，是为了能够利用__name__ == '__main__'进行测试
    使用说明：
    1、在通讯管理中新增配置
        gl_txgl.txwjmc指向main函数所在的py
    2、进程管理中新增配置
        gl_jcxxpz.qdml指向固定的文件ops/core/app_icp.py的绝对路径
        要求 gl_jcxxpz.jcmc = gl_txgl.bm
    3、TCP同步半双工长连接
    4、含心跳处理，建立一次连接使用一个日志
"""
from ops.core.logger import tlog ,set_tlog_parms
import socket
from ops.core.rpc import call_jy_reply

def main( kwd, txbm ):
    """
       # kwd 字典
       # k-v来源于界面配置
       # txbm 通讯编码
    """
    # 生成tcp服务器的套接字
    server = socket.socket(socket.AF_INET ,socket.SOCK_STREAM)
    server.bind( ('' ,int(kwd["PORT"])) )
    server.listen(10)
    while True:
        rzlsh = None
        client = None
        try:
            # rzlsh 是本次日志的流水号，可以将其返回，用于查询日志
            rzlsh = set_tlog_parms(tlog ,"icp_long_demo" ,kind="icp_long_demo",reload_jyzd="yes")
            tlog.log_info( "waiting for connection..." )
            # 等待连接（被动等待），阻塞式的 
            client, ip = server.accept()
            tlog.log_info("本次通讯的的日志流水号为[%s] "%rzlsh)
            tlog.log_info( "...connected from: %s" %(str(ip)) )
            while True:
                # 接收报文
                buf_data = client.recv(10000)
                buf_fk = b''
                if not buf_data:
                    tlog.log_info( '接收到的报文不合法，断开连接' )
                    break
                elif buf_data == b"MSFS_TC_CHECK":
                    buf_fk = b'MSFS_TC_CHECK_OK'
                else:
                    tlog.log_info( '接收到的报文为:[%s]' % buf_data )
                    # 调用核心交易
                    buf_fk = call_jy_reply(txbm,buf_data)
                    tlog.log_info("反馈报文为:[%s]"%buf_fk)
                # 返回报文
                client.sendall( buf_fk )
        except: 
            tlog.log_exception( "服务端异常:")
        finally:
            if client:client.close()
            # 一次链接完成，关闭tlog
            if rzlsh:tlog.close(rzlsh)


if __name__ == '__main__':
    print(main({'PORT':'11111'} ,'ZDFSSVR'))
