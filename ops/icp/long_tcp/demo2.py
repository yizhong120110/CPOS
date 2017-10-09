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
    5、多线程处理方式
"""
from ops.core.logger import tlog ,set_tlog_parms
import threading  
import socketserver
from ops.core.rpc import call_jy_reply

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):  
    def handle(self):
        # rzlsh 是本次日志的流水号，可以将其返回，用于查询日志
        rzlsh = set_tlog_parms(tlog ,"icp_demo2" ,kind="icp_demo2",reload_jyzd="yes")
        try:
            tlog.log_info("本次通讯的的日志流水号为[%s] "%rzlsh)
            tlog.log_info('接收到来自%s的连接请求'%(repr(self.client_address)))
            while True:
                # 接收报文
                buf_data = self.request.recv(10000)
                buf_fk = b''
                if not buf_data:
                    tlog.log_info('接收到的报文不合法')
                elif buf_data == b"MSFS_TC_CHECK":
                    buf_fk = b'MSFS_TC_CHECK_OK'
                else:
                    tlog.log_info( '接收到的报文为:[%s]' % buf_data )
                    # 调用核心交易
                    buf_fk = call_jy_reply(txbm,buf_data)
                    tlog.log_info("反馈报文为:[%s]"%buf_fk)
                # 返回报文
                self.request.sendall( buf_fk )
        except: 
            tlog.log_exception("服务端通讯异常:")
        finally:
            # 一次处理完成，关闭tlog
            tlog.close(rzlsh)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):  
    pass  

def main( kwd, txbm ):
    """
       # kwd 字典
       # k-v来源于界面配置
       # txbm 通讯编码
    """
    socketserver.TCPServer.allow_reuse_address = True  
    server = ThreadedTCPServer(('' ,int(kwd["PORT"])), ThreadedTCPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)  
    # 设置为守护进程
    server_thread.daemon = True
    # 启动线程
    server_thread.start()  
    # 启动服务监听
    server.serve_forever()

if __name__ == "__main__":
    main({'PORT':'11111'} ,'MSFSPOSS')
