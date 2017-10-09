# -*- coding: utf-8 -*-

#日期型字段打包

from ops.trans.fmtstring import  e_string , d_string

from datetime import date , timedelta , datetime , time as dtime
import time
from ops.core.logger import traceback2

def e_datetime(value ,  buflen = 0 , align = 'L' , fmt = '%Y%m%d%H%M%S' ,fillchar = ' ' , encoding = 'utf-8' ):
    """
    打包，日期 时间型打包为格式字符串
    参数列表：value:       字段内容
              buflen:      填充后总长度 
              align: 字段对齐(默认左对齐) L:左对齐 R:右对齐 C:居中
              format:      转换格式(默认'%Y%m%d%H%M%S')
              fillchar:    填充字符(默认空格符)
              encoding:
    """
    try:
        if value:
            tmpstr = value.strftime( fmt )
        else:
            tmpstr = ''
        return e_string( tmpstr , buflen , align , fillchar, encoding )
    except:
        raise RuntimeError( '输入内容[%s]不是合法的格式' % value )

def e_date(value ,  buflen = 0 , align = 'L' , fmt = '%Y%m%d' ,fillchar = ' ' , encoding = 'utf-8' ):
    """
    打包，日期 时间型打包为格式字符串
    参数列表：value:       字段内容
              buflen:      填充后总长度 
              align: 字段对齐(默认左对齐) L:左对齐 R:右对齐 C:居中
              format:      转换格式(默认'%Y%m%d%H%M%S')
              fillchar:    填充字符(默认空格符)
    """
    return e_datetime( value , buflen , align = align , fmt = fmt , fillchar = fillchar, encoding = encoding )

def e_time(value , buflen = 0 , align = 'L' , fmt = '%H:%M:%S' ,fillchar = ' ' , encoding = 'utf-8' ):
    """
    打包，日期 时间型打包为格式字符串
    参数列表：value:       字段内容
              buflen:      填充后总长度 
              align: 字段对齐(默认左对齐) L:左对齐 R:右对齐 C:居中
              format:      转换格式(默认'%Y%m%d%H%M%S')
              fillchar:    填充字符(默认空格符)
    """
    return e_datetime( value , buflen , align = align , fmt = fmt , fillchar = fillchar, encoding = encoding )

ZERO_DATE = date( 1899 , 12 , 31 )
import copy

def long2date( i ):
    """
    整型转换为日期型
    """
    if type( i ) != int:
        if i is not None:
            raise RuntimeError( '整形数据[%s]无法按照规则转换为日期型' % repr(i) )
        else:
            i = 0
    if i:
        return ZERO_DATE + timedelta(i)
    else:
        return copy.copy( ZERO_DATE )

def date2long( d ):
    """
    日期型转换为整型  先判断传进来的参数d类型不能为空，然后判断是否是日期型
    """
    if not isinstance( d , date ):
        if d is not None:
            raise RuntimeError( '日期型数据[%s]无法按照规则转换为整形' % repr(d) )
        else:
            return 0
    return ( d - ZERO_DATE ).days

def d_date( buf ,  start = 0 , length = 0 ,fmt = '%Y%m%d' , fillchar = ' ' , encoding = 'utf-8' ):
    """
    解包，获取日期型字段
    参数列表：buf:      原始报文串
              start:    字段起始位置 
              length:   字段长度
              format:   转换格式(默认'yyyymmdd')
              fillchar: 填充字符(默认空格符)
    """
    t = get_tuple( buf , start , length , fmt , fillchar , encoding )
    if t:
        return t.date()
    return None

def d_time( buf ,  start = 0 , length = 0 ,fmt = '%H%M%S' , fillchar = ' ' , encoding = 'utf-8' ):
    """
    解包，获取时间型字段
    参数列表：buf:      原始报文串
              start:    字段起始位置 
              length:   字段长度
              format:   转换格式(默认'HHMMSS')
              fillchar: 填充字符(默认空格符)
    """
    t = get_tuple( buf , start , length , fmt , fillchar , encoding )
    if t:
        return t.time()
    return None

def d_datetime( buf ,  start = 0 , length = 0 , fmt = '%Y%m%d%H%M%S' ,fillchar = ' ' , encoding = 'utf-8' ):
    """
    解包，获取日期时间型字段
    参数列表：buf:      原始报文串
              start:    字段起始位置 
              length:   字段长度
              format:   转换格式(默认'yyyymmddHHMMSS')
              fillchar: 填充字符(默认空格符)
    """
    t = get_tuple( buf , start , length , fmt , fillchar , encoding )
    if t:
        return t
    return None
 
import threading
LOCK = threading.Lock()
def get_tuple( buf , start , length , fmt , fillchar , encoding = 'utf-8' ):
    """
    解包  截取指定长度的字符串
    并将得到的字符串转化成日期时间型格式
    """
    with LOCK:
        tmpstr = d_string( buf , start , length, fillchar, encoding )
        if tmpstr:
            try:
                return datetime.strptime( tmpstr , fmt )
            except:
                traceback2.print_exc( show_locals = True )
                raise RuntimeError( '日期格式转换[%s]不能用[%s]格式转换' % ( tmpstr , fmt ) )
        else:
            return None

def e_now( buflen = 0 , align = 'L' , fmt = '%Y%m%d%H%M%S' ,fillchar = ' ' , encoding = 'utf-8' ):
    """
    打包，获取当前时间，并调用e_datetime方法返回一个日期时间型字段
    参数列表：buflen:      填充后总长度 
              align: 字段对齐(默认左对齐) L:左对齐 R:右对齐 C:居中
              format:      转换格式(默认'%Y%m%d%H%M%S')
              fillchar:    填充字符(默认空格符)
    """
    n = datetime.now()
    return e_datetime( n , buflen , align , fmt , fillchar, encoding )
