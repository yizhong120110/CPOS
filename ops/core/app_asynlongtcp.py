# -*- coding: utf-8 -*-
"""
    socket异步全双工长连接
    二次开发仅开发真正的业务处理逻辑文件即可，通过-T对应的值，导致数据库中的client_type，然后获得相应的处理逻辑代码
    要求：gl_jcxxpz.jcmc=gl_txgl.bm
    python34 app_asynlongtcp.py -p 5614 -T jnfstpos_app -i b13bdf8529ff4f5b89b12cef1ad5b493 -t 10 -w 600
"""
from ops.core.logger import logger
from ops.core.app import RpclogEApp ,get_shell_args
from ops.core.rpc import start_ocm_server
from ops.core.rdb_icpocm import get_txxx ,get_txcs
import socket
import pickle
import sys
import time
import random


# 使用client_type作为唯一标识，然后查询数据库，得到相关信息
options ,args = get_shell_args()
selfname = options['client_type']

########################################################################
#def get_txcs( txjclx ,txbm = None ):
#    print("get_txcs =====",txjclx ,txbm)
#    return {'IP': '127.0.0.1' ,'PORT': '20012,31111' ,'PORT_SHORT': '10012,32222' ,'IP': '127.0.0.1'}
#    
#def get_txxx( txjclx ):
#    print("get_txxx =====",txjclx)
#    return {'txwj': 'ops.icp.long_tcp.demo3' ,'txwjmc': 'rpcTCPLong' ,'bm': 'shhx-test'}
########################################################################

def _port_is_free(port):
#    print('check port %d isfree?'%port)
    logger.ods( 'check port %d isfree?'%port ,lv = 'info',cat = 'ops.app_asynlongtcp')
    s = socket.socket()
    s.settimeout(0.5)
    try:
        #s.connect_ex return 0 means port is open
        rs = s.connect_ex(('localhost', port)) != 0
#        print('check result is %s'%rs)
        logger.ods( 'check result is %s'%rs ,lv = 'info',cat = 'ops.app_asynlongtcp')
        return rs
    finally:
        s.close()

class TCPLong(RpclogEApp):
    """
        单个三方，socket异步全双工长连接 通讯
        接收到三方的报文后，转发核心ICM
        然后通过RMQ获得返回结果，发送给三方
    """
    def service (self ,received):
        # 这里不能够输出日志，有可能存在文件，输出文件内容时会很大
        # buff才是二次开发者操作的变量，封装一下的目的是为了保证二次开发传递的参数都在一个字典value中
        comm_message = received.getcontent()["buff"]
        try:
            data = pickle.dumps(comm_message["kwd"])
            self.tcpCliSock.send(data)
            return {"rsbuff":'END'}, self.keep_running
        except:
            return {"rsbuff":"存在语法错误: "+str(sys.exc_info())}, self.keep_running

    def jobResponder (self):
        # 这里用于从RMQ上获得消息
        try:
            # 用于线程间通讯
            time.sleep(2)
            self.tcpCliSock = socket.socket(socket.AF_INET ,socket.SOCK_STREAM)
            self.tcpCliSock.connect(('127.0.0.1' ,int(self.txxtcs["PORT_SHORT"])))  
            self.tcpCliSock.send( b"hello" )

            # zhangchl 和 shihx 确认 此处需要使用通讯文件名称，是和ops.trans.node.py 中
            # call_node的 message_to_ocm(senddic,jyzd.TXWJMC,int(jyzd.TIMEOUT)+5) TXWJMC 遥相呼应
            start_ocm_server([self.backend_name] ,self.service)
        except:
            logger.oes( 'jobResponder' ,lv = 'error',cat = 'ops.app_asynlongtcp')
        self.stopping()
        return True

    def working_rpcstart(self):
        # 二次开发者实现的监听代码
        try:
            main( self.txxtcs, self.txxxdic['bm'] ,self.backend_name )
        except:
            logger.oes( 'working_rpcstart.main' ,lv = 'error',cat = 'ops.app_asynlongtcp')
            # 有可能是端口被占用了，随机睡眠一定时间
            time.sleep(random.randint(1,5))
        self.stopping()
        return True

    def on_start (self):
        self.txxxdic = get_txxx(selfname)
        self.txxtcs = get_txcs(selfname, txbm = self.txxxdic['bm'])
        self.backend_name = "%s_%s"%(self.txxxdic['txwjmc'], self.txxtcs["PORT_SHORT"])
        continue_cnt = 0
        try:
            # 这里是为了能够获得一个可用的端口，用于外部通讯
            ps = self.txxtcs["PORT"].split(',')
            flag = False
            for tport in ps:
                if tport and _port_is_free(int(tport)):
                    # 这是一个可用的端口
                    self.txxtcs["PORT_BAK"] = self.txxtcs["PORT"]
                    self.txxtcs["PORT"] = tport
                    flag = True
                    break
                # 如果外部端口被占用了，对应的内部端口就不检查了
                continue_cnt = continue_cnt + 1
            if flag == False:
                logger.ods( 'on_start PORT 无可用监听端口' ,lv = 'warning',cat = 'ops.app_asynlongtcp')
                self.stopping()

            # 这里是为了能够获得一个可用的端口，用于内部通讯
            ps = self.txxtcs["PORT_SHORT"].split(',')
            flag = False
            for tport in ps:
                if continue_cnt > 0:
                    continue_cnt = continue_cnt - 1
                    continue
                if tport and _port_is_free(int(tport)):
                    # 这是一个可用的端口
                    self.txxtcs["PORT_SHORT_BAK"] = self.txxtcs["PORT_SHORT"]
                    self.txxtcs["PORT_SHORT"] = tport
                    self.backend_name = "%s_%s"%(self.txxxdic['txwjmc'], tport)
                    flag = True
                    break
            if flag == False:
                logger.ods( 'on_start PORT_SHORT 无可用监听端口' ,lv = 'warning',cat = 'ops.app_asynlongtcp')
                self.stopping()
        except:
            logger.oes( 'on_start' ,lv = 'error',cat = 'ops.app_asynlongtcp')
            # 出现异常就关闭
            self.stopping()
        
        # 引用放在这里，是为了能够在启动时就检查模块是否配置错误
        exec("from %s import main"%(self.txxxdic['txwj']) ,globals())

        RpclogEApp.on_start(self)
        # 这是附加一个线程
        self.register_thread('working_rpcstart',self.working_rpcstart)
        self.register_thread('jobResponder',self.jobResponder)

TCPLong(appname=selfname).run()
