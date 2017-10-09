# -*- coding: utf-8 -*-

import threading
import socketserver
from ops.core.logger import TransactionLogger, set_tlog_parms
from ops.core.rpc import call_jy_reply

# 用于传递参数到ThreadedTCPRequestHandler.handle中
HANDLEKWD = {"TXBM": "TCR_S", "KIND": "tcr_icp"}

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        tlog = TransactionLogger()
        # rzlsh 是本次日志的流水号，可以将其返回，用于查询日志
        rzlsh = set_tlog_parms(
            tlog,
            HANDLEKWD["KIND"],
            kind=HANDLEKWD["KIND"],
            reload_jyzd="yes")
        try:
            tlog.log_info('TCR 本次通讯的的日志流水号为【%s】' % rzlsh)
            tlog.log_info('TCR 接收到来自【%s】的连接请求' % (repr(self.client_address)))
            # 接收报文
            buf_data = self.request.recv(10000)
            if not buf_data:
                tlog.log_info('TCR 接收到的报文不合法')
            else:
                tlog.log_info('TCR 接收到原始的报文为【%s】' % buf_data)
                tlog.log_info('TCR 接收到的转换后的报文为【%s】' % buf_data.decode('UTF-8'))
                # 调用核心交易
                buf_fk = call_jy_reply(HANDLEKWD['TXBM'], buf_data)
                tlog.log_info('TCR 反馈报文为:【%s】' % buf_fk)
            # 返回报文
            self.request.sendall(buf_fk)
        except:
            raise
            tlog.log_exception('TCR 服务端通讯异常!')
        finally:
            # 一次处理完成，关闭tlog
            tlog.close(rzlsh)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def main(kwd, txbm):
    """
       # kwd 字典
       # k-v来源于界面配置
       # txbm 通讯编码 ,本示例中未使用，仅作占位
    """
    HANDLEKWD.update(kwd)
    if not kwd.get("PORT"):
        raise RuntimeError("通讯参数PORT必须指定")
    socketserver.TCPServer.allow_reuse_address = True
    server = ThreadedTCPServer(
        ("", int(kwd["PORT"])), ThreadedTCPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    # 设置为守护进程
    server_thread.daemon = True
    # 启动线程
    server_thread.start()
    # 启动服务监听
    server.serve_forever()

if __name__ == "__main__":
    main({"PORT": "11111"}, "MSFSPOSS")
