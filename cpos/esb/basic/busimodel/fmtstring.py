# -*- coding: utf-8 -*-

# 字符串字段打包

def e_string( value , buflen = 0 , align='L' , fillchar = ' ' ):
    """
    打包，字符型字段填充
    参数列表：value:       字段内容
              buflen:      填充后总长度 
              align: 字段对齐(默认左对齐) L:左对齐 R:右对齐 C:居中
              fillchar:    填充字符(默认空格符)
    """
    if value is None:
        value = ''
    elif type( value ) != str:
        value = str(value)
    if len(fillchar) != 1:
        raise RuntimeError( '填充字符参数[fillchar]格式错误' )  
    if buflen > 0:
        if len(value) > buflen:
            raise RuntimeError( '打包字段[%s]长度越界，要求长度为：%d，实际长度为：%d' % ( value , buflen , len(value) ) )
        if align == 'L':
            return value.ljust(buflen,fillchar)
        elif align == 'R':
            return value.rjust(buflen,fillchar)
        elif align == 'C':
            return value.center(buflen,fillchar)
        else:
            raise RuntimeError( '填充方向参数[align]格式错误，合法的参数为L、R、C'  )
    else:
        return value
        
def d_string( buf , start = 0 , length = 0 , fillchar = ' ' ):
    """
    解包，提取字符串字段
    参数列表：buf:      原始报文串
              start:    字段起始位置 
              length:   字段长度
              fillchar: 填充字符(默认空格符)
    """
    if buf is None:
        return None
        
    if length:
        tmpstr = buf[start:start+length].strip(fillchar)
    else:
        tmpstr = buf[start:].strip(fillchar)
    return tmpstr

def d_string_1( buf , start , end , fillchar = ' ' ):
    """
    解包，提取字符串字段
    参数列表：buf:      原始报文串
              start:    字段起始位置 
              end:      字段结束位置
              fillchar: 填充字符(默认空格符)
    """
    tmpstr = buf[start:end+1].strip(fillchar)
    return tmpstr

