#!/home/tstx/apps/python34/bin/python34
# -*- coding: utf-8 -*-

# 用于tong的转发进程
# 综合前置-->FESB-->核心

import os, datetime, sys
import struct
import socket
import pickle
import tong
import traceback
from ops.core.rpc import call_jy_reply
from ops.trans import log
log.init_log( "tongsvr4beai", screen = True )

log.info( 'tongsvr4beai', "初始化tongsvr4beai" )

try:
    echo_code = 0
    i = tong.TEAppLogin(  int( sys.argv[1] )  )
    if i < 0:
        log.info( 'tongsvr4beai', '应用程序注册失败，apptype：%s，retcode：%s' % ( int( sys.argv[1] ), i ) )
        sys.exit(0)
    
    t_obj = tong.TEPKINFO()
    
    i , buf , files = tong.TESvrRcv( t_obj )
    if i < 0:
        raise RuntimeError( 'received error: %d' % i )
        
    # 保留原始报文，以备超时返回使用
    buf_fh = buf

    log.info( 'tongsvr4beai', '接收到BANCSLINK发送的通讯请求，请求方[%s]，内容[%s]' % ( t_obj.Src.decode('gb18030'), repr(buf_fh) ) )
    log.info( 'tongsvr4beai', '接收到的交易码：%s' % t_obj.PktType.decode('gb18030'))

    if t_obj.PktType.decode('gb18030') == '0200':
        try:
            buf = call_jy_reply( 'BANCSLINK_SVR', buf )
            log.info( 'tongsvr4beai', 'FESB返回内容为：[%s]' % repr(buf) )
            
            # 根据与交易打包的约定解析报文，获取要发送的文件以及要发送的报文
            buf_dic = pickle.loads( buf )
            files, buf = buf_dic['SYS_YFSDWJ'], buf_dic['SYS_YFSDBW']
            # 应该于tongfil目录下直接获取文件发送
            log.info( 'tongsvr4beai', '实际返回报文|返回文件：[%s|%s]' % ( buf.decode('gbk') , files.decode('gbk') ) )

            t_obj.DataLen = len( buf )
            t_obj.FileLen = len( files )
        except:
            log.exception( 'tongsvr4beai', '交易处理异常A' )
            # 异常时，报文原样返回
            buf = buf_fh[:7] + 'A'.encode('gbk') + buf_fh[8:158] + 'EPY001'.encode('gbk') + (( '%-120s' % '交易失败' ) + ' '*1000).encode('gbk')
            log.info( 'tongsvr4beai', '生成的失败报文为：[%s]' % rep(buf) )
            
            t_obj.DataLen = len(buf)
            files = ''
            t_obj.FileLen = 0

        # 返回
        i = tong.TESvrEcho( t_obj , buf , echo_code , files )
        log.info( 'tongsvr4beai', '交易处理完毕' )
    elif t_obj.PktType.decode('gb18030') == '0202':
        # 确认报文
        tong.TESvrEnd( t_obj , 0 )
    elif t_obj.PktType.decode('gb18030') == '0402':
        # 冲正
        tong.TESvrEnd( t_obj , 0 )
    else:
        tong.TESvrEnd( t_obj , t_obj.EchoCode )
except:
    log.exception( 'tongsvr4beai', '交易处理异常B' )
finally:
    tong.TEAppLogout()
