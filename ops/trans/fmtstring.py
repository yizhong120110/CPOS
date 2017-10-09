# -*- coding: utf-8 -*-

# 字符串字段打包

def e_string( value , buflen = 0 , align='L' , fillchar = ' ' , encoding = 'utf-8' ):
    """
    打包，字符型字段填充
    参数列表：value:       字段内容
              buflen:      填充后总长度，字节长度
              align: 字段对齐(默认左对齐) L:左对齐 R:右对齐 C:居中对齐
              fillchar:    填充字符(默认空格符)，字节长度为1
              encoding:    报文接收系统的字符编码(默认utf-8)
    """
    if value is None:
        value = b''
    elif type( value ) == bytes:
        pass
    elif type( value ) != str:
        value = str(value).encode( encoding )
    else:
        value = value.encode( encoding )
    
    fillchar = fillchar.encode( encoding )
    if len( fillchar ) != 1:
        raise RuntimeError( '填充字符参数[fillchar]格式错误' )
    
    if buflen > 0:
        if len(value) > buflen:
            raise RuntimeError( '打包字段[%s]长度越界，要求长度为：%d，实际长度为：%d' % ( value.decode( encoding ) , buflen , len(value) ) )
        if align == 'L':
            return value + fillchar * ( buflen - len(value) )
        elif align == 'R':
            return fillchar * ( buflen - len(value) ) + value
        elif align == 'C':
            n = buflen - len(value)
            half = int(n/2)
            if n%2 and buflen%2:
                # This ensures that center(center(s, i), j) = center(s, j)
                half = half + 1
            return fillchar*half + value + fillchar*(n-half)
        else:
            raise RuntimeError( '填充方向参数[align]格式错误，合法的参数为L、R、C'  )
    else:
        return value
        
def d_string( buf , start = 0 , length = 0 , fillchar = ' ' , encoding = 'utf-8' ):
    """
    解包，提取字符串字段
    参数列表：buf:      原始报文串
              start:    字段起始位置 
              length:   字段长度
              fillchar: 填充字符(默认空格符)
              encoding: 报文接收系统的字符编码(默认utf-8)
    """
    if buf is None:
        return None
    if type( buf ) != bytearray and type( buf ) != bytes:
        raise RuntimeError( '原始报文串类型[%s]错误，需为[bytes]类型'%type(buf)  )
    if length:
        tmpstr = buf[start:start+length].strip( fillchar.encode( encoding ) )
    else:
        tmpstr = buf[start:].strip( fillchar.encode( encoding ) )
    return tmpstr.decode( encoding )

def d_bytes( buf , start = 0 , length = 0 , fillchar = ' ' , encoding = 'utf-8' ):
    """
    解包，提取字符串字段
    参数列表：buf:      原始报文串
              start:    字段起始位置 
              length:   字段长度
              fillchar: 填充字符(默认空格符)
              encoding: 报文接收系统的字符编码(默认utf-8)
    """
    if buf is None:
        return None
    if type( buf ) != bytes:
        raise RuntimeError( '原始报文串类型错误，需为[bytes]类型'  )
    if length:
        tmpstr = buf[start:start+length].strip( fillchar.encode( encoding ) )
    else:
        tmpstr = buf[start:].strip( fillchar.encode( encoding ) )
    return tmpstr
