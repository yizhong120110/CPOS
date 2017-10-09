# -*- coding: utf-8 -*-
"""
    单独将main函数拆分到一个py文件中，是为了能够利用__name__ == "__main__"进行测试
    使用说明：
    1、在通讯管理中新增配置
        gl_txgl.txwjmc指向main函数所在的py
    2、进程管理中新增配置
        gl_jcxxpz.qdml指向固定的文件ops/core/app_icp.py的绝对路径
        要求 gl_jcxxpz.jcmc = gl_txgl.bm
    3、多线程处理方式
    配置方法：
        ◆开发系统--通讯管理--新增通讯服务端
            通讯编码：自定义
            通讯名称：自定义
            通讯类型：本文件在ops/icp/short_tcp目录下，需要选择“tcp短连接”，两者存在对应关系
            通讯文件名称：在列表中选择本文件
            超时时间：不在本文件中使用，有其他作用
        ◆开发系统--通讯管理--配置后新增一条记录，在详细信息中编辑
            通讯参数设置，新增记录：
                下面的main函数的kwd参数提供了配置记录的字典
                参数代码：PORT
                参数值：端口号，在本文件中使用，用于监听端口
            交易码解出函数，用于该通讯节点的交易码解出，示例如下：
                jyzd.SYS_JYM = jyzd.SYS_JSDDBW[4:20].strip().decode("utf8")
        ◆维护系统--主机监控中的某个主机详细信息--进程配置管理
            新增记录，用于通讯进程自动启动：
                进程名称：要求与上面“开发系统--通讯管理--新增通讯服务端”中定义的“通讯编码”一致
                启动命令：该文件要求固定填写 /home/sjdev/src/ops/core/app_icp.py
                启动类型：自定义，用于查看命令中识别进程
                查看命令：ps -ef|grep 启动类型
    多个通讯服务端共用本文件的设置方式
        ◆增加通讯服务端时，上面的配置方法不变
        ◆在“开发系统--通讯管理--通讯详细信息”中新增通讯参数
            参数代码：TXBM
            参数值：通讯编码，用于报文的解交易码使用
            参数代码：KIND
            参数值：通讯日志类型，在“通讯日志查看”功能中作为“通讯对象”使用
    进行请求处理的流量控制
        ◆在上面的配置基础上继续扩展
        ◆在“开发系统--通讯管理--通讯详细信息”中新增通讯参数
            参数代码：形如IP_127_0_0_1 ,为请求方的IP地址
            参数值：最大允许使用的并发量，没有配置参数时，请求方默认最大并发量为0
"""
import threading
import socketserver
from ops.core.logger import TransactionLogger, set_tlog_parms
from ops.core.rpc import call_jy_reply

# 用于传递参数到ThreadedTCPRequestHandler.handle中
HANDLEKWD = {"TXBM": "ZDFSSVR", "KIND": "icp_demo3"}


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        tlog = TransactionLogger()
        # rzlsh 是本次日志的流水号，可以将其返回，用于查询日志
        rzlsh = set_tlog_parms(
            tlog,
            HANDLEKWD["KIND"],
            kind=HANDLEKWD["KIND"],
            reload_jyzd="yes")
        reqs = []
        thread_name = "%s" % threading.current_thread().getName()
        try:
            tlog.log_info("本次通讯的的日志流水号为[%s] " % rzlsh)
            client_ip = ("IP_%s" % (self.client_address[0])).replace(".", "_")
            reqsmax = int(HANDLEKWD.get(client_ip, "0"))
            reqs = HANDLEKWD["%s_reqs" % client_ip]
            tlog.log_info("接收到来自%s的连接请求, 最大连接数为%s，已用%s" %
                          (repr(self.client_address), reqsmax, len(reqs)))
            if len(reqs) > reqsmax:
                buf_fk = b"connect no free"
            else:
                reqs.append(thread_name)

                # 接收报文
                buf_data = self.request.recv(10000)
                buf_fk = b""
                if not buf_data:
                    tlog.log_info("接收到的报文不合法")
                elif buf_data == b"MSFS_TC_CHECK":
                    buf_fk = b"MSFS_TC_CHECK_OK"
                else:
                    tlog.log_info("接收到的报文为:[%s]" % buf_data)
                    # 调用核心交易
                    buf_fk = call_jy_reply(HANDLEKWD["TXBM"], buf_data)
            tlog.log_info("反馈报文为:[%s]" % buf_fk)
            # 返回报文
            self.request.sendall(buf_fk)
        except:
            tlog.log_exception("服务端通讯异常:")
        finally:
            if thread_name in reqs:
                reqs.remove(thread_name)
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
    for kk in list(HANDLEKWD.keys()):
        if kk.startswith("IP_"):
            HANDLEKWD["%s_reqs" % kk] = []
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
