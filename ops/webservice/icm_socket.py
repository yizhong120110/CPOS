# -*- coding: utf-8 -*-
""" python26版 """
"""
    将接收到的报文通过socket方式转发给ICM
"""

import socket,os
import traceback
import struct
import icm_spec


def main( kwd ,commnode_id = 'ZDFSSVR' ):
    """
        # kwd 字典
        # IP、PORT、BUF、TIMEOUT、FILENAME
        # FILENAME：文件名称，此字段有值表示有文件需要ftp给三方
       
        返回值：
            1：正常的返回值
            -1：kwd中的值不全
            -2：创建socket连接失败
            -3：发送报文失败
            -4：接收报文失败
    """
    # 字段值校验
    if not kwd.get('IP') or not kwd.get('PORT') or not kwd.get('BUF'):
        return {'flag':-1 ,'buf':''}
    
    s = None
    try:
        # socket连接
        try:
            IP_PORT = ( kwd['IP'], int(kwd['PORT'] ) )
            s = socket.socket()
            # 设定通讯超时时间
            s.settimeout( int(kwd.get( 'TIMEOUT', 30 )) ) 
            # 连接对方，连接不成功返回-1
            s.connect( IP_PORT ) 
        except:
            return {'flag':-2 ,'buf':'%s'%(traceback.format_exc())}

        # 发送报文
        try:
            # 报文直接发送，不需要分包
            buf = icm_spec.build_icm_frame(commnode_id,kwd['BUF']).marshal()
            s.send( buf )  
        except:
            return {'flag':-3 ,'buf':'%s'%(traceback.format_exc())}
        
        # 接收报文
        try:
            message_body = ""
            while True:
                # 目前报文未分包，不需要考虑分包接收的问题
                resbuf = s.recv( 10000 )
                flen ,in_frame = icm_spec.icm_decode_frame(resbuf)
                commnode_id,message_body = icm_spec.icm_decode_frame_payload(in_frame.payload)
                if in_frame.frame_type == 0x02:
                    print 'Received [message_body].'
                    break
                elif in_frame.frame_type == 0x03:
                    print 'Received [ACCEPTED].' + str(message_body)
                elif in_frame.frame_type == 0x04:
                    message_body = 'REFUSED'
                    break
                else:
                    break

            return {'flag':1 ,'buf':message_body} 
        except:
            return {'flag':-4 ,'buf':'%s'%(traceback.format_exc())}
    finally:
        if s:
            s.close()

if __name__ == '__main__':
    # 测试
    print(main({}))
    buf = b'\x01\x01\x00\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x01\x00\x00\x00EZDFSSVR\x00\x00\x00\x00\x00\x00\x00\x00\x000053RL9999          {"JYJGM": "1001", "CZGY": "1001"}WS'
    print(main({'IP':'46.17.189.232','PORT':'5620','BUF':buf}))
#    print repr(icm_spec.build_icm_frame('ZDFSSVR',b'0053RL9999          {"JYJGM": "1001", "CZGY": "1001"}').marshal())
