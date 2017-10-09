# -*- coding: utf-8 -*-
from .fmtdatetime import e_now
import ops.core.rdb
import math
from ops.core.rpc import call_jy_noreply, upload_to_ocm
from cpos.esb.basic.config import settings

from mako.template import Template

def print_( d, mako, filename, encoding='utf-8' ):
    """
    根据模版将打印文件生成到通讯主机
    """
    nr = Template(mako).render(**d)
    nr1 = nr.encode( encoding )
    upload_to_ocm(nr1,filename)

def amtup( src ):
    """
        返回金额大写，输入金额为字符串，以分为单位
    """
    if type( src ) is not str:
        raise RuntimeError( "请指定分单位的金额字符串" )
    larr = ["分","角","元","拾","佰","仟","万","拾","佰","仟","亿","拾","佰","仟","整"]
    sarr=  ["零","壹","贰","叁","肆","伍","陆","柒","捌","玖"]
    src = str(src).strip().lstrip('0')
    rsrc = []
    for i in src:
        rsrc.insert( 0 , i )
    length = len( src )
    if length == 0:
        return '零元整'
    ret = []
    j = length - 1
    while j >= 2:
        if larr[j] in [ '万' , '元' , '亿' ]:   #阶段性数字，需要打出
            if rsrc[j] != '0':
                ret.append( sarr[ int(rsrc[j]) ] )
            if (j < length - 1 ) and rsrc[j+1] == '0' and ret[-1] in [ '零' ] :
                ret.pop(-1) # 跳过前面的零
            if larr[j] == '万' and ret[-1] == '亿':
                j -= 1
                continue # 跳过万前面的亿
            ret.append( larr[j] )
            j -= 1
            continue
        if j < length - 1:  #不是最高位
            if rsrc[j] == '0' and ret[-1] == '零': #如果该位为零且上一位也为零
                j -= 1
                continue
        ret.append( sarr[ int(rsrc[j]) ] )
        if rsrc[j] != '0':
            ret.append( larr[j] )
        j -= 1
    if rsrc[:2] == [ '0' , '0' ]:   #整元
        ret.append( larr[-1] )
    else:
        if  len( rsrc ) > 1:
            ret.append( sarr[ int(rsrc[1]) ] )
            if rsrc[1] != '0':
                ret.append( '角' )
        if rsrc[0] != '0':
            ret.append( sarr[ int(rsrc[0]) ] + '分' )
    #针对此函数在输入“100”时会返回“壹佰零元”特此修改
    dxje = ''.join( ret )
    return dxje

def money_up( je , base ):
    """
        取金额进位单位
        参数列表：
            je：金额，数值型
            base：基数
    """
    return math.ceil( je * 1.0 / base ) * base

#组成GTP文件名用
def get_gtp_lsh( cur = None ):
    if not cur:
        with connection() as con:
            cur = con.cursor()
    sql = " select seq_gtp_lsh.nextval from dual "
    cur.execute( sql )
    lsh = cur.fetchone()[0]
    return lsh
    
def get_zwrq( cur=None, fmt='%Y%m%d'):
    """
        根据系统版本获取账务日期
        并根据格式校验账务日期是否正确
        cur 游标，如果不在事务下，可以不必传送此项
        fmt 账务日期格式，系统校验账务日期是否满足此格式
    """
    zwrq = ''
    try:
        if not cur:
            with connection() as con:
                cur = con.cursor()
                rs = sql_execute( cur, sql )
                while rs.next():
                    zwrq = rs.getString( 'zwrq' )
        else:
            rs = sql_execute( cur, sql )
            while rs.next():
                zwrq = rs.getString( 'zwrq' )
        
        # 校验账务日期格式是否正确
        import datetime
        datetime.datetime.strptime( zwrq, fmt )
        
        return zwrq
    except:
        raise RuntimeError( '获取账务日期非法:%s  FMT[%s]' % ( zwrq, fmt ) )
        
def e_beai_money( value, buflen, decimaldigit=3, sign = 'R' ):
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
        return value+bz
    elif sign == 'L':
        return bz+value
    else:
        return value

def get_seq( seq , con = None ):
    """
        1 不用隐式的seq名称，显式比隐式要好
        2 能支持更多的应用环境。采取传入con的方式。
    """
    if con:
        cur = con.cursor()
        return _get_seq( cur , seq )
    else:
        with connection() as con:
            cur = con.cursor()
            return _get_seq( cur , seq )

def _get_seq( cur , seq ):
    sql_lsh = " select %s.nextval from dual"%seq
    cur.execute(sql_lsh)
    lsh = cur.fetchone()
    return lsh[0]

def get_lsh_old( cs , min = 1 , max = 100000 ):
    with connection() as db:
        row = db.execute_sql( "select dm , lsh from zd_lsh where dm = %(1)s for update" , { '1': cs } )
        if not row:
            db.execute_sql( "insert into zd_lsh( dm , lsh ) values ( %(1)s , %(2)s ) " , { '1': cs , '2': min } )
            return min
        else:
            lsh = row[0]['lsh'] + 1
            if lsh < min:
                lsh = min
            if lsh > max:
                lsh = min
            db.execute_sql( 'update zd_lsh set lsh = %(1)s where dm = %(2)s' , { '1': lsh , '2': cs } )
            return lsh

def __get_lsh( cs , min , max  ,cu ):
    cu.execute( "select dm , lsh from zd_lsh where dm = :1 for update" , [ cs ] )
    row = cu.fetchone()
    if row is None:
        cu.execute( "insert into zd_lsh( dm , lsh ) values ( :1 , :2 ) " , [ cs , min ] )
        return min
    else:
        lsh = row[1] + 1
        if lsh < min:
            lsh = min
        if lsh > max:
            lsh = min
        cu.execute( 'update zd_lsh set lsh = :1 where dm = :2' , [ lsh , cs ] )
        return lsh

def __get_lsh_pgsql( cs , min , max  ,cu ):
    cu.execute( "select dm , lsh from zd_lsh where dm = %(1)s for update" , { '1': cs } )
    row = cu.fetchone()
    if row is None:
        cu.execute( "insert into zd_lsh( dm , lsh ) values ( %(1)s , %(2)s ) " , { '1': cs , '2': min } )
        return min
    else:
        lsh = row[1] + 1
        if lsh < min:
            lsh = min
        if lsh > max:
            lsh = min
        cu.execute( 'update zd_lsh set lsh = %(1)s where dm = %(2)s' , { '1': lsh , '2': cs } )
        return lsh

def get_lsh( cs , min = 1 , max = 100000 ,cur = None ):
    """
    获取流水号，从zd_lsh数据表中
    """
    if cur:
        return __get_lsh_pgsql( cs,min,max,cur ) if settings.DB_TYPE == "postgresql" else __get_lsh( cs,min,max,cur )
    else:
        with connection() as con:
            cur = con.cursor()
            return __get_lsh_pgsql( cs, min, max, cur ) if settings.DB_TYPE == "postgresql" else __get_lsh( cs,min,max,cur )

#组成GTP文件名用
def get_gtp_lsh( cur = None ):
    if not cur:
        with connection() as con:
            cur = con.cursor()
    sql = " select seq_gtp_lsh.nextval from dual "
    cur.execute( sql )
    lsh = cur.fetchone()[0]
    return lsh

#组成GTP文件名用
def get_wj_pch( rq,cur = None ):
    """
    获取登记文件登记簿记录时所需的批次号
    """
    if cur:
        lsh = get_lsh( 'wj_pch', cur=cur  )
    else:
        lsh = get_lsh( 'wj_pch' )
    pch = '%s%06d' % ( rq ,int(lsh) )
    return pch
    
def get_zwrq( cur=None, fmt='%Y%m%d'):
    """
        根据系统版本获取账务日期
        并根据格式校验账务日期是否正确
        cur 游标，如果不在事务下，可以不必传送此项
        fmt 账务日期格式，系统校验账务日期是否满足此格式
    """
    zwrq = ''
    try:
        if not cur:
            with connection() as con:
                cur = con.cursor()
                rs = sql_execute( cur, sql )
                while rs.next():
                    zwrq = rs.getString( 'zwrq' )
        else:
            rs = sql_execute( cur, sql )
            while rs.next():
                zwrq = rs.getString( 'zwrq' )
        
        # 校验账务日期格式是否正确
        import datetime
        datetime.datetime.strptime( zwrq, fmt )
        
        return zwrq
    except:
        raise RuntimeError( '获取账务日期非法:%s  FMT[%s]' % ( zwrq, fmt ) )
        
def e_beai_money( value, buflen, decimaldigit=3, sign = 'R' ):
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
        return value+bz
    elif sign == 'L':
        return bz+value
    else:
        return value

def get_seq( seq , con = None ):
    """
        1 不用隐式的seq名称，显式比隐式要好
        2 能支持更多的应用环境。采取传入con的方式。
    """
    if con:
        cur = con.cursor()
        return _get_seq( cur , seq )
    else:
        with connection() as con:
            cur = con.cursor()
            return _get_seq( cur , seq )

def _get_seq( cur , seq ):
    sql_lsh = " select %s.nextval from dual"%seq
    cur.execute(sql_lsh)
    lsh = cur.fetchone()
    return lsh[0]

def get_xtlsh():
    """ 获取系统流水号 """
    return get_seq( 'jy_ls_lsh_seq' )


#####def _set_xtcs(csdm , csz ,con):
#####    """
#####        # 为了get_xtcs和set_xtcs共用同一个赋值语句
#####    """
#####    cur = con.cursor()
#####    cur.execute( "update gl_csdy set value = '%s' where csdm = '%s' and lx = '1'"%(csz , csdm) )
#####    if cur.rowcount == 0:
#####        # 状态（1：启用），类型（1：系统参数） 来源：2（铺底）
#####        cur.execute( "insert into gl_csdy ( id ,csdm ,value ,csms ,lx ,zt ,ly ,ssid ,czr ,czsj ,wym) values( '%s', '%s', '%s' ,'','1','1','1','','','','' )"%(csdm , csdm , csz) )
#####
#####def get_xtcs( csdm , default = '' ):
#####    """
#####    获取系统参数。
#####    参数：
#####        csdm    参数代码
#####        default 默认值
#####    以字符串形式返回
#####    """
#####    with connection() as con:
#####        cur = con.cursor()
#####        # 只取类型为系统参数的参数信息
#####        cur.execute( "select value from gl_csdy where csdm = '%s' and lx = '1'"%(csdm) )
#####        row = cur.fetchone()
#####        if not row:
#####            csz = default
#####            _set_xtcs(csdm , csz ,con)
#####        else:
#####            csz = row[0]
#####        return csz
#####
#####def set_xtcs( csdm , csz ):
#####    """
#####    设置系统参数
#####    参数：
#####        csdm    参数代码
#####        csz     参数值（字符串形式）
#####    """
#####    with connection() as con:
#####        _set_xtcs(csdm , csz ,con)


def ins_lsz( lsh, jyrq, jysj, jym, jgdm=None, gyh=None ):
    """
    登记交易流水jy_ls
    参数|建议取值：
        lsh   交易流水号           jyzd.SYS_XTLSH
        jyrq  交易日期             jyzd.SYS_JYRQ
        jysj  交易时间
        jym   交易码
        jgdm  发起机构代码
        gyh   操作柜员
    """
    with connection() as db:
        db.execute_sql( """insert into jy_ls ( lsh , jyrq , jysj , jyfqsj , jym , jgdm , gyh , zt )
                               values ( %(1)s , %(2)s , %(3)s , %(4)s , %(5)s , %(6)s , %(7)s , %(8)s )""" ,
                         { '1':lsh , '2':jyrq , '3':jysj , '4':e_now() , '5':jym , '6':jgdm , '7':gyh , '8':'00' } )

def upd_lsz( rq, lsh, **d ):
    """
    更新交易流水的字段
    参数：
        rq  交易日期取值jyzd.SYS_JYRQ
        lsh 交易流水号jyzd.SYS_XTLSH
        d  要更新的字段字典，型如：{ field:value, }
    """
    try:
        with connection() as con:
            lsh = d.pop( 'lsh', lsh ) # 流水号不可被更新，故从d中弹出
            cu = con.cursor()
            set_clause = []
            for k,v in d.items():
                set_clause.append( "%s =%s" % ( k , repr(v) ) )
            cu.execute( "update jy_ls set %s where jyrq = '%s' and lsh = %d" % ( ','.join( set_clause ), rq, int(lsh) ) )
    except:
        print( '更新流水[%s]失败' , lsh )
        #log_exception( '更新流水[%s]失败' , lsh )
        raise

def ins_htrz( jyzd , htjd, txjdbh, jbjd=None , htxx='' , **kwargs ):
    """
    登记回退日志，由于回退日志一定同tongser控制的交易挂钩，因此，我们自动从jyzd中提取数据已减轻调用的复杂度。
    jyzd：
        lsh   交易流水号jyzd.SYS_XTLSH
        jyrq  交易日期取值jyzd.SYS_JYRQ
        xh    本次交易中该冲正节点的序号，对应jyzd.SJ_HTXH。注意，该字段可以用来在_pre_end节点中自动判断是否需要冲正。
        jym   交易码
        jdmc  固定取值 jyzd.MODNAME+ '.' + jyzd.FUNCNAME
    htjd  回退打包节点 格式：mod.func
    txjdbh 通讯节点编号
    jbjd  解包节点 格式：mod.func
    htxx  回退信息，逗号分割的字符串，用于从jyzd中提取回退数据用。
    kwargs 额外的回退信息，不再交易字典中的数据。
    """
    # 1 初始化回退数据
    data = {}
    data.update( kwargs ) # 先初始化补充数据
    if htxx:
        for k in htxx.split( ',' ):
            k = k.strip()
            data[ k ] = jyzd[ k ]
    
    htxx = dbbinary( pickle_dumps( data ) )
    # 2 处理回退序号
    if jyzd.SJ_HTXH is None:
        jyzd.SJ_HTXH = '1'
    else:
        jyzd.SJ_HTXH = str( int( jyzd.SJ_HTXH ) + 1 )
    
    with connection() as db:
        db.execute_sql( """insert into jy_htrz( lsh, jyrq, xh, rq, jym, jdmc, htxx, htjd, txjdbh, jbjd )
                                      values( %(1)s , %(2)s , %(3)s , %(4)s , %(5)s , %(6)s , %(7)s , %(8)s , %(9)s , %(10)s )""" %
                     { '1': jyzd.SYS_XTLSH , '2': jyzd.SYS_JYRQ , '3': int(jyzd.SJ_HTXH) , '4': e_now(), '5': jyzd.SYS_JYM , '6': jyzd.MODNAME + '.' + jyzd.FUNCNAME ,
                       '7': htxx, '8': htjd , '9': txjdbh , '10': jbjd } )

def get_xtcs( jyzd, csdm_lst, cur=None ):
    """系统数获取函数
        jyzd:交易字典
        csdm_lst:要获取的参数代码列表
        cur：数据库链接句柄
    """
    sql =  "select csdm,value from gl_csdy where csdm in ( '%s' ) and lx = '1'" % "','".join( csdm_lst )
    #log_info( '获取业务参数sql[%s]', sql )
    if cur:
        cur.execute( sql )
        rs = cur.fetchall()
    else:
        with connection() as con:
            cur = con.cursor()
            cur.execute( sql )
            rs = cur.fetchall()
    if len( rs ) != len( csdm_lst ):
        raise RuntimeError("业务参数未配置！")
    for row in rs:
        jyzd[ row[0] ] = row[1]

def set_xtcs( jyzd, csdm_lst, cur=None ):
    """系统参数设置函数
        jyzd:交易字典
        csdm_lst:要设置的参数代码列表
        cur：数据库链接句柄
    """
    def _upd( cur ):
        for items in csdm_lst:
            if jyzd[items] is None:
                raise RuntimeError("获取参数值错[%s]！"%items)
            sql = "update gl_csdy set value='%s' where csdm='%s' and lx = '1' " % ( jyzd[items], items )
            #log_info( '业务参数配置sql[%s]', sql )
            cur.execute( sql )
    if cur:
        _upd( cur )
    else:
        with connection() as con:
            cur = con.cursor()
            _upd( cur )

# call_jy异步
def call_jy_asy( buf ):
    """
    封装自动发起交易，二次开发者只需录入报文即可，发送方为核心管理端通讯
    """
    # 自动发起交易的通讯节点代码--ZDFSSVR,不用get_xtcs方式，因为还要考虑游标，call_jy_asy(),就要传cur,为了不让那么复杂，直接写死即可
    #r_d = {}
    #csdm = "CALL_JY_COMMID"
    #get_xtcs(r_d ,[csdm])
    #commid = r_d.get(csdm ,"")
    call_jy_noreply( 'ZDFSSVR' ,buf )
    
def send_msg( dxnr,phone_lst,jyzd,cur=None ):
    """
    往jy_dxxx表中插入数据，等待后台轮询生成短信文件
    dxnr:要发送的短信内容
    phone_lst:电话列表，例如：186111111111,187111111111
    cur:数据库游标
    """
    from ops.trans.utils import get_xtcs
    PHONE_NO =  [ sjh for sjh in phone_lst.split(',') if sjh ] if phone_lst else [] 
    get_xtcs( jyzd, ['DX_JGDM'], cur=cur )      # 短信机构码
    import datetime
    sj = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    dxnr = '[%s]' % sj + dxnr
    if len(PHONE_NO):
        for sjh in PHONE_NO:
            # 往短信信息表中插入信息
            insert_dxxx( sjh, dxnr,jyzd.DX_JGDM,cur=cur )

def insert_dxxx( sjh, xxnr, jgdm, jyrqsj='', yxj='00', stbz='0', cur=None ):
    """
    向短信信息记录表中插入数据(函数自身创建数据库链接)
    sjh:手机号
    xxnr:短信内容
    jgdm:机构代码
    jyrqsj:交易日期时间
    yxj:优先级
    stbz:收条标志
    """
    if not jyrqsj:
        import datetime
        jyrqsj = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if cur:
        __insert_dxxx( sjh,xxnr,jyrqsj,yxj,stbz,jgdm,cur )
    else:
        with connection() as con:
            cur = con.cursor()
            __insert_dxxx( sjh,xxnr,jyrqsj,yxj,stbz,jgdm,cur )

def __insert_dxxx( sjh,xxnr,jyrqsj,yxj,stbz,jgdm,cur ):
    """
    插入短信
    """
    sql = """insert into jy_dxxx(id, sjh, xxnr, yxj, stbz, jgdm, jyrqsj, fsbz) values( jy_dxxx_id_seq.nextval, '%s', '%s', '%s', '%s', '%s', '%s', '0')
          """ % ( sjh, xxnr, yxj, stbz, jgdm, jyrqsj )
    if settings.DB_TYPE == "postgresql":
        sql = """insert into jy_dxxx(id, sjh, xxnr, yxj, stbz, jgdm, jyrqsj, fsbz) values( nextval('jy_dxxx_id_seq'), '%s', '%s', '%s', '%s', '%s', '%s', '0')
          """ % ( sjh, xxnr, yxj, stbz, jgdm, jyrqsj )
    cur.execute( sql )

def ins_wjcldjb( ywlx, wjm, djrq, djsj, cur=None ):
    """
    登记文件处理登记表，预登记，初始状态全都默认为99 
    ywlx  业务类型
    wjm   文件名
    djrq  登记日期
    djsj  登记时间
    """    
    id = 0
    data = [ id, ywlx, wjm, djrq, djsj, '%s %s' % ( djrq, djsj ) ] # 构建登记数据库的列表
    sql_sel = "select jy_wjcldjb_id_seq.nextval id from dual"
    sql_ins = """insert into jy_wjcldjb( id, ywlx, wjm, zt, djrq, djsj, updtime )
            values( :1, :2, :3, '99', :4, :5, :6 )
          """
    if cur:
        cur.execute( sql_sel )
        row = cur.fetchone()
        data[0] = id = row[0]
        # 2.登记文件处理登记表
        cur.execute( sql_ins, data )
    else:
        with connection() as con:
            cur = con.cursor()
            cur.execute( sql_sel )
            row = cur.fetchone()
            data[0] = id = row[0]
            # 2.登记文件处理登记表
            cur.execute( sql_ins, data )
    return id

def upd_wjcldjb( id, cur=None, **kwargs ):
    """
    更新文件处理登记表
    id  文件处理登记表中的唯一索引
    cur:数据库游标
    d  要更新的字段字典，型如：{ field : value, }
    """
    id = kwargs.pop( 'id', id ) # id不可被更新，故从d中弹出
    kwargs.pop( 'wjm', '' )          # 文件名
    kwargs.pop( 'ywlx', '' )         # 业务类型不可被更新
    kwargs.pop( 'djrq', '' )         # 登记日期不可被更新
    kwargs.pop( 'djsj', '' )         # 登记时间不可被更新
    # 控制更新sql，使用 set a = :1 , b = :2 的方式
    
    set_keys   = []
    set_values = []
    i = 1
    for k, v in kwargs.items():
        set_keys.append( "%s = :%d" % ( k , i ) )
        set_values.append( v )
        i += 1
    sql = " update jy_wjcldjb set %s where id=%d " % ( ','.join( set_keys), int( id ) )
    if cur:
        cur.execute( sql, set_values )
    else:
        with connection() as con:
            cur = con.cursor()
            cur.execute( sql, set_values )

def ins_jycz( lsh, jyrq, cs=0, czwz=0, zt='0' ):
    """
    登记交易流水jy_ls
    参数|建议取值：
        rq       原流水交易日期     jyzd.SYS_JYRQ
        ylsh     原流水号           jyzd.SYS_XTLSH
        cs       冲正次数：初始为0
        czwz     冲正位置：记录已经成功冲正了几个节点，初始为0
        zt       当前冲正状态: 
                    0 待冲正
                    1 冲正中
                    2 冲正成功
                    9 错误不再冲正
        updtime  更新时间（当前时间）
    """
    with connection() as con:
        sql = """ insert into JY_CZ( rq, ylsh, cs, czwz, zt, updtime )
                               values ( %(jyrq)s , %(lsh)s , %(cs)s , %(czwz)s , %(zt)s , %(updtime)s )"""
        d = dict( jyrq=jyrq , lsh=lsh , cs=cs , czwz=czwz , zt=zt , updtime=e_now().decode('utf8') )
        con.execute_sql( sql , d )

if __name__=="__main__":
    print('----------',get_xtcs('xtrq'))
    set_xtcs('xtrq','20150320')
    print('----------',get_xtcs('xtrq'))
    #get_xtcs('xtrq')
    #ins_lsz( 38, '', '2015-03-20 15:10:25.467869', 'lt001' )
    #upd_lsz('jyrq',3,**{'xym':'0'})
