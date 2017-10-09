# -*- coding: utf-8 -*-

from ops.core.logger import tlog ,set_tlog_parms
import threading  
import socketserver
from ops.core.rpc import call_jy_reply

class ThreadedTCPRequestHandler( socketserver.BaseRequestHandler ):
    def handle(self):
        # 生成日志流水号，开始写日志
        rzlsh = set_tlog_parms( tlog , 'enc_icp', kind='enc_icp', reload_jyzd='yes' )
        tlog.log_info( 'ENC 本次通讯的的日志流水号为[%s] ' % rzlsh )
        tlog.log_info( '接收到来自【%s】的连接请求' % (repr(self.client_address)) )
        try:
            # 接收报文长度
            buf_len = self.request.recv( 8 )
            tlog.log_info( '接收到的报文长度buf_len:[%s]' % ( buf_len ) )
            # 接收整体报文
            buf_data = self.request.recv( int(buf_len) )
            buf_fk = b''
            if not buf_data:
                tlog.log_info('接收到的报文不合法')
            else:
                tlog.log_info( '接收到的报文为:recv>>>>>>>>>>>>>>:[%s]' % buf_data )
                # 调用FESB交易
                buf_fk = call_jy_reply( 'ENC_S', buf_data )
                tlog.log_info( 'ENC 反馈报文为:buf_fk>>>>>>>>>>>[%s]' % buf_fk )
                # 计算长度
                buf_fk_len = len( buf_fk )
                tlog.log_info( 'ENC 返回报文的长度为【%s】' % buf_fk_len )
                # 组合报文
                buf_fk_enc = str(buf_fk_len).rjust( 8, '0').encode('utf-8') + buf_fk
                tlog.log_info( 'ENC 返回给c端的报文为[%s]' % buf_fk_enc )
            self.request.sendall( buf_fk_enc )
        except: 
            import traceback
            tlog.log_exception( 'ENC 服务端通讯异常:\n%s' % traceback.format_exc() )
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
    main({'PORT':7300},'txbm')
