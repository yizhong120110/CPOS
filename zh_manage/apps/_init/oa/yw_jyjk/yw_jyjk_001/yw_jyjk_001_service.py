# -*- coding: utf-8 -*-
# Action: 交易监控
# Author: zhangchl
# AddTime: 2015-04-13
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql, logger
from sjzhtspj.common import ( get_bmwh_bm, get_strfdate, analyse_sys_run_trace, lc_data_service, get_srysjdid, 
                            get_scysjdid, format_log, binary_to_hex_db, change_log_msg )
from sjzhtspj.esb import memcache_data_del
from sjzhtspj.esb import readlog


def index_service( sql_data ):
    """
    # 初始化交易监控页面数据准备 service
    """
    # 初始化反馈值
    data = { 'zt_lst': [], 'xtlx': '', 'yw_lst': [{'value': '', 'text': '请选择'}] }
    # 查询流水状态列表
    zt_lst = get_bmwh_bm( '10010' )
    # 追加请选择选项
    zt_lst.insert( 0, {'value': '', 'ms': '', 'text': '请选择'} )
    # 将结果放到返回值中
    data['zt_lst'] = zt_lst
    # 当前日期
    data['nowdate'] = get_strfdate()
    # 系统类型
    # 数据库链接
    with sjapi.connection() as db:
        xtlx_rs = ModSql.common.execute_sql(db, "get_xtlx")
        if xtlx_rs:
            data['xtlx'] = xtlx_rs[0].value
        # 查询系统内所有业务 
        data['yw_lst'].extend( ModSql.yw_jyjk_001.execute_sql_dict(db, "get_ywlst", sql_data) )
        
    # 将结果反馈给view
    return data

def data_service( sql_data ):
    """
    # 交易监控列表json数据 service
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    # 清理为空的查询条件
    search_lst = [ 'jyrq', 'jymc', 'jym', 'lszt', 'jgdm', 'lsh', 'khzh', 'shzh', 'gyh' ]
    for k in list(sql_data.keys()):
        if k in search_lst and sql_data[k] == '':
            del sql_data[k]
    # 数据库链接
    with sjapi.connection() as db:
        # 查询交易总条数
        total = ModSql.yw_jyjk_001.execute_sql(db, "data_count", sql_data)[0].count
        # 查询交易列表
        jbxx = ModSql.yw_jyjk_001.execute_sql_dict(db, "data_rs", sql_data)
        # 查询流水状态列表
        zt_lst = get_bmwh_bm( '10010', db = db )
        # 流水状态字典
        zt_dict = dict( [(xx['value'], xx['text']) for xx in zt_lst ] )
        # 对结果集中状态进行翻译
        for obj in jbxx:
            obj['ztmc'] = zt_dict.get( obj['zt'], obj['zt'] )
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = jbxx
    
    # 将查询到的结果反馈给view
    return data

def workflow_service( sql_data ):
    """
    # 交易流水日志查看组织流程图书架 view
    """
    
    # 调用公共方法获取流程图( 交易id， lx：流程 )
    workflow = lc_data_service( sql_data['jyid'], sql_data['lclx'] )
    with sjapi.connection() as db:
        # 日志信息
        sys_run_trace = sql_data['sys_run_trace']
        # 打解包字典
        djbxx = {}
        # 前台未传入日志信息
        if not sys_run_trace:
            # 根据交易码查询交易的打解包信息
            jyxx = ModSql.common.execute_sql_dict(db, "get_jydy_byjym", sql_data)
            # 查询打包节点id、解包节点id对应的节点编码
            if jyxx:
                # 打包节点id
                dbjdid = jyxx[0]['dbjdid']
                # 解包节点id
                jbjdid = jyxx[0]['jbjdid']
                jdxx_lst = ModSql.common.execute_sql_dict( db, "get_jddy", { 'ids': [ dbjdid, jbjdid ] } )
                # 组织数据结构
                dbjdxx = []
                jbjdxx = []
                for obj in jdxx_lst:
                    if obj['id'] == dbjdid:
                        dbjdxx = [dbjdid,obj['bm'],obj['jdmc']]
                    if obj['id'] == jbjdid:
                        jbjdxx = [jbjdid,obj['bm'],obj['jdmc']]
                djbxx = {'dbjd': dbjdxx, 'jbjd': jbjdxx}
            # 后台调用核心接口readlog，传入参数交易日期、流水号，获取日志信息列表。
            # 取最后一条log信息中存放的交易字典中的SYS_RUN_TRACE信息
            ret_log_lst = readlog(sql_data['jyrq'], sql_data['lsh'])
            logger.info('查询反馈的日志列表：%s' % str(ret_log_lst))
            sys_run_trace = ''
            if ret_log_lst:
                for log_dic in list( reversed( ret_log_lst ) ):
                    if log_dic.get('jyzd',''):
                        jyzd = log_dic.get('jyzd',{})
                        if jyzd.get('SYS_JYJDGZ'):
                            sys_run_trace = jyzd.get('SYS_JYJDGZ')
                            break
        
        # 获取交易的主流程走向和子流程信息
        # lczx结构：[[start,返回值],[节点编码,返回值],[子流程编码,返回值],[end,返回值]]
        # zlc_dic数据结构：{'zlcdm':'zlcdm,start[0]:节点编码[1]:end[0]',…}
        # 确定交易或子流程开始节点的节点编码
        start_type = 'jystart'
        if sql_data['lclx'] == 'zlc':
            start_type = 'zlcstart'
        # 获取流程走向和子流程字典
        logger.info('查询反馈的整理出的SYS_JYJDGZ：%s' % str(sys_run_trace))
        lczx, zlc_dic = analyse_sys_run_trace( sys_run_trace, start_type = start_type )
        logger.info('查询反馈的整理出的流程走向：%s' % str(lczx))
        logger.info('查询反馈的整理出的子流程信息：%s' % str(zlc_dic))
        # 循环lczx，判断节点编码在zlc_dic中是否有数据，若有，则表示此节点为子流程，若没有，则为节点
        connector1 = []
        for lxxx in lczx:
            # 节点编码
            jdbm = lxxx[0]
            if jdbm == 'end':
                if sql_data['lclx'] == 'lc':
                    jdbm = 'jyend'
                else:
                    jdbm = 'zlcend'
            # 节点返回值
            jdfhz = lxxx[1]
            # 节点类型
            jdlx = 'jd'
            # 子流程信息
            zlc_run_trace = ''
            # 查询布局条件字典
            jdbj_dic = {}
            if sql_data['lclx'] == 'zlc':
                jdbj_dic['sszlcid'] = sql_data['jyid']
            else:
                jdbj_dic['ssjyid'] = sql_data['jyid']
            # 判断是否是子流程
            if jdbm in zlc_dic:
                # 节点布局信息
                jdbj_dic['bm'] = jdbm
                jdbjxx = ModSql.yw_jyjk_001.execute_sql_dict( db, "get_zlc_bj", jdbj_dic )
                # 节点类型
                jdlx = 'zlc'
                # 子流程信息
                zlc_run_trace = zlc_dic.get( jdbm, '' )
            # 判断是否是节点
            else:
                jdbj_dic['bm'] = jdbm
                jdbjxx = ModSql.yw_jyjk_001.execute_sql_dict( db, "get_lc_bj", jdbj_dic )
            if jdbjxx:
                # 节点id
                jdid = jdbjxx[0]['jdid']
                jdmc = jdbjxx[0]['mc']
                # 交易
                # 组织数据结构时，处理节点编码为jystart、jyend时，
                # 数据结构中对应的节点ID为djbxx中的解包节点id和打包节点id，
                # 节点编码为djbxx中对应的解包节点编码和打包节点编码
                if sql_data['lclx'] == 'lc':
                    # 交易开始节点
                    if jdbm == 'jystart':
                        jbxx = djbxx.get( 'jbjd' )
                        jdid = jbxx[0]
                        #jdbm = jbxx[1]
                        jdmc = '%s[%s]' % ('交易开始', jbxx[2])
                    if jdbm == 'jyend':
                        dbxx = djbxx.get( 'dbjd' )
                        jdid = dbxx[0]
                        #jdbm = dbxx[1]
                        jdmc = '%s[%s]' % ('交易结束', dbxx[2])
                # 将本节点信息追加到执行列表中
                connector1.append( { 'jdid': jdid, 'bjid': jdbjxx[0]['bjid'], 'jdfhz': jdfhz,
                'jdbm': 'end' if jdbm in ['zlcend','jyend'] else jdbm, 
                'mc': jdmc, 'jdlx': jdlx, 'zlc_run_trace': zlc_run_trace } )
        # 追加到结果集( 流程走向详情 )
        workflow.append( connector1 )
        # 流程走向概况
        workflow.append( lczx )
        # 子流程字典
        workflow.append( zlc_dic )
    
    # 返回查询结果集
    return workflow

def lcrzck_service( sql_data ):
    """
    # 查询流程日志
    """
    # 初始化返回值
    result = { 'state':True, 'msg': '', 'rznr':'' }
    # 调用公共函数获取本流程交易日期
    log_all = []
    if sql_data['lccj']:
        if len( sql_data['lccj'].split('.') ) >1 and sql_data['lccj'].split('.')[0] == '':
            sql_data['lccj'] = '.'.join( sql_data['lccj'].split('.')[1:] )
        # 获取日志
        log_lst_dic = readlog( sql_data['jyrq'], sql_data['lsh'], jdid = sql_data['lccj'] )
        log_all = change_log_msg( log_lst_dic )
    else:
        log_lst_dic = readlog( sql_data['jyrq'], sql_data['lsh'] )
        log_all = change_log_msg( log_lst_dic )
    # 整理日志
    result['rznr'] = format_log( log_all )
    # 将日志信息返回给view
    return result
    
def check_jdlx_service( sql_data ):
    """
    # 验证节点类型是否是系统预设节点
    # 若查询到的节点类型为2或7，则表示该节点为预置节点，不能修改。
    # 节点类型：2-系统节点，为通讯子流程的预处理节点；7-通讯节点，为通讯子流程的通讯节点
    """
    # 初始化反馈信息
    result = { 'state':False, 'msg': '' }
    with sjapi.connection() as db:
        jdxx_lst = ModSql.common.execute_sql_dict( db, "get_jddy", { 'ids': [ sql_data['jdid'] ] } )
        if jdxx_lst:
            if jdxx_lst[0]['jdlx'] not in [ '2', '7' ]:
                result['state'] = True
            else:
                result['msg'] = '本节点为系统预置节点，不能修改'
        else:
            result['msg'] = '本节点已在系统中不存在，不能修改'
    
    return result
    
def jdrzck_service( sql_data ):
    """
    # 节点日志查看
    """
    # 初始化反馈信息
    result = { 'state':False, 'msg': '', 'srys_lst': [], 'scys_lst': [], 'rznr': '' }
    with sjapi.connection() as db:
        # 获取此节点的输入输出要素
        jdys_lst = ModSql.yw_jyjk_001.execute_sql_dict( db, "get_jdys", { 'jddyid': sql_data['jdid'] } )
        srscys = { 'srys': [], 'scys': [] }
        for obj in jdys_lst:
            # 输入要素
            if obj['lb'] == '1':
                srscys['srys'].append( obj['bm'] )
            # 输出要素
            elif obj['lb'] == '2':
                srscys['scys'].append( obj['bm'] )
        # (1)获取本节点的输出要素tab页中要展示的信息
        #   传入参数交易日期、流水号、流程层级.本节点的编码、类型（节点），获取本节点的日志信息列表
        #   流程层级
        lccj = '%s.%s' % ( sql_data['lccj'], sql_data['jdbm'] )
        #   节点类型
        jdlx = 'jd'
        # 获取本节点信息
        if len( lccj.split('.') ) >1 and lccj.split('.')[0] == '':
            lccj = '.'.join( lccj.split('.')[1:] )
        ret_log_lst = readlog( sql_data['jyrq'], sql_data['lsh'], jdid = lccj )
        # 如果日志获取成功，根据日志最后一条log信息中存放的交易字典信息
        # 交易字典{编码1：值，编码2：值，编码3}
        bjd_jyzd = {}
        if ret_log_lst:
            for log_dic in list( reversed( ret_log_lst ) ):
                if log_dic.get('jyzd',''):
                    bjd_jyzd = log_dic.get('jyzd',{})
            # 将二进制转换为对比十六进制
            binary_to_hex_db( bjd_jyzd )
        # 给输出要素填值
        for bm in srscys.get('scys',[]):
            ysxx = { 'bm': bm, 'ysz': bjd_jyzd.get( bm, '' ) }
            result['scys_lst'].append( ysxx )
        # (2)获取本节点的输入要素tab页中要展示的信息
        # (21)若该节点类型为start，则根据bjd_jyzd和srscys中的srys结构，获取本节点的输入要素编码及值
        if sql_data['jdlx_start'] == '1':
            for bm in srscys.get('srys',[]):
                ysxx = { 'bm': bm, 'ysz': bjd_jyzd.get( bm, '' ) }
                result['srys_lst'].append( ysxx )
        else:
        # (22)若该节点不为start，则根据前台传入的lczx结构，获取本节点在流程走向中的上一个节点的编码
            # 节点所在位置
            jd_index = False
            # 下标
            row_index = 0
            for zxxx in sql_data['lczx']:
                if zxxx[0] == sql_data['jdbm']:
                    jd_index = row_index
                    break
                row_index += 1
            # 在流程布局中存在且不是第一个节点
            if jd_index > 0:
                # 上一节点编码
                sy_jdbm = sql_data['lczx'][jd_index-1][0]
                # 若上一节点编码为start，则根据流程类型，重新定义上一节点编码
                if sy_jdbm == 'start':
                    if sql_data['lclx'] == 'zlc':
                        sy_jdbm = 'zlcstart'
                    else:
                        sy_jdbm = 'jystart'
                # 若上一节点编码在zlc_dic中有对应数据，则重新定义上一节点编码
                elif sy_jdbm in sql_data['zlc_dic']:
                    sy_jdbm = '%s.end' % sy_jdbm
                # 流程层级
                lccj = '%s.%s' % ( sql_data['lccj'], sy_jdbm )
                # 调用核心接口readlog，传入参数交易日期、流水号、上一节点编码、类型（节点），获取上一节点的日志信息列表
                if len( lccj.split('.') ) >1 and lccj.split('.')[0] == '':
                    lccj = '.'.join( lccj.split('.')[1:] )
                sy_ret_log_lst = readlog( sql_data['jyrq'], sql_data['lsh'], jdid = lccj )
                # 交易字典{编码1：值，编码2：值，编码3}
                syjd_jyzd = {}
                if sy_ret_log_lst:
                    for log_dic in list( reversed( sy_ret_log_lst ) ):
                        if log_dic.get('jyzd',''):
                            syjd_jyzd = log_dic.get('jyzd',{})
                    # 将二进制转换为对比十六进制
                    binary_to_hex_db( syjd_jyzd )
                # 赋值
                for bm in srscys.get('srys',[]):
                    ysxx = { 'bm': bm, 'ysz': syjd_jyzd.get( bm, '' ) }
                    result['srys_lst'].append( ysxx )
        
        # (3)获取本节点的日志tab页中要展示的信息
        if ret_log_lst:
            # 调用公共函数获取本流程交易日期
            log_all = change_log_msg( ret_log_lst )
            # 整理日志
            result['rznr'] = format_log( log_all )
        
        # 获取成功
        result['state'] = True
    return result
    
def lctlb_zlcrzck_service( sql_data ):
    """
    # 流程图列表 子流程输入、输出、日志查看
    """
    # 取子流程中开始节点后一节点
    srysjdbm = get_srysjdid(sql_data['zlc_dic'].get(sql_data['jdbm']))
    # 结束节点前一节点
    scysjdbm = get_scysjdid(sql_data['zlc_dic'].get(sql_data['jdbm']))
    # 初始化反馈信息
    result = { 'state':False, 'msg': '', 'srys_lst': [], 'scys_lst': [], 'rznr': '' }
    with sjapi.connection() as db:
        # 获取要素输入、输出要素
        srscys = { 'srys': [], 'scys': [] }
        # 开始节点后一节点的输入要素
        srys_lst = []
        # zcl 20150902 如果是预处理节点，则是打包节点的输入要素
        if srysjdbm == 'ycljd':
            srys_lst = ModSql.yw_jyjk_001.execute_sql_dict( db, "get_dbjdys_sr", { 'zlcdyid': sql_data['jdid'] } )
        else:
            srys_lst = ModSql.yw_jyjk_001.execute_sql_dict( db, "get_jdys_byjdbm", { 'jdbm': srysjdbm, 'lb': '1' } )
        # 结束节点前一节点的输出要素
        scys_lst = []
        # zcl 20150902 如果非预处理节点正常获取
        if scysjdbm != 'ycljd':
            scys_lst = ModSql.yw_jyjk_001.execute_sql_dict( db, "get_jdys_byjdbm", { 'jdbm': scysjdbm, 'lb': '2' } )
        # 根据结果组织输入、输出要素
        for obj in srys_lst:
            # 输入要素
            srscys['srys'].append( obj['bm'] )
        for obj in scys_lst:
            if scysjdbm != 'ycljd':
                # 输出要素
                srscys['scys'].append( obj['bm'] )
        
        # (1)获取本节点的输出要素tab页中要展示的信息
        #   传入参数交易日期、流水号、流程层级.子流程编码.zlcend、类型（节点），获取日志信息列表
        #   流程层级
        lccj = '%s.%s' % ( sql_data['lccj'], sql_data['jdbm'] )
        # 如果是预处理节点
        if scysjdbm == 'ycljd':
            lccj = '%s.%s.ycljd' % ( sql_data['lccj'], sql_data['jdbm'] )
        #   节点类型
        if len( lccj.split('.') ) >1 and lccj.split('.')[0] == '':
            lccj = '.'.join( lccj.split('.')[1:] )
        sc_ret_log_lst = readlog( sql_data['jyrq'], sql_data['lsh'], jdid = lccj )
        # 如果日志获取成功，根据日志最后一条log信息中存放的交易字典信息
        bjd_jyzd = {}
        if sc_ret_log_lst:
            # 交易字典{编码1：值，编码2：值，编码3}
            for log_dic in list( reversed( sc_ret_log_lst ) ):
                if log_dic.get('jyzd',''):
                    bjd_jyzd = log_dic.get('jyzd',{})
            # 将二进制转换为对比十六进制
            binary_to_hex_db( bjd_jyzd )
        # 给输出要素填值
        if scysjdbm == 'ycljd':
            result['scys_lst'] = [ { 'bm': bm, 'ysz': bjd_jyzd.get( bm, '' ) } for bm in sorted(bjd_jyzd.keys()) ]
        else:
            for bm in srscys.get('scys',[]):
                ysxx = { 'bm': bm, 'ysz': bjd_jyzd.get( bm, '' ) }
                result['scys_lst'].append( ysxx )
        
        # (2)获取本节点的输入要素tab页中要展示的信息
        # (21)如果此子流程时第一个节点，则取子流程的zlcstart
        sy_jdbm = ''
        if sql_data['jdlx_start'] == '1':
            sy_jdbm = '%s.zlcstart' % sql_data['jdbm']
        else:
        # (22)则根据前台传入的lczx结构，获取本节点在流程走向中的上一个节点的编码
            # 节点所在位置
            jd_index = False
            # 下标
            row_index = 0
            for zxxx in sql_data['lczx']:
                if zxxx[0] == sql_data['jdbm']:
                    jd_index = row_index
                    break
                row_index += 1
            # 在流程布局中存在且不是第一个节点
            if jd_index > 0:
                # 上一节点编码
                sy_jdbm = sql_data['lczx'][jd_index-1][0]
                # 若上一节点编码为start，则根据流程类型，重新定义上一节点编码
                if sy_jdbm == 'start':
                    if sql_data['lclx'] == 'zlc':
                        sy_jdbm = 'zlcstart'
                    else:
                        sy_jdbm = 'jystart'
                # 若上一节点编码在zlc_dic中有对应数据，则重新定义上一节点编码
                elif sy_jdbm in sql_data['zlc_dic']:
                    sy_jdbm = '%s.zlcend' % sy_jdbm
        # 流程层级
        lccj = '%s.%s' % ( sql_data['lccj'], sy_jdbm )
        # 调用核心接口readlog，传入参数交易日期、流水号、上一节点编码、类型（节点），获取上一节点的日志信息列表。
        if len( lccj.split('.') ) >1 and lccj.split('.')[0] == '':
            lccj = '.'.join( lccj.split('.')[1:] )
        sy_ret_log_lst = readlog( sql_data['jyrq'], sql_data['lsh'], jdid = lccj )
        # 交易字典{编码1：值，编码2：值，编码3}
        syjd_jyzd = {}
        if sy_ret_log_lst:
            for log_dic in list( reversed( sy_ret_log_lst ) ):
                if log_dic.get('jyzd',''):
                    syjd_jyzd = log_dic.get('jyzd',{})
            # 将二进制转换为对比十六进制
            binary_to_hex_db( syjd_jyzd )
        # 输入要素赋值
        for bm in srscys.get('srys',[]):
            ysxx = { 'bm': bm, 'ysz': syjd_jyzd.get( bm, '' ) }
            result['srys_lst'].append( ysxx )
        
        # (3)获取本节点的日志tab页中要展示的信息:
        #    后台调用核心接口readlog，传入参数交易日期、流水号、流程层级.子流程编码、类型（子流程）
        lccj = '%s.%s' % ( sql_data['lccj'], sql_data['jdbm'] )
        jdlx = 'zlc'
        if len( lccj.split('.') ) >1 and lccj.split('.')[0] == '':
            lccj = '.'.join( lccj.split('.')[1:] )
        zlc_ret_log = readlog( sql_data['jyrq'], sql_data['lsh'], jdid = lccj )
        if zlc_ret_log:
            # 调用公共函数获取本流程交易日期
            log_all = change_log_msg( zlc_ret_log )
            # 整理日志
            result['rznr'] = format_log( log_all )
        # 获取成功
        result['state'] = True
    # 反馈执行结果
    return result

def yxxjyls_ck_service( sql_data ):
    """
    # 交易监控列表json数据 service
    """
    # 初始化返回值
    data = {'state': False, 'msg': '', 'total':0, 'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询交易列表
        total = ModSql.yw_jyjk_001.execute_sql(db, "get_lsyxxjy_total", sql_data)[0].count
        jbxx = ModSql.yw_jyjk_001.execute_sql_dict(db, "get_lsyxxjy", sql_data)
        # 将查询详情结果放到结果集中
        data['total'] = total
        data['rows'] = jbxx
        data['state'] = True
    
    # 将查询到的结果反馈给view
    return data
    
def dbjyls_ck_service( sql_data ):
    """
    # 挡板校验流水查看json数据 service
    """
    # 初始化返回值
    data = {'state': False, 'msg': '', 'total':0, 'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询交易列表
        total = ModSql.yw_jyjk_001.execute_sql(db, "get_lsdbjy_total", sql_data)[0].count
        jbxx = ModSql.yw_jyjk_001.execute_sql_dict(db, "get_lsdbjy", sql_data)
        # 将查询详情结果放到结果集中
        data['total'] = total
        data['rows'] = jbxx
        data['state'] = True
    
    # 将查询到的结果反馈给view
    return data
    
    