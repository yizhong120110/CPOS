# -*- coding: utf-8 -*-
from ops.trans.cz import qx_xh_cz

def ins_jkjy_ls( jyzd , bz,cur = None ):
    """
    往接口校验流水中插入信息
    """
    import uuid
    sql = "insert into gl_jkjy_ls(id,jylsh,cd_dfjymc,cd_txbm,zddm,zdmc,jymc,jyms,jyrq,jysj,jyjg,jyjgsm) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(uuid.uuid4().hex,jyzd.SYS_XTLSH,jyzd.DFJYMC,jyzd.TXZLC_BM,jyzd.CHECK_ZD,jyzd.CHECK_ZDMS,jyzd.CHECK_GZMC,'值：[%s]'%jyzd.CHECK_NR,jyzd.SYS_JYRQ,jyzd.SYS_JYRQSJ,jyzd.CHECK_ZXJG_DB,jyzd.CHECK_ZXJGSM)
    if cur:
        if bz == '1':
            tlog.log_info('插入接口校验流水SQL：%s'%sql)
        cur.execute( sql )
    else:
        # 插入接口校验流水
        with connection() as con:
            cur = con.cursor()
            if bz == '1':
                tlog.log_info('插入接口校验流水SQL：%s'%sql)
            cur.execute( sql )
    
def exce_func( jyzd,zd,nr,gzmc,zjcs = '{}',zdms = '',bz = '0' ):
    """
    1.执行校验函数
    2.将函数结果插入到接口校验流水中
    zd:待校验的字段
    nr:待校验的内容
    gzmc:待校验的规则名称
    zjcs:待校验内容的追加参数
    zdms:待校验的字段描述
    """
    from ops.trans.check_util import check_zh,check_kh,check_zjlx,check_zjhm,check_yzbm,check_je,check_dh,check_rq
    # 校验字段
    jyzd.CHECK_ZD = zd
    # 校验内容
    jyzd.CHECK_NR = nr
    # 校验规则名称
    jyzd.CHECK_GZMC = gzmc
    # 校验追加参数
    jyzd.CHECK_ZJCS = zjcs
    # 校验字段描述
    jyzd.CHECK_ZDMS = zdms
    jyzd.CHECK_ZXJGSM = ''
    d = eval(jyzd.CHECK_ZJCS) if jyzd.CHECK_ZJCS else {}
    if bz == '1':
        tlog.log_info('查询接口校验信息：nr:[%s],d[%s],'%(jyzd.CHECK_NR,d))
    np = {jyzd.CHECK_GZMC:eval(jyzd.CHECK_GZMC)}
    if bz == '1':
        tlog.log_info('执行函数信息【%s】'%( 'zxjg_tupl = ' + jyzd.CHECK_GZMC + "('%s',%s)"%(str(jyzd.CHECK_NR),d) ))
    exec( """zxjg_tupl = """ + jyzd.CHECK_GZMC + """('%s',%s)"""%(str(jyzd.CHECK_NR),d) ,np  ) 
    # 执行结果 True(校验成功)，False(执行失败)
    zxjg = np['zxjg_tupl'][1]
    # 执行结果说明 返回执行结果说明
    jyzd.CHECK_ZXJGSM = np['zxjg_tupl'][0]
    # 存放校验错误信息
    err_str = ''
    # 执行结果-存放到数据表中的
    jyzd.CHECK_ZXJG_DB = ''
    flag = '1'
    if not zxjg:
        # 校验失败，登记日志信息
        if bz == '1':
            tlog.log_info('字段[%s:%s]进行接口校验[%s]时失败，失败信息为[%s],追加参数[%s]'%(jyzd.CHECK_ZD,jyzd.CHECK_NR,jyzd.CHECK_GZMC,jyzd.CHECK_ZXJGSM,'' if jyzd.CHECK_ZJCS == '{}' else jyzd.CHECK_ZJCS))
        flag = '0'
        # 执行结果-数据表中展示：0失败
        jyzd.CHECK_ZXJG_DB = '0'
        err_str = jyzd.CHECK_ZXJGSM 
    else:
        # 执行结果-数据表中展示：1：成功
        jyzd.CHECK_ZXJG_DB = '1'
        # 校验成功，登记日志信息
        if bz == '1':
            tlog.log_info('字段[%s:%s]进行接口校验[%s]成功,追加参数[%s]'%(jyzd.CHECK_ZD,jyzd.CHECK_NR,jyzd.CHECK_GZMC,'' if jyzd.CHECK_ZJCS == '{}' else jyzd.CHECK_ZJCS))
    ins_jkjy_ls( jyzd ,bz)
    return flag,err_str
    
def pre_node():
    """
    预处理节点
    """
    import uuid
    # 获取当前执行的通讯子流程编码,根据节点跟踪获取SYS_JYJDGZ
    # SYS_JYJDGZ组成形式：[gt0012,jystart[0]:BEAI540012,zlcstart[0]:]'
    txzlc_bm = jyzd.SYS_JYJDGZ.split(',')[-2]
    jyzd.TXZLC_BM = txzlc_bm.split(':')[-1]
    tlog.log_info('获取交易跟踪日志信息[%s],通讯子流程编码[%s]'%(jyzd.SYS_JYJDGZ,jyzd.TXZLC_BM))
    # 1、获取通讯子流程信息
    with connection() as con:
        cur = con.cursor()
        cur.execute( "select a.dblx, a.dbssid, a.txglid, a.cssj, a.jkqyzt, a.dbjdid, a.dfjymc from gl_cdtx a, gl_zlcdy b where  a.zlcdyid = b.id and b.bm = '%s'"%jyzd.TXZLC_BM )
        sql = "select a.dblx, a.dbssid, a.txglid, a.cssj, a.jkqyzt, a.dbjdid, a.dfjymc from gl_cdtx a, gl_zlcdy b where  a.zlcdyid = b.id and b.bm = '%s'"%jyzd.TXZLC_BM
        tlog.log_info( '通讯子流程查询SQL【%s】'%sql )
        row = cur.fetchone()
        if not row:
            jyzd.SYS_RspCode = 'TS9999'
            jyzd.SYS_RspInfo = '通讯子流程未配置对应的通讯信息，执行失败'
            tlog.log_info('通讯子流程未配置对应的通讯信息，执行失败')
            return -1
        else:
            # 将通讯信息赋给交易字典
            jyzd.DBLX,jyzd.DBSSID,jyzd.TXGLID,jyzd.TIMEOUT,jyzd.JKQYZT,jyzd.DBJDID,jyzd.DFJYMC = row[0],row[1],row[2],row[3],row[4],row[5],row[6]
            tlog.log_info( '通讯子流程查询信息：jyzd.JKQYZT[%s],jyzd.DBLX【%s】，jyzd.DBSSID【%s】,%s,%s'%(jyzd.JKQYZT, jyzd.DBLX,jyzd.DBSSID,jyzd.DBSSID == 'None',type(jyzd.DBSSID) ) )
    # 2、判断是否有挡板，若有挡板，直接反馈挡板信息
    if jyzd.DBSSID != 'None' and jyzd.DBSSID :
        
        # 根据挡板类型获取挡板信息
        tlog.log_info('有挡板信息，获取挡板信息')
        with connection() as con:
            cur = con.cursor()
            sql_lst = []  # 存放要执行的sql列表
            if jyzd.DBLX == '1':
                # 手工创建的挡板
                sql_ys = "select ysmc, ysz from gl_dbys where dbdyid = '%s'"%jyzd.DBSSID
                tlog.log_info('获取手工创建挡板信息SQL：%s'%sql_ys)
                cur.execute( sql_ys )
                rs = cur.fetchall()
                for row in rs:
                    jyzd[ row[0] ] = row[1]
                    # 登记挡板流水sql，类型为1-要素，2-返回值
                    sql = "insert into gl_dbls(id,lsh,jyrq,ysmc,ysz,lx,dblx,cd_dfjymc,cd_txbm) values('%s','%s','%s','%s','%s','1','%s','%s','%s')"%(uuid.uuid4().hex,jyzd.SYS_XTLSH,jyzd.SYS_JYRQ,row[0],row[1],jyzd.DBLX,jyzd.DFJYMC,jyzd.TXZLC_BM)
                    sql_lst.append(sql)
                sql_fhz = "select fhz from gl_dbdy where id = '%s'"%jyzd.DBSSID
                tlog.log_info('获取手工创建挡板返回值SQL：%s'%sql_fhz)
                cur.execute( sql_fhz )
                row = cur.fetchone()
                # 将返回值登记到挡板流水表中
                sql = "insert into gl_dbls(id,lsh,jyrq,ysmc,ysz,lx,dblx,cd_dfjymc,cd_txbm) values('%s','%s','%s','%s','%s','2','%s','%s','%s')"%(uuid.uuid4().hex,jyzd.SYS_XTLSH,jyzd.SYS_JYRQ,'SYS_JYJDZXJG',row[0],jyzd.DBLX,jyzd.DFJYMC,jyzd.TXZLC_BM)
                sql_lst.append(sql)
                for ins_sql in sql_lst:
                    cur.execute( ins_sql )
                return row[0]
            elif jyzd.DBLX == '2':
                # 测试案例挡板
                sql_ys = "select ysdm, ysz from gl_jdcsalys where jdcsalzxbz = '%s'"%jyzd.DBSSID
                tlog.log_info('获取测试案例挡板信息SQL：%s'%sql_ys)
                cur.execute( sql_ys )
                rs = cur.fetchall()
                for row in rs:
                    jyzd[ row[0] ] = row[1]
                    # 登记挡板流水sql，类型为1-要素，2-返回值
                    sql = "insert into gl_dbls(id,lsh,jyrq,ysmc,ysz,lx,dblx,cd_dfjymc,cd_txbm) values('%s','%s','%s','%s','%s','1','%s','%s','%s')"%(uuid.uuid4().hex,jyzd.SYS_XTLSH,jyzd.SYS_JYRQ,row[0],row[1],jyzd.DBLX,jyzd.DFJYMC,jyzd.TXZLC_BM)
                    sql_lst.append(sql)
                sql_fhz = "select fhz from gl_jdcsalzxbz where id = '%s'"%jyzd.DBSSID
                tlog.log_info('获取测试案例挡板返回值SQL：%s'%sql_fhz)
                cur.execute( sql_fhz )
                row = cur.fetchone()
                # 将返回值登记到挡板流水表中
                sql = "insert into gl_dbls(id,lsh,jyrq,ysmc,ysz,lx,dblx,cd_dfjymc,cd_txbm) values('%s','%s','%s','%s','%s','2','%s','%s','%s')"%(uuid.uuid4().hex,jyzd.SYS_XTLSH,jyzd.SYS_JYRQ,'SYS_JYJDZXJG',row[0],jyzd.DBLX,jyzd.DFJYMC,jyzd.TXZLC_BM)
                sql_lst.append(sql)
                for ins_sql in sql_lst:
                    cur.execute( ins_sql )
                return row[0]
            else:
                jyzd.SYS_RspCode = 'TS9999'
                jyzd.SYS_RspInfo = '无法识别的挡板类型，执行失败'
                tlog.log_info('无法识别的挡板类型，执行失败')
                return -1
    # 3、判断接口启用状态，若为启用，则进行接口有效性校验
    if jyzd.JKQYZT == '1':
        tlog.log_info('接口校验状态为启用，进行接口有效性校验')
        with connection() as con:
            cur = con.cursor()
            # 根据打包节点ID获取接口校验信息
            sql = "select bm, zjcs, ssgzmc, ysmc from gl_jdys where jddyid = '%s' and jkjy = '1'"%jyzd.DBJDID
            tlog.log_info('查询接口校验信息SQL：%s'%sql)
            cur.execute( sql )
            rs = cur.fetchall()
        flag = '1'   # 为1时表示校验成功
        # 校验错误信息存放
        err_lst = []
        for row in rs:
            try:
                tlog.log_info('查询接口校验信息：row:[bm:%s,zjcs:%s,ssgzmc:%s,ysmc:%s]'%(row[0],row[1],row[2],row[3]))
                zjcs = row[1] if row[1] != None else '{}'
                ysmc = row[3] if row[3] != None else ''
                flag_tmp,err_str = exce_func( jyzd,row[0],jyzd[row[0]],row[2],zjcs,ysmc,'1' )                
                err_lst.append( err_str )
                flag = flag_tmp if flag_tmp == '0' else flag
            except Exception as e:
                jyzd.SYS_RspCode = 'TS9999'
                jyzd.SYS_RspInfo = '接口校验异常'
                tlog.log_info('校验异常，异常信息为[%s]'%e)
                return -1
        if flag != '1':
            jyzd.SYS_RspCode = 'TS0004'
            jyzd.SYS_RspInfo = '接口校验失败[%s]'%",".join( err_lst )
            tlog.log_info('接口校验失败[%s]'%",".join( err_lst ))
            return -1
    # 4、获取通讯节点所需信息：通讯节点编码、要发送的报文、IP、端口、超时时间
    tlog.log_info('开始获取通讯节点所需信息')
    with connection() as con:
        cur = con.cursor()
        # 获取通讯编码
        cur.execute( "select bm,txwjmc,txlx from gl_txgl where id = '%s'"%jyzd.TXGLID )
        row = cur.fetchone()
        jyzd.TXJD = row[0]  # 通讯编码
        jyzd.TXWJMC = row[1].split('.')[0] if row[1] else row[1] # 通讯文件名称
        jyzd.TXLX = row[2]  # 通讯类型
        
        # 检查通讯参数中是否有（IP、PORT）
        cur.execute( "select count(0) as num from gl_csdy where lx = '4' and ssid = '%s' and ( csdm = 'IP' or csdm = 'PORT' )"%jyzd.TXGLID )
        rs = cur.fetchone()
        num = rs[0]
        if num < 2:
            jyzd.SYS_RspCode = 'TS0004'
            jyzd.SYS_RspInfo = '未定义通讯的IP或PORT'
            tlog.log_info('未定义通讯的IP或PORT')
            return -1
    return 2

def call_node():
    # 组织通讯所需的参数        
    # 获取通讯参数（IP、PORT、FTP信息）
    kwd = {}  # 存放参数代码列表
    # 将报文，超时时间，文件放到kwd字典中，文件若是多个，用+号连接
    kwd['BUF'] = jyzd.SYS_YFSDBW   # 要发送的报文
    kwd['TIMEOUT'] = jyzd.TIMEOUT  # 超时时间
    kwd['FILENAME'] = jyzd.SYS_YFSDWJ  # 要发送的文件
    kwd['KWARGS'] = jyzd.SYS_KWARGS    # 通讯需要的辅助字典-'{}'
    with connection() as con:
        cur = con.cursor()
        cur.execute( "select csdm, value from gl_csdy where lx = '4' and ssid = '%s' "%jyzd.TXGLID )
        rs = cur.fetchall()
        for row in rs:
            kwd[ row[0] ] = row[1]
    
    from ops.core.rpc import message_to_ocm
    senddic = {}  # 核心需要的信息
    senddic['kwd'] = kwd              # 通讯字典
    tlog.log_info('call_node发送的信息为[%s]'%senddic)
    # 冲正处理
    jyzd.SYS_JSDDBW = cl_zzcz()
    if jyzd.SYS_JSDDBW == '1':
        jyzd.SYS_JSDDBW = message_to_ocm(senddic,jyzd.TXWJMC,int(jyzd.TIMEOUT)+5)
        tlog.log_info('call_node接收的信息为[%s]'%jyzd.SYS_JSDDBW)
        # 当SJ_XH 为1时， 通讯操作时，反馈 -1，-2，-3 时，为交易失败，需要将jyzd.ISSAF置为no
        # 对于交易中失败情况，需要二次开发者在自己节点代码中重新定义ISSAF为False，
        # 因为不同的通讯，解包不同，判断交易失败也不同
        if jyzd.SYS_JSDDBW in ( '-1', '-2', '-3' ):
            tlog.log_info('本次通讯失败')
            if  jyzd.SJ_XH=='1':
                tlog.log_info('本次通讯为第一个冲正通讯，通讯失败不需要做冲正，所以将ISSAF置为no')
                jyzd.ISSAF = 'no'
            if jyzd.SJ_XH and int(jyzd.SJ_XH) > 0:
                tlog.log_info( '冲正序号[%s]大于0，本次通讯失败，此通讯不需要冲正，需要将序号减一,并删除本通讯对应冲正步骤' % jyzd.SJ_XH )
                # 删除冲正步骤
                with connection() as con:
                    cur = con.cursor()
                    qx_xh_cz( cur, jyzd.SYS_XTLSH, jyzd.SYS_JYRQ, jyzd.SJ_XH )
                # 冲正序号减一
                jyzd.SJ_XH = int( jyzd.SJ_XH ) - 1
    else:
        tlog.log_info('call_node冲正判断出现异常情况：%s' % jyzd.SYS_JSDDBW)
    return 0

def cl_zzcz():
    """
    # 处理自动冲正：
    1. 判断是否有配置冲正子流程
    2. 判断htxx是否有值
    3. 新增回退日志表（JY_HTRZ）
    4. 更新：jyzd.SJ_XH， jyzd.ISSAF
    返回值：
        1：正常
        -99：处理冲正操作出现异常
        -98：配置重置子流程但未定义回退信息
    
    各个通讯解包公共函数中需要添加的代码：
    elif buf in ('-99',):
        # 处理冲正操作失败
        tlog.log_info('beai通讯校验，反馈[%s]，处理冲正操作失败' % buf )
        xym = '-1'
        msg = 'beai通讯处理冲正操作失败'
    elif buf in ('-98',):
        # 处理自动冲正：回退信息未定义
        tlog.log_info('beai通讯校验，反馈[%s]，处理自动冲正：回退信息未定义' % buf )
        xym = '-1'
        msg = 'beai通讯回退信息（jyzd.HTXX）未定义'
    
    
    """
    tlog.log_info('处理自动冲正：开始')
    try:
        with connection() as con:
            cur = con.cursor()
            # 判断是有有配置冲正信息
            sql_check = """ select czzlcdyid from gl_cdtx
                            where zlcdyid in (
                              select id from gl_zlcdy
                              where bm = '%s'
                              and lb = '1'
                            )""" % jyzd.TXZLC_BM
            tlog.log_info('处理自动冲正：判断是有有配置冲正信息sql[%s]' % sql_check)
            cur.execute( sql_check )
            rs = cur.fetchone()
            # 有配置冲正子流程
            if rs and rs[0]:
                # 冲正执行冲正子流程
                jyzd.HTZLCID = rs[0]
                tlog.log_info('处理自动冲正：存在冲正子流程：%s' % jyzd.HTZLCID)
                # 判断HTXX是否有值
                if jyzd.HTXX and jyzd.HTXX != '{}':
                    tlog.log_info('处理自动冲正：有登记回退信息[%s]' % jyzd.HTXX)
                    # 新增回退日志表（JY_HTRZ）
                    import pickle
                    htxx = pickle.dumps( jyzd.HTXX )
                    SJ_XH = jyzd.SJ_XH if jyzd.SJ_XH else 0
                    jyzd.SJ_XH = int(SJ_XH) + 1
                    sql_ins_htrz = """ insert into JY_HTRZ( lsh, jyrq, xh, rq, jym, jdmc, htxx, htzlcid ) 
                                    values( %s, '%s', %s, '%s', '%s', '%s', :htxx, '%s' )
                    """ % ( jyzd.SYS_XTLSH, jyzd.SYS_JYRQ, jyzd.SJ_XH, jyzd.SYS_XTRQ,
                            jyzd.SYS_JYM, jyzd.DFJYMC, jyzd.HTZLCID )
                    tlog.log_info('处理自动冲正：登记回退日志sql[%s]' % sql_ins_htrz)
                    cur.execute( sql_ins_htrz, { 'htxx': htxx } )
                    # 将是否记录回退操作记录标识置为yes
                    jyzd.ISSAF = 'yes'
                    # 清空回退信息
                    jyzd.HTXX = ''
                    return 1
                else:
                    tlog.log_info('处理自动冲正：回退信息未定义，反馈-98')
                    return -98
            else:
                tlog.log_info('处理自动冲正：未查询到冲正子流程，无需登记冲正日志')
                return 1
    except:
        # 创建连接失败
        tlog.log_exception( 'call_node 处理冲正操作失败：' )
        return -99

if __name__ == '__main__':
    pass