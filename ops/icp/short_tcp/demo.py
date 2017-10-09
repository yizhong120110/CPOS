# -*- coding: utf-8 -*-
"""
    单独将main函数拆分到一个py文件中，是为了能够利用__name__ == '__main__'进行测试
    使用说明：
    1、在通讯管理中新增配置
        gl_txgl.txwjmc指向main函数所在的py
    2、进程管理中新增配置
        gl_jcxxpz.qdml指向固定的文件ops/core/app_icp.py的绝对路径
        要求 gl_jcxxpz.jcmc = gl_txgl.bm
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
    server = socket.socket()
    server.bind( ('' ,int(kwd["PORT"])) )
    server.listen(10)
    while True:
        client = None
        # rzlsh 是本次日志的流水号，可以将其返回，用于查询日志
        rzlsh = set_tlog_parms(tlog ,"icp_demo" ,kind="icp_demo",reload_jyzd="yes")
        try:
            tlog.log_info("这是演示用demo")
            client, ip = server.accept()
            # 第一种方法：接收报文暂时定为10000,类型为bytes
            #buf_data = client.recv( 1000 )
            ## 第二种方法：接收报文
            buf_len = client.recv( 4 ) # 接收长度位
            buf = buf_len
            size = int( buf_len )
            l = 0
            while l < size:
                f = client.recv( size - l )
                if len( f ) == 0:
                    break
                l += len( f )
                buf += f
            buf_data = buf
            tlog.log_info( "接收到的报文[%s] " % buf_data  )
            buf_fk = call_jy_reply(txbm,buf_data)
            tlog.log_info( "发收到的报文[%s] " % buf_fk  )
            client.send( buf_fk )
        except :
            tlog.log_exception("出异常了")
        finally:
            # 一次处理完成，关闭tlog
            if client: client.close()
            tlog.close(rzlsh)


if __name__ == '__main__':
    print(main({'PORT':'11111'} ,'ZDFSSVR'))
