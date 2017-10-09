# -*- coding: utf-8 -*-
# 功能描述 ：  TCR C端通讯客户端.
# 作　　者 ：  张孝党
# 日　　期 ：  2017/04/16
# 版　　本 ：  V1.00
# 更新履历 ：  V1.00 2017/04/16 张孝党 更新.

import socket
import json
from ops.core.logger import tlog ,set_tlog_parms

def main( kwd ):
    """
       # kwd 字典
       # IP、PORT、BUF、TIMEOUT、FILENAME、TCRC_IP
       # FILENAME：文件名称，此字段有值表示有文件需要ftp给三方
    """
    # rzlsh 是本次日志的流水号，可以将其返回，用于查询日志
    rzlsh = set_tlog_parms( tlog ,'tcrc_ocm' ,kind='tcrc_ocm', reload_jyzd='yes' )
    tlog.log_info('本次通讯的日志流水号为：【%s】' % rzlsh)
    # 1.socket连接
    try:
        # 因C端有多个，所以在与C端通讯时IP需要在交易中存到jyzd.TCRC_IP字段中
        # SB_IP = ( kwd['IP'], int(kwd['PORT'] ) )
        SB_IP = ( kwd['TCRC_IP'], int(kwd['PORT'] ) )
        tlog.log_info( 'Socket连接C端的IP为【%s】' % kwd['TCRC_IP'] )
        s = socket.socket()
        # 设定通讯超时时间
        s.settimeout( int(kwd.get( 'TIMEOUT', 30 )) )
        # 连接对方，连接不成功返回-1
        s.connect( SB_IP )
    except:
        import traceback
        # 创建连接失败
        tlog.log_info( 'Socket连接失败[%s] ' % traceback.format_exc() )
        return -2
    
    # 2.发送报文
    try:
        # 组织报文
        #len_buf = len( kwd['BUF'] )
        #tlog.log_info( '要发送的报文长度为[%s]' % len_buf )
        buf = kwd['BUF']
        tlog.log_info( '要发送的报文为send>>>>>>>>>:[%s]' % buf )
        # 报文直接发送，不需要分包
        s.send( buf )
    except:
        import traceback
        # 报文发送过程中失败
        tlog.log_info( '发送报文失败:[%s]' % traceback.format_exc() )
        s.close()
        return -3
    
    # 3.接收报文
    try:
        tlog.log_info( '等待接收报文' )
        # 目前报文未分包，不需要考虑分包接收的问题
        jsddbw = b''

        ## 接收报文长度
        #jsddbw_len = int( s.recv( 7 ).decode( 'utf-8' ) )
        #tlog.log_info( '接收到的反馈报文为长度：[%s]' % jsddbw_len )
        ## 接收报文
        #l = 0
        #while l < jsddbw_len:
        #    f = s.recv( jsddbw_len - l )
        #    if len( f ) == 0:
        #        break
        #    l += len( f )
        #    jsddbw += f
        # 接收报文
        jsddbw = s.recv(10000)
        tlog.log_info( '接收到的反馈报文为：[%s]' % jsddbw )
        return jsddbw
    except:
        import traceback
        # 报文接收失败
        tlog.log_info( '接收报文异常！[%s]' % traceback.format_exc() )
        return -4
    finally:
        s.close()
        tlog.close( rzlsh )

if __name__ == '__main__':
    buf = b"<?xml version='1.0' encoding='utf-8'?><Service><Service_Header><service_sn>1560109000009000013</service_sn><service_id>00010000506700</service_id><requester_id>0109</requester_id><branch_id>816010006</branch_id><channel_id>06</channel_id><service_time>20161108155643</service_time><version_id>01</version_id></Service_Header><Service_Body><ext_attributes /><request><CRD-NO>6228480408168381270</CRD-NO><DRW-ACCT>0</DRW-ACCT><DRW-AMT>50</DRW-AMT><SVC /><PSWD>.-2E)(44325F.!4E</PSWD><SEC-MT-CON>996228480408168381270=222222000000000000000000000022222222222==000000000000=000000000000=018472600000000</SEC-MT-CON><THD-MT-CON>996228480408168381270=222222000000000000000000000022222222222==000000000000=000000000000=018472600000000</THD-MT-CON><ATM-NO>9999</ATM-NO><ATM-TX-SQ-NO>20152156693</ATM-TX-SQ-NO><TX-DT>20161108</TX-DT><TRANS-DATE>20161108155643</TRANS-DATE><TX-DSCRP /><RESV-DRW-FLG>0</RESV-DRW-FLG><RESV-CHANNEL-FLG /><RESV-AOMSG-AREA /><RESV-COD /><TXCHK-TYP /><ACQUIRE_INST_ID /><SERI-INFO-AREA /><MOBILE-NO /></request></Service_Body></Service>"
    
    buf_fk = main({'IP':'36.0.1.128', 'PORT':'9052', 'BUF': buf})
    print( buf_fk.decode('utf-8'))
