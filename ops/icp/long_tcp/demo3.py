# -*- coding: utf-8 -*-
"""
    单独将main函数拆分到一个py文件中，是为了能够利用__name__ == '__main__'进行测试
    使用说明：
    1、在通讯管理中新增配置
        gl_txgl.txwjmc指向main函数所在的py
    2、进程管理中新增配置
        gl_jcxxpz.qdml指向固定的文件ops/core/app_asynlongtcp.py的绝对路径
        要求 gl_jcxxpz.jcmc = gl_txgl.bm
    3、TCP异步全双工长连接
    4、含心跳处理，建立一次连接使用一个日志
    
    特别注意：通讯文件不可以选择一样的文件：
                目前程序设计是以“通讯文件名”为标识 处理通讯请求。
                所以如果不同的客户端通讯配置一样的通讯文件，
                则启动的通讯进程可以处理非进程对应的通讯请求（
                举例：客户端通讯A  配置通讯文件 demo.py  启动进程 A1
                    客户端通讯B  配置通讯文件 demo.py  启动进程 B1
                    A 发起通讯请求 可以被 A1或B1 处理，正确应该只能是由 A1处理
                    B 发起通讯请求 可以被 A1或B1 处理，正确应该只能是有 B1处理 ）
                得出结论是：通讯文件不可以选择一样的文件。
        解决通讯文件可以选择重复文件问题：
            1.ops.trans.node.py : message_to_ocm(senddic,jyzd.TXWJMC,int(jyzd.TIMEOUT)+5)
                                  将“jyzd.TXWJMC”改为“jyzd.TXBM”(通讯编码)
            2.ops.core.app_ocm.py: start_ocm_server([txxxdic['txwjmc']] ,self.service)
                                  将“txxxdic['txwjmc']”改为“txxxdic['bm']”
            3.ops.ocm.通讯类型.xxxxx_app.py: ocpsname = 'xxxxxx_app'
                                  将“xxxxxx_app” 改为“通讯对应的通讯编码”
"""
from ops.core.logger import tlog ,set_tlog_parms
from ops.core.rpc import call_jy_noreply
import socket
import select
import pickle


def main( kwd, txbm, backend_name ):
    """
       # kwd 字典
       # k-v来源于界面配置 ,IP、PORT、BUF、TIMEOUT、FILENAME
       # txbm 通讯编码
       # backend_name 交易处理完成后返回时message_to_ocm使用的名称
    """
#    print( "main(%s)"%str((kwd, txbm, backend_name)) )
    # 生成tcp服务器的套接字
    server = socket.socket(socket.AF_INET ,socket.SOCK_STREAM)
    server.bind( ('' ,int(kwd["PORT"])) )
    server.listen(10)

    # 长连接，用于接收另一个线程转发的RMQ消息
    resvmsg = socket.socket(socket.AF_INET ,socket.SOCK_STREAM)
    resvmsg.bind( ('' ,int(kwd["PORT_SHORT"])) )
    resvmsg.listen(10)

    # 要先建立与另一个线程的连接，才能用于监听三方 
    ownclient, ip2 = resvmsg.accept()
    
    # inputlist 是一个列表，初始有欢迎套接字以及标准输入  
    inputlist = [server, resvmsg ,ownclient]
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
            # 将服务套接字加入到input列表中
            inputlist.append(client)  
            while True:
                isEnd = 'NO'
                try:
                    # 从input中选择，轮流处理client的请求连接（server），client发送来的消息(client)，及服务器端的发送消息(stdin)  
                    readyInput,readyOutput,readyException = select.select(inputlist,[],[])
                    for indata in readyInput:
                        # 处理client发送来的消息
                        if indata==client:
                            # 接收报文
                            buf_data = client.recv(10000)
                            buf_fk = b''
                            if not buf_data or buf_data == b'88':
                                tlog.log_info( '客户端主动结束' )
                                isEnd = "YES"
                                break
                            elif buf_data == b"MSFS_TC_CHECK":
                                buf_fk = b'MSFS_TC_CHECK_OK'
                            else:
                                tlog.log_info( '接收到的报文为:[%s]' % buf_data )
                                # 调用核心交易，异步处理，无需返回值
                                call_jy_noreply(txbm, pickle.dumps({"BUF":buf_data, "BACKEND_NAME":backend_name}) )
                                buf_fk = b'Receive success'
                                tlog.log_info("报文接收成功")
                            # 返回报文，看情况，可能不需要返回报文
                            client.sendall( buf_fk )
                        # 处理服务器端的发送消息
                        elif indata==ownclient:  
                            data = ownclient.recv(10000)
                            if data == b"hello":
                                break
                            if data:  
                                t_buf = pickle.loads(data)["BUF"]
                                if t_buf == b'88':
                                    tlog.log_info("服务端主动结束")
                                    isEnd = "YES"
                                    break
                                client.send(t_buf)  
                                tlog.log_info( '主动发送的报文为:[%s]' % t_buf )
                except:
                    tlog.log_exception( "服务端通讯异常:")
                    isEnd = "YES"
                if isEnd == "YES":
                    try:
                        inputlist.remove(client)
                    except:
                        pass
                    break
        except: 
            tlog.log_exception( "服务端建立连接异常:")
            break
        finally:
            if client:client.close()
            # 一次链接完成，关闭tlog
            if rzlsh : tlog.close(rzlsh)


if __name__ == '__main__':
    print(main({'PORT':'11111','PORT_SHORT':'22222'} ,'shhx-test', 'test_22222'))
