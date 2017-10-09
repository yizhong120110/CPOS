# -*- coding: utf-8 -*-
# Action: 监控管理-监控配置
# Author: luoss
# AddTime: 2015-05-22
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql
from sjzhtspj.common import get_hsxxb,get_bmwh_bm,get_uuid,get_sess_hydm,get_strftime,get_strftime2,ins_czrz,del_waitexec_task,crontab_fy,ins_waitexec_task,update_jhrw

def index_service( sql_data ):
    """
    # 初始化交易监控页面数据准备 service
    """
    # 初始化反馈值
    data = { 'fxgz_lst': [{'id':'','zwmc':'请选择'}], 'yjjb_lst': [{'value': '', 'ms': '', 'text': '请选择'}], 
            'sfbf_lst': [{'value': '', 'ms': '', 'text': '请选择'}], 'zt_lst': [{'value': '', 'ms': '', 'text': '请选择'}], 
            'pt': sql_data['pt'] }
    with sjapi.connection() as db:
        # 分析规则
        data['fxgz_lst'].extend(get_hsxxb( db, 'gz' ))
        # 预警级别
        data['yjjb_lst'].extend(get_bmwh_bm( '10011', db=db ))
        # 是否可并发
        data['sfbf_lst'].extend(get_bmwh_bm( '10007', db=db ))
        # 状态
        data['zt_lst'].extend(get_bmwh_bm( '10001', db=db ))
        # 将结果反馈给view
        return data
        
def data_service( sql_data ):
    """
    # 交易监控列表json数据 service
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    # 清理为空的查询条件
    search_lst = [ 'mc', 'gzid', 'yjjb', 'zt' ]
    for k in list(sql_data.keys()):
        if k in search_lst and sql_data[k] == '':
            del sql_data[k]
    # 数据库链接
    with sjapi.connection() as db:
        # 查询交易总条数
        total = ModSql.yw_jkgl_006_test.execute_sql(db, "data_count", sql_data)[0].count
        # 查询交易列表
        jbxx = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "data_rs", sql_data)
        # 预警级别
        yjjb_lst = get_bmwh_bm( '10011', db=db )
        # 预警级别字典
        yjjb_dict = dict( [(xx['value'], xx['text']) for xx in yjjb_lst ] )
        # 是否可并发
        sfbf_lst = get_bmwh_bm( '10007', db=db )
        # 是否可并发字典
        sfbf_dict = dict( [(xx['value'], xx['text']) for xx in sfbf_lst ] )
        # 状态
        zt_lst = get_bmwh_bm( '10001', db=db )
        # 状态字典
        zt_dict = dict( [(xx['value'], xx['text']) for xx in zt_lst ] )
        # 对结果集中状态进行翻译
        for obj in jbxx:
            obj['yjjbmc'] = zt_dict.get( obj['yjjb'], obj['yjjb'] )
            obj['sfkbfmc'] = zt_dict.get( obj['sfkbf'], obj['sfkbf'] )
            obj['ztmc'] = zt_dict.get( obj['zt'], obj['zt'] )
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = jbxx
        # 将查询到的结果反馈给view
        return data
        
def xydz_service( sql_data ):
    """
    # 监控配置 响应动作页面展示
    """
    # 数据库链接
    with sjapi.connection() as db:
        # 响应动作查询
        xydz_lst = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "data_xydz_rs", sql_data)
        # 动作执行主机查询
        dzzj_lst = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "data_zxzj_rs", sql_data)
        # 执行主机列表中提取出来的数据
        cont_dict = {}
        for k in dzzj_lst:
            if k['ssid'] in cont_dict:
                cont_dict[k['ssid']] = '%s,%s(%s)'%(cont_dict[k['ssid']],k['mc'],k['zjip'])
            else:
                cont_dict[k['ssid']] =  '%s(%s)'%(k['mc'],k['zjip'])
        # 返回信息值处理
        for k in xydz_lst :
            k['dzzxzj'] = cont_dict.get(k['id'], '')
        return xydz_lst
        
def xydz_sel_service( sql_data ):
    """
    # 监控配置 响应动作页面查询链接展示
    """
    # 数据库链接
    with sjapi.connection() as db:
        # 查询结果
        xydz_rs = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "data_xydz_sel_rs", sql_data)
        # 返回结果
        return xydz_rs
        
def xydz_add_sel_service():
    """
    # 监控配置 响应动作新增 初始化
    """
    # 初始化数据列表信息
    data = {'xydz_lst':[{'id': '', 'zwmc': '请选择'}], 'fqfs_lst':[], 'dzzxzj_lst':[{'ip': '', 'mc': '请选择'}], 'fxjgcf_lst':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 响应动作下拉列表展示查询
        xydz_rs = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "xydz_rs")
        # 分析结果触发查询
        fxjgcf_rs = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "fxjgcf_rs")
        # 发起方式查询
        fqfs_rs = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "fqfs_rs")
        # 动作执行主机查询
        dzzxzj_rs = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "dzzxzj_rs")
        # 数据信息进行统一存储
        data['xydz_lst'].extend(xydz_rs)
        data['dzzxzj_lst'].extend(dzzxzj_rs)
        data['fxjgcf_lst'] = fxjgcf_rs
        data['fqfs_lst'] = fqfs_rs
        # 将整合后的结果返回给view
        return data
        
def xydz_add_change_service( sql_data ):
    """
    # 监控配置 响应动作新增 响应动作改变事件
    """
    # 数据库链接
    with sjapi.connection() as db:
        # 参数列表展示
        data = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "cslbzs_rs", sql_data)
        # 将查询到的信息返回给view
        return data
        
def xydz_add_bjgzcs_service( sql_data ):
    """
    # 监控配置编辑 编辑规则参数 初始化
    """
    # 初始化将要返回的数据类型结构
    data = {'zwmc':'' ,'ms':'' ,'csxx':[], 'sjxx_str':''}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询规则信息
        gzxx = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_gzxx", sql_data)
        # 参数信息列表展示信息查询
        csxx_rs = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_csxx", sql_data)
        # 数据信息默认值
        sjxx_str = ''
        # 参数列表信息提取信息
        if csxx_rs:
            for k in range(len(csxx_rs)):
                sjxx_str = '%s,参数代码:%s参数说明:%s参数值:%s'%(sjxx_str,csxx_rs[k]['csdm'], csxx_rs[k]['cssm'], csxx_rs[k]['csz'])
        # 判断当规则信息不为空时进行数据的整合与返回
        if gzxx:
            data['zwmc'] = gzxx[0]['zwmc']
            data['ms'] = gzxx[0]['ms']
            data['csxx'] = csxx_rs
            data['sjxx_str'] = sjxx_str
            # 将整合后的结果返回给view
            return data
            
def xydz_add_bjgzcs_set_service( sql_data ):
    """
    # 监控配置编辑 编辑规则参数 保存事件
    """
    # 初始化反馈信息
    result = {'state':False, 'msg':''}
    # 数据库链接
    with sjapi.connection() as db:
        # 删除参数对应表中的传入参数id为csid的信息
        ModSql.yw_jkgl_006_test.execute_sql_dict(db, "delete_csdyb", sql_data)
        # 循环更新参数对应表
        csxx_lst = []
        # 参数集合字符串( 传入参数id~参数对应表~参数代码~参数说明~参数值&传入参数id~参数对应表~参数代码~参数说明~参数值 )
        for row_str in sql_data['crcs_str'].split('&'):
            # 传入参数id~参数对应表~参数代码~参数说明~参数值
            row_lst = row_str.split('~')
            # 判断参数值是否为空，为空时不进行插入
            if row_lst[4] != '':
                # 组织传入参数对应表的SQL参数  参数对应表（ID,传入参数ID，参数值，类型，所属ID） 
                sql_csdyb = {'id':get_uuid(), 'csid':row_lst[0], 'csz':row_lst[4], 'lx':'gz', 'ssid':sql_data['id'] }
                ModSql.yw_jkgl_006.execute_sql_dict(db, "add_csdyb", sql_csdyb)
                csxx_lst.append( '参数代码：%s，参数说明：%s，参数值：%s' % ( row_lst[2], row_lst[3], row_lst[4] ) )
        # 调用操作日志公共方法
        csxx_str = '；'.join( csxx_lst )
        # 调用操作日志公共方法
        ins_czrz(db, '监控配置管理-编辑规则参数：编辑前：[%s]，编辑后：[%s]'%(sql_data['sjxx_str'],csxx_str), pt='wh', gnmc='监控配置管理-编辑规则参数')
        result['state'] = True
        result['msg'] = '编辑成功'
        # 返回消息结果
        return result
        
def xydz_add_service( sql_data ):
    """
    # 监控配置 响应动作新增 保存事件
    """
    # 数据库链接
    with sjapi.connection() as db:
        # 数据插入响应动作配置表
        ModSql.yw_jkgl_006_test.execute_sql_dict(db, "add_xydzpz", sql_data)
        print('数据表中插入的信息',sql_data)
        # 循环插入到动作执行主机表
        for k in range(len(sql_data['dzzxzj'])):
            # 组织主机表的插入信息
            sql_zjip = {'id':get_uuid(), 'zjip':sql_data['dzzxzj'][k], 'dzid':sql_data['id'] }
            # 将动作执行主机逐条添加到动作执行主机
            ModSql.yw_jkgl_006_test.execute_sql_dict(db, "add_dzzxzj", sql_zjip)
        # 参数列表展示数据
        data = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "cslbzs_rs", sql_data)
        # 循环更新参数对应表
        # 执行插入操作
        csxx_lst = []
        if sql_data['crcs_str']:
            # 参数集合字符串( 传入参数id~参数对应表~参数代码~参数说明~参数值&传入参数id~参数对应表~参数代码~参数说明~参数值 )
            for row_str in sql_data['crcs_str'].split('&'):
                # 传入参数id~参数对应表~参数代码~参数说明~参数值
                row_lst = row_str.split('~')
                # 判断参数值是否为空，为空时不进行插入
                if row_lst[4] != '':
                    # 组织传入参数对应表的SQL参数  参数对应表（ID,传入参数ID，参数值，类型，所属ID） 
                    sql_csdyb = {'id':get_uuid(), 'csid':row_lst[0], 'csz':row_lst[4], 'lx':'dz', 'ssid':sql_data['xydzid'] }
                    ModSql.yw_jkgl_006.execute_sql_dict(db, "add_csdyb", sql_csdyb)
                    csxx_lst.append( '参数代码：%s，参数说明：%s，参数值：%s' % ( row_lst[2], row_lst[3], row_lst[4] ) )
        # 日志信息
        rzxx_xydz = '监控配置名称[%s]响应动作名称[%s]，分析结果触发[%s]，发起方式[%s]，计划时间[%s]'%(sql_data['id'],sql_data['xydzid'],sql_data['fxjgcf'], sql_data['fqfs'], sql_data['jhsj'])
        rzxx_zxzj = '[%s]'%( sql_data['dzzxzj'] )
        rzxx_cslb = '；'.join( csxx_lst )
        ins_czrz(db, '监控配置管理-新增响应动作：%s，动作执行主机：%s，参数列表：%s'%(rzxx_xydz,rzxx_zxzj,rzxx_cslb), pt='wh', gnmc='监控配置管理-新增响应动作')
        # 返回消息结果
        return {'state':True,'msg':'新增成功'}
        
def xydz_update_sel_service( sql_data ):
    """
    # 响应动作编辑 初始化
    """
    # 初始化将要返回的数据类型结构
    data = {'xydzmc':'' ,'fxjgcf':'' ,'fqfs':'', 'jhsj':'', 'dzzxzj_lst':[],'csxx':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 响应动作配置信息获取
        pzxx_rs = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_pzxx", sql_data)
        # 动作执行主机获取
        dzzxzj_rs = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_dzzxzj_lst", sql_data)
        # 参数信息列表展示信息查询
        csxx_rs = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_csxx", sql_data)
        if pzxx_rs != []:
            data['xydzmc'] = pzxx_rs[0]['xydzmc']
            data['fxjgcf'] = pzxx_rs[0]['fxjgcf']
            data['fqfs'] = pzxx_rs[0]['fqfs']
            data['jhsj'] = pzxx_rs[0]['jhsj']
            data['dzzxzj_lst'] = dzzxzj_rs
            data['csxx'] = csxx_rs
            # 返回整合的信息值
            return data
            
def xydz_update_set_service( sql_data ):
    """
    # 响应动作编辑 保存事件
    """
    # 数据库链接
    with sjapi.connection() as db:
        # 修改前 响应动作配置信息获取
        cz_bjq = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_pzxx", sql_data)
        # 更新响应动作配置表
        ModSql.yw_jkgl_006_test.execute_sql_dict(db, "update_gl_dzzxzj", sql_data)
        # 原动作执行主机列表获取
        dzzxzj_rs = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_dzzxzj_lst", sql_data)
        # 比对原动作执行主机与现在的动作执行主机列表，查看是否一致，若不一致，进行更新操作
        if sql_data['dzzxzj_lst'] != dzzxzj_rs:
            # 删除动作执行主机的信息 ${paras._or('ssid',paras.xydzpzid)}
            ModSql.yw_jkgl_006_test.execute_sql_dict(db, "delete_dzzxzj", sql_data)
            # 循环动作执行主机，重新插入动作执行主机
            for k in sql_data['dzzxzj_lst']:
                # 组织主机循环插入数据参数
                sql_dzzxzj = {'id':get_uuid(),'zjip':k, 'ssid':sql_data['xydzpzid']}
                ModSql.yw_jkgl_006_test.execute_sql_dict(db, "update_insert_dzzxzj", sql_dzzxzj)
        # 删除参数对应表中的传入参数id为csid的信息
        ModSql.yw_jkgl_006_test.execute_sql_dict(db, "delete_csdyb", sql_data)
        # 循环更新参数对应表
        for k in range(len(sql_data['csid'])):
            # 判断参数值是否为空，为空时不进行插入
            if sql_data['csz'][k] != '':
                # 组织传入参数对应表的SQL参数  参数对应表（ID,传入参数ID，参数值，类型，所属ID） 
                sql_csdyb = {'id':get_uuid(), 'csid':sql_data['csid'][k], 'csz':sql_data['csz'][k], 'lx':'dz', 'ssid':sql_data['xydzpzid'] }
                ModSql.yw_jkgl_006_test.execute_sql_dict(db, "add_csdy", sql_csdyb)
        # 操作日志 参数对应信息表查询
        csxx_rs = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_csxx", sql_data)
        # 操作日志 查询监控配置名称
        cz_jkpzmc = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_jkpzmc", sql_data)
        # 操作日志信息获取和最终的信息整合
        rz_sta = '监控配置管理-编辑响应动作：监控配置名称[%s]响应动作名称[%s]'%(cz_jkpzmc[0]['jkpzmc'],cz_bjq[0]['xydzmc'])
        rz_bjq = '编辑前：%s'%(cz_bjq)
        rz_bjh = '编辑后：[分析结果触发[%s]，发起方式[%s]，计划时间[%s]'%(sql_data['fxjgcf'],sql_data['fqfs'],sql_data['jhsj'])
        rz_zxzj = '动作执行主机：%s'%(sql_data['dzzxzj_lst'])
        rz_cslb = '参数列表：%s'%(csxx_rs)
        nr_rs = '%s，%s，%s，%s，%s'%(rz_sta,rz_bjq,rz_bjh,rz_zxzj,rz_cslb)
        # 调用操作日志公共方法
        ins_czrz(db, nr_rs, pt='wh', gnmc='监控配置管理-编辑响应动作')
        # 返回消息结果
        return {'state':True,'msg':'编辑成功'}
        
def xydz_delete_service( sql_data ):
    """
    # 响应动作删除  
    """
    # 初始化反馈信息
    result = {'state':False, 'msg':''}
    # 数据库链接
    with sjapi.connection() as db:
        # 获取响应动作名称及监控分析名称
        rz_jbxx = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_jbxx", sql_data)
        # 获取主机IP
        rz_zjip = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_zjip", sql_data)
        # 删除响应动作配置表
        ModSql.yw_jkgl_006_test.execute_sql_dict(db, "delete_gl_xydzpz", sql_data)
        # 删除动作执行主机
        ModSql.yw_jkgl_006_test.execute_sql_dict(db, "delete_gl_dzzxzj", sql_data)
        # 删除参数对应表
        ModSql.yw_jkgl_006_test.execute_sql_dict(db, "delete_gl_csdyb", sql_data)
        if rz_jbxx and rz_zjip:
            # 操作日志信息
            rz_sta = '监控配置管理-删除响应动作：监控配置名称[%s]响应动作名称[%s]，分析结果触发[%s]，发起方式[%s]，计划时间[%s]'%(rz_jbxx[0]['gzmc'],rz_jbxx[0]['jkfxmc'],rz_jbxx[0]['fxjgcf'],rz_jbxx[0]['fqfs'],rz_jbxx[0]['jhsj'])
            rz_end = '动作执行主机：[%s]'%(rz_zjip[0]['zjip'])
            # 调用操作日志公共方法
            ins_czrz(db, '%s，%s'%(rz_sta,rz_end), pt='wh', gnmc='监控配置管理-删除响应动作')
            # 返回消息结果
            result['state'] = True
            result['msg'] = '删除成功'
            return result
            
def jkpz_delete_service( sql_data ):
    """
    # 监控配置删除
    """
    # 数据库链接
    with sjapi.connection() as db:
        # 查看监控分析配置的相关信息
        jkfxpz = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_jkfxpz", sql_data)
        # 删除响应动作配置-参数对应表
        ModSql.yw_jkgl_006_test.execute_sql_dict(db, "delete_xydz_csdyb", sql_data)
        # 删除响应动作配置-动作执行主机
        ModSql.yw_jkgl_006_test.execute_sql_dict(db, "delete_xydz_dzzxzj", sql_data)
        # 删除响应动作配置表
        ModSql.yw_jkgl_006_test.execute_sql_dict(db, "delete_xydz_dzpz", sql_data)
        # 删除监控分析配置-参数对应表
        ModSql.yw_jkgl_006_test.execute_sql_dict(db, "delete_jkpz_csdyb", sql_data)
        # 查询计划任务表ID,删除当日执行计划表
        jhrwid = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_drjh", sql_data)
        # 删除当日执行计划表
        if jhrwid:
            for k in range(len(jhrwid)):
                del_waitexec_task(jhrwid[k]['id'])
        # 删除计划任务表
        ModSql.yw_jkgl_006_test.execute_sql_dict(db, "delete_jkpz_jhrw", sql_data)
        # 删除监控分析配置表：
        ModSql.yw_jkgl_006_test.execute_sql_dict(db, "delete_jkpz_jkfxpz", sql_data)
        if jkfxpz:
            rz_jbxx = '监控配置管理-删除监控配置：监控配置名称[%s]分析规则名称[%s]，状态[%s]，预警级别[%s]，是否可并发[%s]，crontab配置[%s]，crontab配置说明[%s]'%(jkfxpz[0]['mc'],jkfxpz[0]['gzmc'],jkfxpz[0]['zt'],jkfxpz[0]['yjjb'],jkfxpz[0]['sfkbf'],jkfxpz[0]['zdfqpz'],jkfxpz[0]['zdfqpzsm'])
            # 操作日志记录
            ins_czrz(db, rz_jbxx, pt='wh', gnmc='监控配置管理-删除监控配置')
        # 返回消息结果
        return {'state':True,'msg':'删除成功'}
        
def update_qyjy_service( sql_data ):
    """
    # 监控配置管理-设为启用、禁用  合并操作
    """
    # 判断是启用还是禁用
    qyjy_mc = '启用' if sql_data['qyjy_mc'] == '1' else '禁用'
    print(qyjy_mc)
    # 数据库链接
    with sjapi.connection() as db:
        # 查询监控配置的信息，方便登记操作日志
        jkpz_lst = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_qy_jkpz", sql_data)
        # 筛选前台传入监控配置列表中是否已经有启用的
        jkpz_lst_qy = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_qy_jkpz_lst", sql_data)
        # 判断启用列表是否有值，当没有值时即
        if not jkpz_lst_qy:
            return {'state':False,'msg':'选择的列表中的状态都为%s，无需再设'%(qyjy_mc)}
        # 调用公共方法，操作计划任务
        for obj in jkpz_lst_qy:
            obj['rwlx'] = 'fx'
            yzt = obj['zt']
            obj['zt'] = sql_data['qyjy_mc']
            obj['ssid'] = obj['id']
            update_jhrw( db, yzt, obj['zdfqpz'], upd_dic = obj, sfxz = False )
        # 操作人
        sql_data['czr'] = get_sess_hydm()
        # 操作时间
        sql_data['czsj'] = get_strftime()
        # 状态
        sql_data['zt'] = sql_data['qyjy_mc']
        # 更新监控分析配置表
        ModSql.yw_jkgl_006_test.execute_sql_dict(db, "update_qy_jkfxpz", sql_data)
        # 操作日志
        nr = '监控配置管理-设为%s:%s' % ( qyjy_mc, '，'.join( [ '%s:%s'%(obj['mc'],obj['zt']) for obj in jkpz_lst ] ) )
        ins_czrz( db, nr, pt='wh', gnmc='监控配置管理-设为%s' % qyjy_mc )
        
def client_translate_service( sql_data ):
    """
    # 监控配置添加 翻译按钮事件
    """
    # 调用公共函数crontab_fy，传入参数Crontab配置内容，判断函数返回结果(True/False，中文翻译,message)
    r = crontab_fy(sql_data['zdfqpz'])
    if r[0]:
        # 如果公共方法执行成功，则返回函数翻译结果
        return {'state':True,'msg':r[1]}
    else:
        # 如果公共方法执行失败，则返回失败的提示消息
        return {'state':False,'msg':r[2]}
        
def jkpz_add_insert_service( sql_data ):
    """
    # 监控配置添加 保存事件
    """
    # 数据库链接
    with sjapi.connection() as db:
        # 调用公共函数crontab_fy，传入参数Crontab配置内容，判断函数返回结果(True/False，中文翻译,message)
        r = crontab_fy(sql_data['zdfqpz'])
        if r[0]:
            # 如果公共方法crontab_fy执行成功，则给配置说明赋值
            sql_data['zdfqpzsm'] = r[1]
        else:
            # 如果公共方法crontab_fy执行失败，则返回失败的提示消息
            return {'state':False,'msg':r[2]}
        # 校验名称是否唯一
        only_mc = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_jymc",sql_data)
        if only_mc:
            return {'state':False,'msg':'名称[%s]已经存在，请重新输入'%(only_mc[0]['mc'])}
        # 主键
        sql_data['id'] = get_uuid()
        # 操作人
        sql_data['czr'] = get_sess_hydm()
        # 操作时间
        sql_data['czsj'] = get_strftime()
        # 校验通过，执行插入操作
        ModSql.yw_jkgl_006_test.execute_sql_dict(db, "add_mcjy_set",sql_data)
        # 从参数表中获取ip
        sql_csb = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_csb_ip")
        if not sql_csb:
            return {'state':False,'msg':'参数代码[ywzj_ip:业务主机IP]未在参数定义表中存在'}
        sql_data['ssid'] = sql_data['id']
        sql_data['rwlx'] = 'fx'
        # 往计划任务表中插入数据
        ModSql.yw_jkgl_006_test.execute_sql_dict(db, "add_csdy_set", sql_data)
        # 若状态为启用，需要调用公共函数ins_waitexec_task，传入参数：计划任务表ID
        if sql_data['zt'] == 1:
            ins_waitexec_task(sql_csdy['id'])
        # 操作日志
        rz_add = '监控配置管理-新增监控配置：名称[%s]，描述[%s]，规则名称 [%s]，预警级别[%s]，crontab配置:[%s]，crontab配置说明：[%s]，是否可并发：[%s]，状态：[%s]'%(sql_data['mc'],sql_data['ms'],sql_data['gzid'],sql_data['yjjb'],sql_data['zdfqpz'],sql_data['zdfqpzsm'],sql_data['sfkbf'],sql_data['zt'])
        ins_czrz(db, rz_add, pt='wh', gnmc='监控配置管理-新增监控配置')
        # 返回消息结果
        return {'state':True,'msg':'新增成功'}
        
def jkpz_add_update_select_service( sql_data ):
    """
    # 监控配置添加、编辑 页面初始化
    """
    # 初始化返回值
    data = {'state':False, 'msg':'', 'fxgz_lst':[{'id':'','zwmc':'请选择'}], 'yjjb_lst':[{'bm':'','mc':'请选择'}], 'sfkbf_lst':[{'bm':'1','mc':'是'}]}
    # 数据库链接
    with sjapi.connection() as db:
        # 分析规则查询
        fxgz_lst = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_fxgz_lst")
        # 预警级别查询
        yjjb_lst = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_yjjb_lst")
        # 是否可并发查询
        sfkbf_lst = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_sfkbf_lst")
        #信息整合到返回值中
        data['fxgz_lst'].extend(fxgz_lst)
        data['yjjb_lst'].extend(yjjb_lst)
        data['sfkbf_lst'].extend(sfkbf_lst)
        # 判断是否有传来的值
        if sql_data['jkpzid']:
            # 根据id获取当前的信息
            mess = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_oneself", sql_data)
            if mess:
                # 当前的信息和返回值进行合并 并返回
                data['state'] = True
                return dict(data,**mess[0])
            else:
                data['msg'] = '未查找到编辑的信息'
        # 返回当前的信息值
        return data
        
def jkpz_update_submit_service( sql_data ):
    """
    # 监控配置编辑 保存事件
    """
    # 数据库链接
    with sjapi.connection() as db:
        # 获取原信息数据
        data_mess = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_oneself", sql_data)
        # 调用公共函数crontab_fy，传入参数Crontab配置内容，判断函数返回结果(True/False，中文翻译,message)
        r = crontab_fy(sql_data['zdfqpz'])
        if r[0]:
            # 如果公共方法crontab_fy执行成功，则给配置说明赋值
            sql_data['zdfqpzsm'] = r[1]
        else:
            # 如果公共方法crontab_fy执行失败，则返回失败的提示消息
            return {'state':False,'msg':r[2]}
        # 校验名称是否唯一
        only_mc = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_jymc",sql_data)
        if not only_mc:
            return {'state':False,'msg':'名称[%s]已经存在，请重新输入'%(sql_data['mc'])}
        # 执行更新操作
        ModSql.yw_jkgl_006_test.execute_sql_dict(db, "update_gl_jkfxpz",sql_data)
        # 判断原信息是否有值
        if data_mess:
            # 若规则ID与原规则ID不一致，需要删除参数对应表(对应的分析规则参数信息会变)
            if data_mess[0]['gzid'] != sql_data['gzid']:
                ModSql.yw_jkgl_006_test.execute_sql_dict(db, "delete_jkfxpz_gzid",sql_data)
            # 查询计划任务表ID
            jhrw_id = ModSql.yw_jkgl_006_test.execute_sql_dict(db, "select_jhrw_id",sql_data)
            # 新添加一个更新需要的参数
            sql_data['jhrwid'] = jhrw_id[0]['id']
            # 更新计划任务表中数据
            ModSql.yw_jkgl_006_test.execute_sql_dict(db, "update_jhrw",sql_data)
            # 若crontab配置，更新计划任务表中数据
            if data_mess[0]['zdfqpz'] != sql_data['zdfqpz']:
                del_waitexec_task( sql_data['jhrwid'] )
                ins_waitexec_task( sql_data['jhrwid'] )
            # 若是否可并发更新计划任务表中数据
            if data_mess[0]['sfkbf'] != sql_data['sfkbf']:
                ModSql.yw_jkgl_006_test.execute_sql_dict(db, "update_jhrw_sfkbf",sql_data)
            # 若预警级别修改了，更新计划任务表中数据
            if data_mess[0]['yjjb'] != sql_data['yjjb']:
                ModSql.yw_jkgl_006_test.execute_sql_dict(db, "update_jhrw_yjjb",sql_data)
            # 操作日志
            rz_bjq = '编辑前：[原列表信息]'%(data_mess[0])
            rz_bjh = '编辑后：[名称[%s]，描述[%s]，规则名称 [%s]，预警级别[%s]，crontab配置:[%s]，crontab配置说明：[%s]，是否可并发：[%s]]'%(sql_data['mc'],sql_data['ms'],sql_data['gzid'],sql_data['yjjb'],sql_data['mc'],sql_data['zdfqpz'],sql_data['sfkbf'])
            ins_czrz(db, '监控配置管理-编辑监控配置：%s，%s'%(rz_bjq,rz_bjh), pt='wh', gnmc='监控配置管理-编辑监控配置')
            return {'state':True,'msg':'编辑成功'}
            
if __name__ == '__main__':
#    # 测试index_service
#    sql_data = {'pt': 'wh'}
#    data = index_service( sql_data )
#    print ( '>>>>>>>>>>>>data',data )
#    # 测试data_service
#    sql_data = { 'pt': 'wh', 'mc': '', 'gzid': '', 'yjjb': '', 'sfkbf': '', 'zt': '', 'rn_start': 1, 'rn_end': 20 }
#    data = data_service( sql_data )
#    print ( '>>>>>>>>>>>>data',data )
    
    pass
    
    # 监控配置 响应动作新增 初始化
    # xydz_add_sel_service()
    
    # 监控配置 相应动作新增 响应动作改变事件
    # sql_data = {'xydzid':'luoss_jkgl_006'}
    # xydz_add_change_service( sql_data )
    
    # 监控配置 响应动作新增 保存事件
    # sql_data = {'id':get_uuid(), 'xydzid':'luoss_jkgl_test_006', 'fxjgcf':'2', 'fqfs':'1', 'jhsj': '2015051800','dzzxzj':'zhuji1,zhuji2,zhuji3'.split(','),'csdm':'csz1idm,csz2idm,csz3idm'.split(','), 'csz':'csz1,csz2,csz3'.split(','),'jkpzid':'1234567','crcs_str':'传入参数id~参数对应表~参数代码~参数说明~参数值&传入参数id~参数对应表~参数代码~参数说明~参数值'}
    # xydz_add_service(sql_data)
    
    # 监控配置 响应动作编辑 初始化
    # sql_data = {'sslb':'2', 'xydzid':'2222', 'xydzpzid':'1221'}
    # xydz_update_sel_service( sql_data )
    
    # 监控配置 响应动作编辑 保存事件
    # sql_data = {'xydzmc':'响应动作编辑xydzmc' ,'xydzid':'2222','fxjgcf':'fxjgcf1' ,'fqfs':'1', 'jhsj':'20150516', 'dzzxzj_lst':'zhuji1,zhuji2,zhuji3'.split(','), 'csid':'csz1id,csz2id,csz3id'.split(','), 'csz':'csz1,csz2,csz3'.split(','), 'xydzpzid':'1221'}
    # xydz_update_set_service( sql_data )
    
    # 监控配置 响应动作删除
    # sql_data = {'xydzpzid':'23123456789,1221'.split(',')} 
    # xydz_delete_service( sql_data )
    
    # 监控配置删除
    # sql_data = {'jkpzid':'1234567,luoss_jkgl_006'.split(',')}
    # jkpz_delete_service( sql_data )
    
    # 监控配置启用设置、禁用设置 合并
    # sql_data = {'jkpzid':'2312,1234567'.split(','), 'czr': 'czr', 'czsj': get_strftime(),'qyjy_mc':'1'}
    # update_qyjy_service( sql_data )
    
    # 监控配置添加 翻译事件-----------------------------------------------
    # sql_data = {'zdfqpz':'1 1 * * *'}
    # client_translate_service( sql_data )
    
    # 监控配置添加 保存事件
    # sql_data = {'id':get_uuid(), 'mc':'mc', 'ms':'ms', 'gzid':'gzid', 'zt':'1', 'czr': 'czr', 'czsj': get_strftime(), 'yjjb':'2','sfkbf':'1','zdfqpz':'1 1 * * *','zdfqpzsm':'zdfqpzsm'}
    # jkpz_add_insert_service( sql_data )
    
    # 监控配置新增、编辑  初始化
    # sql_data = {'jkpzid':'1234567'}
    # jkpz_add_update_select_service( sql_data )
    
    # 监控配置编辑 编辑规则参数 初始化
    # sql_data = {'sslb':'1','gzid':'luoss_jkgl_006'}
    # xydz_add_bjgzcs_service( sql_data )
    
    # 监控配置编辑 编辑规则参数 保存事件
    # sql_data = {'csid':'csz1id,csz2id,csz3id'.split(','), 'csdm':'csdm1,csdm2id,csdm3id'.split(','), 'csz':'csz1,csz2,csz3'.split(','), 'cssm':'cssm1,cssm2,cssm3'.split(','), 'jkpzid':'luoss_jkgl_006','lx':'gz', 'sjxx_str':'sjxx_str'}
    # xydz_add_bjgzcs_set_service( sql_data )
    
    # 监控配置编辑 保存事件
    # sql_data = {'jkpzid':'1234567', 'mc':'mc', 'ms':'ms', 'gzid':'gzid', 'zt':'2', 'czr': 'czr', 'czsj': get_strftime(), 'yjjb':'2','sfkbf':'2','zdfqpz':'1 1 * * *','zdfqpzsm':'zdfqpzsm'}
    # jkpz_update_submit_service( sql_data )
    
    # 响应动作列表展示
    # sql_data = {'jkpzid':'1234567'}
    # xydz_service( sql_data )
    
    # 响应动作 查询 列表展示
    # sql_data = {'xydzid':'2222','xydzpzid':'jkgl_006_t'}
    # xydz_sel_service( sql_data )