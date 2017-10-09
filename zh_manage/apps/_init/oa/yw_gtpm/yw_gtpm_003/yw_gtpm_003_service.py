# -*- coding: utf-8 -*-
# Action: 阈值检验流水
# Author: chengdg
# AddTime: 2015-04-25
# Standard: 注释仅能以“#”开头,sql可以是“--”；注释不能同代码在同一行
import pickle
from sjzhtspj import ModSql, logger
from sjzhtspj.common import ins_czrz, get_strftime,get_bmwh_bm, get_strftime2


def index_service():
    """
    # 初始化阈值检验流水页面数据准备 service
    """
    # 数据结构    
    data = {'ssyw':[{'id':'','ywmc':'请选择'}], 'jklx':[{'value':'','text':'请选择'}]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询对象类型
        ssyw = ModSql.yw_gtpm_003.execute_sql_dict(db, "data_ssyw", {})
        # 将查询结果放到结果集中
        data['ssyw'].extend(ssyw)
        data['jklx'].extend(get_bmwh_bm( '10019', db=db ))
    return data

def data_service( sql_data ):
    """
    # 文件登记表json数据 service
    # sql_data = { 'ssyw': ssyw, 'startJyrq': startJyrq, 'endJyrq': endJyrq, 'jklx': jklx, 'rn_start': rn_start, 'rn_end': rn_end }
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    # 清理为空的查询条件
    search_lst = [ 'ssyw', 'startJyrq', 'endJyrq', 'jklx' ]
    for k in list(sql_data.keys()):
        if k in search_lst and sql_data[k] == '':
            del sql_data[k]
    # 如果监控类型未选择时，则默认为bmwh表中10019定义的信息
    if 'jklx' in sql_data:
        sql_data['jklx'] = [ sql_data['jklx'] ]
    else:
        sql_data['jklx'] = [ xx_dic['value'] for xx_dic in get_bmwh_bm( '10019' ) ]
    # 数据库链接
    with sjapi.connection() as db:
        # 查询文件记录总条数
        total = ModSql.yw_gtpm_003.execute_sql(db, "data_count", sql_data)[0].count
        # 查询文件记录明细
        jbxx = ModSql.yw_gtpm_003.execute_sql_dict(db, "data_wjjl", sql_data)
        # 查询对象类型
        yw_lst = ModSql.yw_gtpm_003.execute_sql_dict(db, "data_ssyw")
        yw_dic = dict( [ ( obj['id'], obj['mc'] ) for obj in yw_lst ] )
        # 查询对象状态
        zt_lst = get_bmwh_bm( '10019', db=db )
        zt_dic = dict( [ ( obj['value'], obj['text'] ) for obj in zt_lst ] )
        # 组织数据结构
    connector = []
    for wjjl in jbxx:
        connector.append({'id':wjjl['id'], 'ywmc':yw_dic.get(wjjl['ssywid'],''), 'wjlx':wjjl['wjlx'], 'wjmc':wjjl['wjm'], 'djrq':wjjl['djrq'][:4]+'-'+wjjl['djrq'][4:6]+'-'+wjjl['djrq'][6:8], 'djsj':wjjl['djsj'][:2]+':'+wjjl['djsj'][2:4]+':'+wjjl['djsj'][4:6], 'pch':wjjl['pch'], 'updtime':wjjl['updtime'], 'zt': zt_dic.get(wjjl['zt'],''), 'ztbm':wjjl['zt']})
    # 将总条数放到结果集中
    data['total'] = total
    # 将查询详情结果放到结果集中
    data['rows'] = connector
    # 将查询到的结果反馈给view
    return data

def index_check_mxck_service( sql_data ):
    """
    # 查询明细页面跳转前的校验 service
    """
    # 初始化返回值
    data = {'state':True, 'msg':''}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询配置的查询扣款明细的sql语句
        data_sql = ModSql.yw_gtpm_003.execute_sql_dict( db, 'data_mxls_sql', sql_data )
        if not data_sql:
            data['state'] = False
            data['msg'] = '该业务未进行阈值校验业务配置，请先配置业务参数再处理！'
        return data

def index_mxck_service( data ):
    """
    # 初始化阈值检验流水页面数据准备
    """
    # 数据结构    
    data['zt'] = [{'value':'','text':'请选择'}]
    # 数据库链接
    with sjapi.connection() as db:
        # 查询对象状态
        data['zt'].extend(get_bmwh_bm( '10020', db=db ))
        
    return data
    
def data_mxck_service( sql_data ):
    """
    # 阈值校验流水明细查看json数据
    # sql_data = { 'wjid':wjid, 'ywlx': ywlx, 'sfzh': sfzh, 'khmc': khmc, 'zt': zt, 'rn_start': rn_start, 'rn_end': rn_end }
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    sub_sql = ""
    if sql_data['zt']:
        sub_sql += " and zt = %s " % sql_data['zt']  # 没采用冒号传值，是因为用db.execute不支持特殊的sql语句（例如:select count(0) as count from ( select mxbh as id,zczh as sfzh from test_pkmxb )where 1=1 and a.sfzh = :sfzh），下同
    else:
        sub_sql += " and zt in ('00','55','97','98') "
    if sql_data['ywlx']:
        sub_sql += " and ywlx like '%%%s%%' " % sql_data['ywlx']
    if sql_data['sfzh']:
        sub_sql += " and sfzh like '%%%s%%' " % sql_data['sfzh']
    if sql_data['khmc']:
        sub_sql += " and khmc like '%%%s%%' " % sql_data['khmc']
    # 获取定义sql
    cxmx_sql = ''
    with sjapi.connection() as db:
        # 查询对象类型
        ssyw_lst = ModSql.yw_gtpm_003.execute_sql_dict(db, "data_ssyw", {})
        # 查询配置的查询扣款明细的sql语句
        data_sql = ModSql.yw_gtpm_003.execute_sql_dict( db, 'data_mxls_sql', sql_data )[0]
        cxmx_sql = pickle.loads(data_sql['kkmxsjcxsql'].read()) if data_sql else ''
    # 根据sql获取数据
    # 每页显示条数
    total = 0
    # 当前页显示信息
    mxls = []
    with sjapi.connection() as con:
        cur = con.cursor()
        # 查询文件记录总条数
        # 2015-05-07 10:24 cdg 由于防注入机制，在xml中配置动态sql查询语句会报错,经与孝党商量决定拿出来放在service层组织sql语句
        total_sql = "select count(0) as count from ( %s ) where 1=1 %s " % ( cxmx_sql, sub_sql )
        # 执行db.execute时，sql_data中不能有多余的key值，否则报错
        cur.execute( total_sql, [sql_data['wjid']] )
        total = cur.fetchone()[0]
        # 查询文件记录明细
        # 数据结构 [{ywlsh:业务流水号，wjmc:文件名称，ywlx:业务类型，sfzh：三方账号，kkje:扣款金额，khmc:客户名称，zt：状态}]
        mxls_sub_sql = " (%s) a where 1=1 %s " % ( cxmx_sql, sub_sql )
        mxls_sql = "select *  from ( select a.* ,rownum rn from %s ) where rn >= %s and %s >= rn" % ( mxls_sub_sql, sql_data['rn_start'], sql_data['rn_end'] )
        # 执行db.execute时，sql_data中不能有多余的key值，否则报错
        logger.info( '查询明细sql：%s' %  mxls_sql )
        rs = sql_execute( cur, mxls_sql, [sql_data['wjid']] )
        while rs.next( ):
            mxls.append( rs.to_dict() )
    # 处理金额，仅显示小数点后2位
    for mx in mxls:
        if 'kkje' in list( mx.keys() ):
            mx['kkje'] = '%.2f'%float(mx['kkje'])
    # 将总条数放到结果集中
    data['total'] = total
    # 将查询详情结果放到结果集中
    data['rows'] = mxls
    # 将查询到的结果反馈给view
    return data
    
def edit_service( sql_data ):
    """
    # 批量置为失败/批扣  json数据
    """
    # 标志：批量置为批扣--'zwpk',批量置为失败--'zwsb'
    flag = sql_data['flag']
    wjid = sql_data['wjid']
    # 初始化返回值
    data = {'state':True, 'msg':('%s操作成功'%('批量置为失败' if flag=='zwsb' else '批量置为成功'))}
    Je = 0  # 初始化金额
    Bs = 0  # 初始化笔数
    now_time = get_strftime2()
    # 数据库链接
    if flag=='zwsb': # 批量置为失败
        with sjapi.connection() as db:
            for lsmx in eval(sql_data['mx']):
                up_zt = '98' if lsmx['zt'] == '55' else '97'
                data_sql = ModSql.yw_gtpm_003.execute_sql( db, 'zwsb_sql', { 'wjid': wjid } )[0]
                zwsb_sql = pickle.loads(data_sql['zwsbsql'].read()) if data_sql else ''
                cs_data = {'1': up_zt, '2': lsmx['id']}
                logger.info( '更新sql：%s' %  zwsb_sql )
                db.execute(zwsb_sql, cs_data)
                Je += float(lsmx['kkje'])
                Bs += 1
            # 更新文件登记簿中的总金额、总笔数
            re_data = ModSql.yw_gtpm_003.execute_sql_dict(db, "cx_sql", {'id':wjid})[0]
            sjkkzbs = re_data['sjkkzbs'] if re_data['sjkkzbs'] else 0
            sjkkzje = float(re_data['sjkkzje']) if re_data['sjkkzje'] else 0
            upd_data = {
            'sjkkzbs':int(sjkkzbs)-Bs,
            'sjkkzje':(sjkkzje-Je),
            'updtime':now_time,
            'id':wjid}
            ModSql.yw_gtpm_003.execute_sql( db, "upd_sql", upd_data )
    else:
        # 批量置为批扣
        with sjapi.connection() as db:
            for lsmx in eval(sql_data['mx']):
                up_zt = '00'
                data_sql = ModSql.yw_gtpm_003.execute_sql( db, 'zwpk_sql', { 'wjid': wjid } )[0]
                zwpk_sql = pickle.loads(data_sql['zwpksql'].read()) if data_sql else ''
                cs_data = {'1': up_zt, '2': lsmx['id']}
                logger.info( '更新sql：%s' %  zwpk_sql )
                db.execute(zwpk_sql, cs_data)
                if lsmx['zt'] in ['97','98']:
                    Je += float(lsmx['kkje'])
                    Bs += 1
            # 更新文件登记簿中的总金额，总笔数
            re_data = ModSql.yw_gtpm_003.execute_sql_dict(db, "cx_sql", {'id':wjid})[0]
            sjkkzbs = re_data['sjkkzbs'] if re_data['sjkkzbs'] else 0
            sjkkzje = float(re_data['sjkkzje']) if re_data['sjkkzje'] else 0
            upd_data = {
            'sjkkzbs':int(sjkkzbs)+Bs,
            'sjkkzje':(sjkkzje+Je),
            'updtime':now_time,
            'id':wjid}
            ModSql.yw_gtpm_003.execute_sql( db, "upd_sql", upd_data )
    # 登记操作日志
    rzxx = ModSql.yw_gtpm_003.execute_sql_dict(db, "sel_rzxx", {'wjid':wjid})[0]
    rznr_zwpk = '阈值校验流水_查看明细_置为批扣：文件名称[%s]，文件类型: [%s]，所属业务:[%s]，批次号[%s]'%( rzxx['wjmc'],rzxx['wjlx'],rzxx['ywmc'],rzxx['pch'] )
    rznr_zwsb = '阈值校验流水_查看明细_置为失败：文件名称[%s]，文件类型: [%s]，所属业务:[%s]，批次号[%s]，置为失败的总金额为[%.2f]，置为失败的总笔数为[%d]'%( rzxx['wjmc'],rzxx['wjlx'],rzxx['ywmc'],rzxx['pch'], Je, Bs )
    gnmc = '阈值校验流水_查看明细_置为失败' if flag=='zwsb' else '阈值校验流水_查看明细_置为批扣'
    with sjapi.connection() as db:
        ins_czrz( db, rznr_zwsb if flag=='zwsb' else rznr_zwpk, pt = 'wh', gnmc = gnmc)
    # 将查询到的结果反馈给 view
    return data

def zwjwdkk_service( sql_data ):
    """
    # 置文件为待扣款 json数据
    """
    # 初始化返回值
    data = {'state':True, 'msg':'置文件为待扣款成功'}
    ids_lst = sql_data['id'].split(',')
    # ids_lst = [ls['id'] for ls in ids_lst]
    now_time = get_strftime2()
    now_time = now_time.replace(' ','')
    # 更新文件登记簿的状态为12（准备批扣）
    with sjapi.connection() as db:
        ModSql.yw_gtpm_003.execute_sql(db, "upd_wjdpk", {'ids_lst':ids_lst,'updtime':now_time})
        # 登记操作日志
        rzxx_rs = []
        for id in ids_lst:
            rzxx = ModSql.yw_gtpm_003.execute_sql_dict(db, "sel_rzxx", {'wjid':id})[0]
            rzxx_rs.append({'文件名称':rzxx['wjmc'],'文件类型':rzxx['wjlx'],'所属业务':rzxx['ywmc']})
        rznr = '阈值校验流水_将文件置为待扣款:' + str(rzxx_rs)
        ins_czrz( db, rznr, pt = 'wh', gnmc = '阈值校验流水_将文件置为待扣款')
        # 将查询到的结果反馈给view
    return data

def xgyz_service( sql_data ):
    """
    # 修改阈值 json数据
    """
    # 初始化返回值
    data = {'state':True, 'msg':''}
    # 更查询阈值校验_参数配置ID
    with sjapi.connection() as db:
        data_wjxx = ModSql.yw_gtpm_003.execute_sql_dict(db, "sel_wjxx", sql_data)[0]
        data_wjxx['csdm'] = ''
        if data_wjxx['zt'] == '66':
            data_wjxx['csdm'] = 'YZJY_CFJE'
        if data_wjxx['zt'] == '77':
            data_wjxx['csdm'] = 'YZJY_DBJE'
        if data_wjxx['zt'] == '88':
            data_wjxx['csdm'] = 'YZJY_YZ'
        # 查询阈值校验_参数配置ID
        data_cspzid = ModSql.yw_gtpm_003.execute_sql_dict(db, "sel_csid", data_wjxx)[0]
        data['id'] = data_cspzid['id']
        # 登记操作日志
        rzxx = ModSql.yw_gtpm_003.execute_sql_dict(db, "sel_rzxx", data_wjxx)[0]
        rznr = '阈值校验流水查看_修改阈值:文件名称[%s],文件类型[%s],所属业务[%s],批次号[%s]'%( rzxx['wjmc'], rzxx['wjlx'], rzxx['ywmc'], rzxx['pch'] )
        ins_czrz( db, rznr, pt = 'wh', gnmc = '阈值校验流水查看_修改阈值')
        # 将查询到的结果反馈给view
    return data

def cx_service( sql_data ):
    """
    # 撤销 json数据
    """
    # 初始化返回值
    data = {'state':True, 'msg':'撤销成功'}
    wjid = sql_data['wjid']
    now_time = get_strftime2()
    now_time = now_time.replace(' ','')
    # # 从数据库中取出全部撤销的sql
    with sjapi.connection() as db:
        data_sql = ModSql.yw_gtpm_003.execute_sql( db, 'qbcx_sql', { 'wjid': wjid } )
        if data_sql:
            qbcx_sql = pickle.loads(data_sql[0]['ycqbcxsql'].read()) if data_sql else ''
            cur = db.cursor()
            cur.execute(qbcx_sql,[wjid])
        else:
            data['state'] = False
            data['msg'] = '该业务未进行阈值校验业务配置，请先配置业务参数再处理！'
            return data
        # 更新文件处理登记簿状态为16：待反馈三方，更新时间为当前时间
        upd_data = {'zt':'16', 'updtime':now_time, 'id':wjid}
        ModSql.yw_gtpm_003.execute_sql( db, 'upd_wjzt_sql', upd_data )
        # 登记操作日志
        rzxx = ModSql.yw_gtpm_003.execute_sql_dict(db, "sel_rzxx", sql_data)[0]
        rznr = '阈值校验流水_撤销：文件名称[%s],文件类型[%s],所属业务[%s],批次号[%s]'%( rzxx['wjmc'], rzxx['wjlx'], rzxx['ywmc'], rzxx['pch'] )
        ins_czrz( db, rznr, pt = 'wh', gnmc = '阈值校验流水_撤销')
        # 将查询到的结果反馈给view
    return data

def tg_service( sql_data ):
    """
    # 通过 json数据
    """
    # 初始化返回值
    data = {'state':True, 'msg':'通过成功'}
    wjid = sql_data['wjid']
    now_time = get_strftime()
    now_time = now_time.replace(' ','')
    # # 从数据库中取出全部撤销的sql
    with sjapi.connection() as db:
        data_sql = ModSql.yw_gtpm_003.execute_sql( db, 'qbtg_sql', { 'wjid': wjid } )
        if data_sql:
            qbtg_sql = pickle.loads(data_sql[0]['ycqbtgsql'].read()) if data_sql else ''
            cur = db.cursor()
            cur.execute(qbtg_sql,[wjid])
        else:
            data['state'] = False
            data['msg'] = '该业务未进行阈值校验业务配置，请先配置业务参数再处理！'
            return data
        # 更新文件处理登记簿状态为13：导入到GTP流水，更新时间为当前时间
        upd_data = {'zt':'13', 'updtime':now_time, 'id':wjid}
        ModSql.yw_gtpm_003.execute_sql( db, 'upd_wjzt_sql', upd_data )
        # 登记操作日志
        rzxx = ModSql.yw_gtpm_003.execute_sql_dict(db, "sel_rzxx", sql_data)[0]
        rznr = '阈值校验流水_通过：文件名称[%s],文件类型[%s],所属业务[%s],批次号[%s]'%( rzxx['wjmc'], rzxx['wjlx'], rzxx['ywmc'], rzxx['pch'] )
        ins_czrz( db, rznr, pt = 'wh', gnmc = '阈值校验流水_通过')
        # 将查询到的结果反馈给view
    return data