# -*- coding: utf-8 -*-

#数值型字段打包

import struct
import binascii

from ops.trans.fmtstring import e_string , d_string


def e_int(value , buflen = 0 , align = 'R' , fillchar = '0' ):
    """ 打包，整型数值字段打包格式字符串
        参数列表：value:       字段内容
                  buflen:      填充后总长度 
                  align: 字段对齐(默认左对齐) L:左对齐 R:右对齐 C:居中
                  fillchar:    填充字符(默认空格符)
    """
    if value is None:
        value = 0
    tmpstr = str(int(value))
    return e_string( tmpstr , buflen , align , fillchar )

def e_float(value , buflen = 0 , fmt = '%.2f' , align = 'R' , fillchar = '0' ):
    """
    打包，浮点型数值字段打包格式字符串
    参数列表：value:       字段内容
              buflen:      填充后总长度 
              align: 字段对齐(默认左对齐) L:左对齐 R:右对齐 C:居中
              fillchar:    填充字符(默认空格符)
    """
    if value is None:
        value = 0.0
    tmpstr = fmt % float( value )
    return e_string( tmpstr , buflen , align , fillchar )


def e_sint_binary_l( value , buflen = 0 , align = 'R' , fillchar = ' ' ):
    """
    打包，短整型数值字段打包二进制(低位在前)格式字符串
    参数列表：value:       字段内容
              buflen:      填充后总长度 
              align: 字段对齐(默认左对齐) L:左对齐 R:右对齐 C:居中
              fillchar:    填充字符(默认空格符)
    """
    try:
        tmpstr = struct.pack('<h',value)
        return e_string( tmpstr , buflen , align , fillchar )
    except:
        raise RuntimeError( '输入内容不是合法的格式' )


def e_sint_binary_b( value , buflen = 0 , align = 'R' , fillchar = ' ' ):
    """
    打包，短整型数值字段打包二进制(高位在前)格式字符串
    参数列表：value:       字段内容
              buflen:      填充后总长度 
              align: 字段对齐(默认左对齐) L:左对齐 R:右对齐 C:居中
              fillchar:    填充字符(默认空格符)
    """
    try:
        tmpstr = struct.pack('>h',value)
        return e_string( tmpstr , buflen , align , fillchar )
    except:
        raise RuntimeError( '输入内容不是合法的格式' )


def e_int_binary_l( value , buflen = 0 , align = 'R' , fillchar = ' ' ):
    """
    打包，整型数值字段打包二进制(低位在前)格式字符串
    参数列表：value:       字段内容
              buflen:      填充后总长度 
              align: 字段对齐(默认左对齐) L:左对齐 R:右对齐 C:居中
              fillchar:    填充字符(默认空格符)
    """
    try:
        tmpstr = struct.pack('<i',value)
        return e_string( tmpstr , buflen , align , fillchar )
    except:
        raise RuntimeError( '输入内容不是合法的格式' )

def e_int_binary_b( value , buflen = 0 , align = 'R' , fillchar = ' ' ):
    """
    打包，整型数值字段打包二进制(高位在前)格式字符串
    参数列表：value:       字段内容
              buflen:      填充后总长度 
              align: 字段对齐(默认左对齐) L:左对齐 R:右对齐 C:居中
              fillchar:    填充字符(默认空格符)
    """
    try:
        tmpstr = struct.pack('>i',value)
        return e_string( tmpstr , buflen , align , fillchar )
    except:
        raise RuntimeError( '输入内容不是合法的格式' )

def e_float_binary_l( value , buflen = 0 , align = 'R', fillchar = ' ' ):
    """
    打包，浮点型数值字段打包二进制(低位在前)格式字符串
    参数列表：value:       字段内容
              buflen:      填充后总长度 
              align: 字段对齐(默认左对齐) L:左对齐 R:右对齐 C:居中
              fillchar:    填充字符(默认空格符)
    """
    try:
        tmpstr = struct.pack('<f',value)
        return e_string( tmpstr , buflen , align , fillchar )
    except:
        raise RuntimeError( '输入内容不是合法的格式' )

def e_float_binary_b( value , buflen = 0 , align = 'R' , fillchar = ' ' ):
    """
    打包，浮点型数值字段打包二进制(高位在前)格式字符串
    参数列表：value:       字段内容
              buflen:      填充后总长度 
              align: 字段对齐(默认左对齐) L:左对齐 R:右对齐 C:居中
              fillchar:    填充字符(默认空格符)
    """
    try:
        tmpstr = struct.pack('>f',value)
        return e_string( tmpstr , buflen , align , fillchar )
    except:
        raise RuntimeError( '输入内容不是合法的格式' )

def e_int_money( value , buflen = 0 , align = 'R' , fillchar = '0' ):
    """
     打包，以分为单位的金额格式话
     参数列表: value       字段内容，整形或浮点型，以元为单位
               buflen      填充后长度
               align 对齐方式(默认左对齐) L:左对齐 R:右对齐 C:居中
               fillchar    填充字符(默认空格符)
    """
    if value is None:
        value = 0
    if float(value) <0:
        s = b'-'+ e_int( round(abs(value) * 100) , buflen-1 , align , fillchar )
        return s
    else:
        return e_int( round(value * 100) , buflen , align , fillchar )

def e_beai_money( value, buflen, decimaldigit=3, sign = 'R', encoding = 'utf-8' ):
    """ BEAI金额字段打包
    参数列表：value         金额值
              buflen        金额总长度
              decimaldigit  小数位长度
              sign          符号位，默认在右边，R:右;L:左,N:无
              align         对齐方式，R:右;L:左
              fillchar      位数不足时要补充的字符
    根据《HXB_业务集成平台BEAI接口规范_分行特色v1.0.doc》的描述，S为带符号(+、-)的金额类型，数据不足时左补0，符号在字段最后一位上。
    例如：9(14)V999S表示14位整数3位小数，小数点不占位，最后一位是符号位，整个字符串总长度位18
    -102.234元转成18位字符串的表示为00000000000102234-，本函数可将00000000000102234-解析回-102.234。
    """
    f = float( value )
    if f >= 0:
        bz = '+'
    else:
        bz = '-'
        f = -f
    zslen = buflen + ( 1 if sign == 'N' else 0 )
    value = ( ( '%%0%d.%df' % ( zslen , decimaldigit ) ) % f ).replace( '.' , '' )
    if sign == 'R':
        return ( value+bz ).encode( encoding )
    elif sign == 'L':
        return ( bz+value ).encode( encoding )
    else:
        return ( value ).encode( encoding )

def d_int( buf , start = 0 , length = 0 , fillchar = ' ', encoding='utf-8' ):
    """
    解包，提取整数字段
    参数列表：buf:      原始报文串
              start:    字段起始位置 
              length:   字段长度
              fillchar: 填充字符(默认空格符)
    """
    tmpstr = d_string( buf , start , length, fillchar, encoding=encoding )
    if tmpstr:
        try:
            tmp = int(tmpstr)
            return tmp
        except:
            raise RuntimeError( '输入内容[%s]不是合法的格式' % tmpstr )
    else:
        return 0

def d_float( buf , start = 0 , length = 0 , fillchar = ' ', encoding = 'utf-8' ):
    """
    解包，提取浮点数字段
    参数列表：buf:      原始报文串
              start:    字段起始位置 
              length:   字段长度
              fillchar: 填充字符(默认空格符)
    """
    tmpstr = d_string( buf , start , length, fillchar, encoding=encoding )
    if tmpstr:
        try:
            tmp = float(tmpstr)
            return tmp
        except:
            raise RuntimeError( '输入内容[%s]不是合法的格式' % tmpstr )
    else:
        return 0.0

def d_sint_binary_l( buf , start = 0 , length = 0 , fillchar = ' '):
    """
    解包，在二进制(低位在前)格式字符串提取短整型字段
    参数列表：buf:      原始报文串
              start:    字段起始位置 
              length:   字段长度
              fillchar: 填充字符(默认空格符)
    """
    tmpstr = d_bytes( buf , start , length, fillchar )
    if tmpstr:
        if len(tmpstr) != struct.calcsize('h'):
            raise RuntimeError( '输入内容长度不符' )
        try:
            tmp , = struct.unpack('<h',tmpstr)
            return tmp
        except:
            raise RuntimeError( '输入内容[%s]不是合法的格式' % tmpstr )
    else:
        return 0
        
def d_sint_binary_b( buf , start = 0 , length = 0 , fillchar = ' '):
    """
    解包，在二进制(高位在前)格式字符串提取短整型字段
    参数列表：buf:      原始报文串
              start:    字段起始位置 
              length:   字段长度
              fillchar: 填充字符(默认空格符)
    """
    tmpstr = d_bytes( buf , start , length, fillchar )
    if tmpstr:
        if len(tmpstr) != struct.calcsize('h'):
            raise RuntimeError( '输入内容长度不符' )
        try:
            tmp , = struct.unpack('>h',tmpstr)
            return tmp
        except:
            raise RuntimeError( '输入内容[%s]不是合法的格式' % tmpstr )
    else:
        return 0

def d_int_binary_l( buf , start = 0 , length = 0 , bin = True , fillchar = ' '):
    """
    解包，在二进制(低位在前)格式字符串提取整型字段
    参数列表：buf:      原始报文串
              start:    字段起始位置 
              length:   字段长度
              fillchar: 填充字符(默认空格符)
    """
    tmpstr = d_bytes( buf , start , length, fillchar)
    if tmpstr:
        if bin == False:
            tmpstr = binascii.a2b_hex( tmpstr )
        
        if len(tmpstr) != struct.calcsize('i'):
            raise RuntimeError( '输入内容[%s]长度不符' % tmpstr )
        try:
            tmp , = struct.unpack('<i',tmpstr)
            return tmp
        except:
            raise RuntimeError( '输入内容[%s]不是合法的格式' % tmpstr )
    else:
        return 0

def d_int_binary_b( buf , start = 0 , length = 0 , bin = True , fillchar = ' '):
    """
    解包，在二进制(高位在前)格式字符串提取整型字段
    参数列表：buf:      原始报文串
              start:    字段起始位置 
              length:   字段长度
              fillchar: 填充字符(默认空格符)
    """
    tmpstr = d_bytes( buf , start , length, fillchar)
    if tmpstr:
        if bin == False:
            tmpstr = binascii.a2b_hex( tmpstr )
        
        if len(tmpstr) != struct.calcsize('i'):
            raise RuntimeError( '输入内容[%s]长度不符' % tmpstr )
        try:
            tmp , = struct.unpack('>i',tmpstr)
            return tmp
        except:
            raise RuntimeError( '输入内容[%s]不是合法的格式' % tmpstr )
    else:
        return 0

def d_float_binary_l( buf , start = 0 , length = 0 , fillchar = ' '):
    """
    解包，在二进制(低位在前)格式字符串提取浮点型字段
    参数列表：buf:      原始报文串
              start:    字段起始位置 
              length:   字段长度
              fillchar: 填充字符(默认空格符)
    """
    tmpstr = d_bytes( buf , start , length, fillchar )
    if tmpstr:
        if len(tmpstr) != struct.calcsize('f'):
            raise RuntimeError( '输入内容[%s]长度不符' % tmpstr )
        try:
            tmp , = struct.unpack('<f',tmpstr)
            tmp1 = round(tmp,2)
            return tmp1
        except:
            raise RuntimeError( '输入内容[%s]不是合法的格式' % tmpstr )
    else:
        return 0.0

def d_float_binary_b( buf , start = 0 , length = 0 , fillchar = ' '):
    """
    解包，在二进制(高位在前)格式字符串提取浮点型字段
    参数列表：buf:      原始报文串
              start:    字段起始位置 
              length:   字段长度
              fillchar: 填充字符(默认空格符)
    """
    raise RuntimeError( 'API d_float_binary_b待调试' )
    tmpstr = d_bytes( buf , start , length, fillchar )
    if tmpstr:
        if len(tmpstr) != struct.calcsize('f'):
            raise RuntimeError( '输入内容[%s]长度不符' % tmpstr )
        try:
            tmp , = struct.unpack('>f',tmpstr)
            tmp = round(tmp,2)
            return tmp
        except:
            raise RuntimeError( '输入内容[%s]不是合法的格式' % tmpstr )
    else:
        return 0.0

def d_int_money( buf , start = 0 , length = 0 , fillchar = ' ', encoding = 'utf-8' ):
    """ 金额解包函数
    """
    m = d_int( buf , start , length, encoding=encoding )
    return m / 100.0

def d_beai_money( buf, start=0, length=0, decimaldigit=3, f=1, encoding = 'utf-8' ):
    """ BEAI金额字段解包
    参数列表：buf           原始报文串
              start         字段起始位置
              length        字段长度
              decimaldigit  小数位长度
    根据《HXB_业务集成平台BEAI接口规范_分行特色v1.0.doc》的描述，S为带符号(+、-)的金额类型，数据不足时左补0，符号在字段最后一位上。
    例如：9(14)V999S表示14位整数3位小数，小数点不占位，最后一位是符号位，整个字符串总长度位18
    -102.234元转成18位字符串的表示为00000000000102234-，本函数可将00000000000102234-解析回-102.234。
    #11:09 2010-12-2 增加一个参数f，当f=1时，表示符号位在最后面，f=0时，表示符号为在前面
    """
    if f:
        m = d_int( buf, start, length-1, encoding=encoding ) # 先转换为int型的分，不考虑符号
        tmp = buf[start+length-1:start+length]
    else:
        m = d_int( buf, start+1, length-1, encoding=encoding )
        tmp = buf[start:start+1]
    m = m if decimaldigit==0 else m * 1.0 / 10**decimaldigit # 转为float型的元，不考虑符号
    return m if tmp==b'+' else -m # 修正符号

map_z = dict( [ ( chr( ord( 'A' ) + x ) , x + 10 ) for x in range( 26 ) ] )
map_z.update( dict( [ ( '%d' % x , x ) for x in range( 10 ) ] ) )

umap_z = dict( [ (  x + 10 , chr( ord( 'A' ) + x ) ) for x in range( 26 ) ] )
umap_z.update( dict( [ ( x , '%d' % x ) for x in range( 10 ) ] ) )

Z = 36

def e_ZNUM( num , l = 1 , align='R', fillchar = '0'):
    """
        将数字转换为36进制数据. 即以Z为最大字符的数字表达方式，如：
            0 -> 0
            Z -> 35
            ZZZZ -> 1679615
    """
    s = ''
    while num > 0:
        num , m = divmod( num , 36 )
        s = umap_z[ m ] + s
    return e_string( s ,buflen = l , align = align,fillchar =fillchar  )

def d_ZNUM(  buf , start = 0 , length = 0 , fillchar = ' ' ):
    """
        将36进制数据转换为数字. 即以Z为最大字符的数字表达方式，如：
            0 -> 0
            Z -> 35
            ZZZZ -> 1679615
    """
    s = d_string( buf , start , length, fillchar)
    s = s.upper()
    num = 0
    i = 0
    while s:
        c = s[-1]
        s = s[:-1]
        num += map_z[ c ] * Z ** i
        i += 1
    return num

if __name__ == '__main__':
#    print e_ZNUM(44026,4)
#    print d_ZNUM( 'ZZZZ' )
#    
#    for x in range( 0 , 1679615 ):
#        b = e_ZNUM( x,10 )
#        #print x , '->' , b , '->' ,
#        c = d_ZNUM( b )
#        #print c
##        assert( x == c )
#     e_beai_money(-112650.0100)
#     d_beai_money('1111+00000000058966640+11111',5,18,3)
    print (e_int_money( -3.15 , buflen = 10  ))