# -*- coding: utf-8 -*-
# Action: 监控管理-监控配置
# Author: zhangchl
# AddTime: 2015-05-06
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql
from sjzhtspj.common import get_hsxxb,get_bmwh_bm,get_uuid,update_jhrw,crontab_fy,get_sess_hydm,get_strftime,ins_czrz,del_waitexec_task,update_wym_yw


def index_service( sql_data ):
    """
    # 初始化交易监控页面数据准备 service
    """
    # 初始化反馈值
    data = { 'fxgz_lst': [{'id':'','zwmc':'请选择'}], 'yjjb_lst': [{'value': '', 'ms': '', 'text': '请选择'}], 
            'sfbf_lst': [{'value': '', 'ms': '', 'text': '请选择'}], 'zt_lst': [{'value': '', 'ms': '', 'text': '请选择'}], 
            'pt': sql_data['pt'] }
    with sjapi.connection() as db:
        # 分析规则[{id:id, zwmc:zwmc},{id:id, zwmc:zwmc},……]
        data['fxgz_lst'].extend( get_hsxxb( db, 'gz' ) )
        # 预警级别
        data['yjjb_lst'].extend( get_bmwh_bm( '10011', db=db ) )
        # 是否可并发
        data['sfbf_lst'].extend( get_bmwh_bm( '10007', db=db ) )
        # 状态
        data['zt_lst'].extend( get_bmwh_bm( '10001', db=db ) )
    # 将结果反馈给view
    return data

def data_service( sql_data ):
    """
    # 交易监控列表json数据 service
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    # 清理为空的查询条件
    search_lst = [ 'mc', 'gzid', 'yjjb', 'sfkbf', 'zt' ]
    for k in list(sql_data.keys()):
        if k in search_lst and sql_data[k] == '':
            del sql_data[k]
    # 数据库链接
    with sjapi.connection() as db:
        # 查询监控分析配置总条数
        total = ModSql.yw_jkgl_006.execute_sql(db, "data_count", sql_data)[0].count
        # 查询监控分析配置列表
        jbxx = ModSql.yw_jkgl_006.execute_sql_dict(db, "data_rs", sql_data)
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
            obj['yjjbmc'] = yjjb_dict.get( obj['yjjb'], obj['yjjb'] )
            obj['sfkbfmc'] = sfbf_dict.get( obj['sfkbf'], obj['sfkbf'] )
            obj['ztmc'] = zt_dict.get( obj['zt'], obj['zt'] )
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = jbxx
    # 将查询到的结果反馈给view
    return data

def jkpz_add2upd_sel_service( sql_data ):
    """
    # 监控配置新增或编辑获取初始化页面数据
    # 传入参数：
        jkpzid：编辑监控配置id
    """
    # 初始化反馈前台信息
    data = { 'state': False, 'msg': '', 'fxgz_lst': [{'id':'','zwmc':'请选择'}],
            'zxzj_lst': [{'id':'','zwmc':'请选择'}],
            'yjjb_lst': [{'value': '', 'ms': '', 'text': '请选择'}],
            'sfbf_lst': [{'value': '', 'ms': '', 'text': '请选择'}],
            'jkpz_dic': {} }
    with sjapi.connection() as db:
        # 分析规则[{id:id, zwmc:zwmc},{id:id, zwmc:zwmc},……]
        zxzj = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_zxzj")
        data['zxzj_lst'].extend(zxzj)
        data['fxgz_lst'].extend( get_hsxxb( db, 'gz' ) )
        # 预警级别
        data['yjjb_lst'].extend( get_bmwh_bm( '10011', db=db ) )
        # 是否可并发
        data['sfbf_lst'].extend( get_bmwh_bm( '10007', db=db ) )
        # 如果编辑监控配置id存在，则获取编辑对象信息
        if sql_data['jkpzid']:
            # 获取编辑信息
            rs_jkpz = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_jkpz_byid", { 'jkpzidlst': [sql_data['jkpzid']] })
            if rs_jkpz:
                data['jkpz_dic'] = rs_jkpz[0]
                fxgz_lst = [ k['id'] for k in data['fxgz_lst'] ]
                if rs_jkpz[0]['gzid'] not in fxgz_lst:
                    # 获取函数信息表中存在但分析规则中未查询出的分析规则信息
                    rs_hsxx = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_hsxx_fxgz", { 'id': rs_jkpz[0]['gzid'] })
                    if rs_hsxx:
                        data['fxgz_lst'].extend( rs_hsxx )
                data['state'] = True
            else:
                data['msg'] = '编辑监控信息未查询到'
        else:
            data['state'] = True
    
    return data

def jkpz_add_service( sql_data ):
    """
    # 新增提交 service
    """
    # 初始化反馈信息
    result = {'state':False, 'msg':''}
    # 数据库链接
    with sjapi.connection() as db:
        # 校验名称是否唯一
        rs_check = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_check_jkfxpzmc",sql_data)
        # 此名称已经在数据库中存在，不允许再次追加
        if rs_check:
            result['msg'] = '名称[%s]已经存在，请重新输入'%(sql_data['mc'])
            return result
        
        # 调用公共函数crontab_fy，传入参数Crontab配置内容，判断函数返回结果(True/False，中文翻译,message)
        r = crontab_fy(sql_data['zdfqpz'])
        if r[0]:
            # 如果公共方法crontab_fy执行成功，则给配置说明赋值
            sql_data['zdfqpzsm'] = r[1]
        else:
            # 如果公共方法crontab_fy执行失败，则返回失败的提示消息
            result['msg'] = r[2]
            return result
        
        # 校验通过，执行插入操作
        # 监控分析配置表
        # 主键
        sql_data['jkpzid'] = get_uuid()
        # 操作人
        sql_data['czr'] = get_sess_hydm()
        # 操作时间
        sql_data['czsj'] = get_strftime()
        ModSql.yw_jkgl_006.execute_sql_dict(db, "add_jkfxpz",sql_data)
        # 往计划任务表中插入数据
        #   从参数表中获取ip
        rs_zxzjip = ModSql.common.execute_sql_dict(db, "get_xx_csdy")
        if not rs_zxzjip:
            result['msg'] = '参数代码[YWZJ_IP:业务主机IP]未在参数定义表中存在'
            db.rollback()
            return result
        else:
            # 计划任务所属id
            sql_data['ssid'] = sql_data['jkpzid']
            # 任务类型(分析)
            sql_data['rwlx'] = 'fx'
            # 计划任务执行主机
            sql_data['ip'] = sql_data['zxzj'] if sql_data['zxzj'] else rs_zxzjip[0]['value']
            # 调用公共函数：操作计划任务
            update_jhrw( db, sql_data['zt'], '', upd_dic = sql_data )
        # 更新监控分析配置唯一码
        update_wym_yw( db, 'jkpzgl', sql_data['jkpzid'] )
        # 操作日志
        rz_add = '监控配置管理-新增监控配置：名称[%s]，描述[%s]，规则名称 [%s]，预警级别[%s]，crontab配置:[%s]，crontab配置说明：[%s]，是否可并发：[%s]，状态：[%s]'%(
            sql_data['mc'],sql_data['ms'],sql_data['gzmc'],sql_data['yjjbmc'],sql_data['zdfqpz'],sql_data['zdfqpzsm'],
            sql_data['sfkbfmc'], '启用' if sql_data['zt'] == '1' else '禁用')
        ins_czrz(db, rz_add, pt='wh', gnmc='监控配置管理-新增监控配置')
        # 组织反馈信息
        sql_data['id'] = sql_data['jkpzid']
        result['jkpz_dic'] = sql_data
        result['state'] = True
        result['msg'] = '新增成功'
    
    return result

def jkpz_upd_service( sql_data ):
    """
    # 编辑提交 service
    """
    # 初始化反馈信息
    result = {'state':False, 'msg':''}
    # 数据库链接
    with sjapi.connection() as db:
        # 调用公共函数crontab_fy，传入参数Crontab配置内容，判断函数返回结果(True/False，中文翻译,message)
        r = crontab_fy(sql_data['zdfqpz'])
        if r[0]:
            # 如果公共方法crontab_fy执行成功，则给配置说明赋值
            sql_data['zdfqpzsm'] = r[1]
        else:
            # 如果公共方法crontab_fy执行失败，则返回失败的提示消息
            result['msg'] = r[2]
            return result
        # 校验名称是否唯一
        rs_check = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_check_jkfxpzmc",sql_data)
        # 此名称已经在数据库中存在，不允许再次追加
        if rs_check:
            result['msg'] = '名称[%s]已经存在，请重新输入'%(sql_data['mc'])
            return result
        # 首先获取原有信息
        yjkpz_obj_lst = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_jkpz_byid", { 'jkpzidlst': [sql_data['jkpzid']] })
        if not yjkpz_obj_lst:
            result['msg'] = '未查询到编辑监控配置信息，请刷新页面后重试'
            return result
        # 原监控配置对象
        yjkpz_obj = yjkpz_obj_lst[0]
        # 编辑监控配置信息
        # 操作人
        sql_data['czr'] = get_sess_hydm()
        # 操作时间
        sql_data['czsj'] = get_strftime()
        # 执行sql
        ModSql.yw_jkgl_006.execute_sql_dict(db, "update_jkfxpz",sql_data)  
        # 修改执行主机
        #   从参数表中获取ip
        rs_zxzjip = ModSql.common.execute_sql_dict(db, "get_xx_csdy")
        if not rs_zxzjip:
            result['msg'] = '参数代码[YWZJ_IP:业务主机IP]未在参数定义表中存在'
            db.rollback()
            return result
        # 执行主机未选择时，默认系统参数中定义的执行主机
        sql_data['zxzj'] = sql_data['zxzj'] if sql_data['zxzj'] else rs_zxzjip[0]['value']
        ModSql.yw_jkgl_006.execute_sql_dict(db, "update_jkzxzjpz",sql_data) 
        # 若规则ID与原规则ID不一致，需要删除参数对应表(对应的分析规则参数信息会变)
        if yjkpz_obj['gzid'] != sql_data['gzid']:
            # 执行删除参数对应表
            ModSql.yw_jkgl_006.execute_sql_dict(db, "delete_csdyb_byssid",{'ssid': sql_data['jkpzid']})
        # 计划任务更新
        # 计划任务所属id
        sql_data['ssid'] = sql_data['jkpzid']
        # 任务类型(分析)
        sql_data['rwlx'] = 'fx'
        # 调用公共函数：操作计划任务
        # 原是否可并发
        ysfkbf = yjkpz_obj['sfkbf']
        # 原预警级别
        yyjjb = yjkpz_obj['yjjb']
        # 调用公共函数操作计划任务
        update_jhrw( db, yjkpz_obj['zt'], yjkpz_obj['zdfqpz'], upd_dic = sql_data, sfxz = False, ysfkbf = ysfkbf, yyjjb = yyjjb )
        # 更新监控分析配置唯一码
        update_wym_yw( db, 'jkpzgl', sql_data['jkpzid'] )
        # 登记操作日志
        # 修改前信息
        # 分析规则
        fxgz_lst = get_hsxxb( db, 'gz' )
        fxgz_dic = dict( [ ( obj['id'], obj['zwmc'] ) for obj in fxgz_lst ] )
        # 预警级别
        yjjb_lst = get_bmwh_bm( '10011', db=db )
        yjjb_dic = dict( [ ( obj['value'], obj['text'] ) for obj in yjjb_lst ] )
        # 是否可并发
        sfbf_lst = get_bmwh_bm( '10007', db=db )
        sfbf_dic = dict( [ ( obj['value'], obj['text'] ) for obj in sfbf_lst ] )
        # 原有信息
        old_xx = '名称[%s]，描述[%s]，规则名称 [%s]，预警级别[%s]，crontab配置:[%s]，crontab配置说明：[%s]，是否可并发：[%s]，状态：[%s],执行主机：[%s]'%(
            yjkpz_obj['mc'],yjkpz_obj['ms'],fxgz_dic.get( yjkpz_obj['gzid'], yjkpz_obj['gzid'] ),
            yjjb_dic.get( yjkpz_obj['yjjb'], yjkpz_obj['yjjb'] ),yjkpz_obj['zdfqpz'],yjkpz_obj['zdfqpzsm'],
            sfbf_dic.get( yjkpz_obj['sfkbf'], yjkpz_obj['sfkbf'] ), '启用' if yjkpz_obj['zt'] == '1' else '禁用',yjkpz_obj['zxzj'])
        # 修改后信息
        now_xx = '名称[%s]，描述[%s]，规则名称 [%s]，预警级别[%s]，crontab配置:[%s]，crontab配置说明：[%s]，是否可并发：[%s]，状态：[%s],执行主机：[%s]'%(
            sql_data['mc'],sql_data['ms'],sql_data['gzmc'],sql_data['yjjbmc'],sql_data['zdfqpz'],sql_data['zdfqpzsm'],
            sql_data['sfkbfmc'], '启用' if sql_data['zt'] == '1' else '禁用',sql_data['zxzj'])
        # 最终编辑内容
        nr = '监控配置管理-编辑监控配置：编辑前：[%s]，编辑后：[%s]' % ( old_xx, now_xx )
        ins_czrz(db, nr, pt='wh', gnmc='监控配置管理-编辑监控配置')
        # 组织反馈信息
        sql_data['id'] = sql_data['jkpzid']
        result['jkpz_dic'] = sql_data
        result['state'] = True
        result['msg'] = '编辑成功'
    
    return result

def jkpz_gzcs_sel_service( sql_data ):
    """
    #  编辑规则参数，页面初始化service
    """
    # 初始化反馈前台信息
    data = { 'state': False, 'msg': '', 'gzmc': '', 'gzms': '', 'gzcs_lst': [], 'ycsxx_str': '' }
     # 数据库链接
    with sjapi.connection() as db:
        # 查询规则信息
        gzxx_lst = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_gzxx", sql_data)
        if gzxx_lst:
            # 规则信息
            gzxx = gzxx_lst[0]
            data['gzmc'] = gzxx['zwmc']
            data['gzms'] = gzxx['ms']
            # 参数信息列表展示信息
            # 所属类别：1：规则
            sql_data['sslb'] = '1'
            sql_data['crcsssid'] = sql_data['gzid']
            sql_data['csdybssid'] = sql_data['jkpzid']
            # 规则列表
            data['gzcs_lst'] = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_csxx", sql_data)
            # 原参数信息
            data['ycsxx_str'] = '；'.join( [ '参数代码：%s，参数说明：%s，参数值：%s' % ( obj['csdm'], obj['cssm'], obj['csz'] ) for obj in data['gzcs_lst'] ] )
            # 获取数据成功
            data['state'] = True
        else:
            data['msg'] = '未获取到规则信息，请刷新页面后重试'
    return data

def jkpz_gzcs_add2edit_service( sql_data ):
    """
    #  编辑规则参数，新增或编辑提交 service
    """
    # 数据库链接
    with sjapi.connection() as db:
        # 执行删除参数对应表
        ModSql.yw_jkgl_006.execute_sql_dict(db, "delete_csdyb_byssid",sql_data)
        # 循环更新参数对应表
        csxx_lst = []
        # 参数集合字符串( 传入参数id~参数对应表~参数代码~参数说明~参数值&传入参数id~参数对应表~参数代码~参数说明~参数值 )
        for row_str in sql_data['crcs_str'].split('&'):
            # 传入参数id~参数对应表~参数代码~参数说明~参数值
            if row_str:
                row_lst = row_str.split('~')
                # 判断参数值是否为空，为空时不进行插入
                if row_lst[4] != '':
                    # 组织传入参数对应表的SQL参数  参数对应表（ID,传入参数ID，参数值，类型，所属ID） 
                    sql_csdyb = {'id':get_uuid(), 'csid':row_lst[0], 'csz':row_lst[4], 'lx':'gz', 'ssid':sql_data['jkpzid'] }
                    ModSql.yw_jkgl_006.execute_sql_dict(db, "add_csdyb", sql_csdyb)
                    # 更新参数对应表唯一码
                    update_wym_yw(db,'csdyb',sql_csdyb['id'])
                    csxx_lst.append( '参数代码：%s，参数说明：%s，参数值：%s' % ( row_lst[2], row_lst[3], row_lst[4] ) )
        # 更新监控分析配置唯一码
        update_wym_yw( db, 'jkpzgl', sql_data['jkpzid'] )
        # 调用操作日志公共方法
        csxx_str = '；'.join( csxx_lst )
        ins_czrz(db, '监控配置管理-编辑规则参数：编辑前：[%s]，编辑后：[%s]'%(sql_data['ycsxx_str'], csxx_str), pt='wh', gnmc='监控配置管理-编辑规则参数')
        # 返回消息结果
        return {'state':True,'msg':'编辑成功'}

def jkpz_del_service( sql_data ):
    """
    # 删除监控配置 service
    """
    # 数据库链接
    with sjapi.connection() as db:
        # 查询删除监控配置信息
        yjkpz_obj_lst = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_jkpz_byid", sql_data)
        # 删除响应动作配置-参数对应表
        ModSql.yw_jkgl_006.execute_sql_dict(db, "delete_csdyb_byjkpzidlst", sql_data)
        # 删除响应动作配置-动作执行主机
        ModSql.yw_jkgl_006.execute_sql_dict(db, "delete_dzzxzj_byjkpzidlst", sql_data)
        # 删除响应动作配置表
        ModSql.yw_jkgl_006.execute_sql_dict(db, "delete_xydzpz_byjkpzidlst", sql_data)
        # 删除监控分析配置-参数对应表
        ModSql.yw_jkgl_006.execute_sql_dict(db, "delete_csdyb_byssidlst", {'ssidlst': sql_data['jkpzidlst']})
        # 查询计划任务表ID,删除当日执行计划表
        jhrwid_lst = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_jhrwb_byssidlst", sql_data)
        # 删除当日执行计划任务
        if jhrwid_lst:
            for obj in jhrwid_lst:
                del_waitexec_task( obj['id'], db )
            # 删除计划任务
            ModSql.yw_jkgl_006.execute_sql_dict(db, "delete_jhrwb_byssidlst", sql_data)
        # 删除监控分析配置表
        ModSql.yw_jkgl_006.execute_sql_dict(db, "delete_jkfxpz_byjkpzidlst", sql_data)
        # 组织日志内容
        # 分析规则
        fxgz_lst = get_hsxxb( db, 'gz' )
        fxgz_dic = dict( [ ( obj['id'], obj['zwmc'] ) for obj in fxgz_lst ] )
        # 预警级别
        yjjb_lst = get_bmwh_bm( '10011', db=db )
        yjjb_dic = dict( [ ( obj['value'], obj['text'] ) for obj in yjjb_lst ] )
        # 是否可并发
        sfbf_lst = get_bmwh_bm( '10007', db=db )
        sfbf_dic = dict( [ ( obj['value'], obj['text'] ) for obj in sfbf_lst ] )
        # 删除信息列表
        del_jkfxpz_lst = []
        # 获取详细信息集合
        for yjkpz_obj in yjkpz_obj_lst:
            del_jkfxpz_lst.append('监控配置名称[%s], 分析规则名称[%s]，状态[%s]，预警级别[%s]，是否可并发[%s]，crontab配置[%s]，crontab配置说明[%s]' % (
                yjkpz_obj['mc'],fxgz_dic.get( yjkpz_obj['gzid'], yjkpz_obj['gzid'] ),
                '启用' if yjkpz_obj['zt'] == '1' else '禁用', yjjb_dic.get( yjkpz_obj['yjjb'], yjkpz_obj['yjjb'] ),
                sfbf_dic.get( yjkpz_obj['sfkbf'], yjkpz_obj['sfkbf'] ),yjkpz_obj['zdfqpz'],yjkpz_obj['zdfqpzsm'] )
            )
        nr = '监控配置管理-删除监控配置:%s' % ( '；'.join( del_jkfxpz_lst ) )
        ins_czrz(db, nr, pt='wh', gnmc='监控配置管理-删除监控配置')
        # 返回消息结果
        return {'state':True,'msg':'删除成功'}

def jkpz_qyjy_service( sql_data ):
    """
    # 监控配置启用禁用 service
    """
    qyjy_type_mc = '启用' if sql_data['qyjy_type'] =='1' else '禁用'
    # 数据库链接
    with sjapi.connection() as db:
        # 查询启用、禁用监控配置信息
        yjkpz_obj_lst = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_jkpz_byid", sql_data)
        # 获取操作监控配置id列表
        jkpz_obj_lst = [ obj for obj in yjkpz_obj_lst if obj['zt'] != sql_data['qyjy_type']  ]
        # 判断可操作监控分析配置是否为空，如果为空则直接反馈给前台
        if jkpz_obj_lst == []:
            return {'state':False,'msg':'选择的列表中的状态都为%s，无需再设' % ( qyjy_type_mc )}
        # 调用公共方法，操作计划任务
        for jkpz_obj in jkpz_obj_lst:
            jkpz_obj['rwlx'] = 'fx'
            yzt = jkpz_obj['zt']
            jkpz_obj['zt'] = sql_data['qyjy_type']
            jkpz_obj['ssid'] = jkpz_obj['id']
            # 清空id，调用方法中重新生产计划任务表id
            jkpz_obj['id'] = ''
            update_jhrw( db, yzt, jkpz_obj['zdfqpz'], upd_dic = jkpz_obj, sfxz = False )
        # 更新监控分析配置表状态
        # 操作人
        sql_data['czr'] = get_sess_hydm()
        # 操作时间
        sql_data['czsj'] = get_strftime()
        # 状态
        sql_data['zt'] = sql_data['qyjy_type']
        # 执行监控配置启用禁用
        ModSql.yw_jkgl_006.execute_sql_dict(db, "update_jkfxpz_byjkpzidlst", sql_data)
        # 更新监控分析配置唯一码
        for id in sql_data['jkpzidlst']:
            update_wym_yw( db, 'jkpzgl', id )
        # 写行员日常运维流水
        nr = '监控配置管理-设为%s:%s' % ( qyjy_type_mc, '，'.join( [ obj['mc'] for obj in jkpz_obj_lst ] ) )
        ins_czrz( db, nr, pt='wh', gnmc='监控配置管理-设为%s' % qyjy_type_mc )
        # 返回消息结果
        return {'state':True,'msg':'%s成功' % qyjy_type_mc}

def data_xydz_service( sql_data ):
    """
    # 交易监控列表json数据 service
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询交易总条数
        total = ModSql.yw_jkgl_006.execute_sql(db, "data_xydz_count", sql_data)[0].count
        # 查询交易列表
        jbxx = ModSql.yw_jkgl_006.execute_sql_dict(db, "data_xydz_rs", sql_data)
        # 执行主机字典
        zxzj_dic = {}
        if jbxx:
            # 根据本页响应动作查询对应执行主机信息 
            zxzj_lst = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_dzzxzj_byxydzidlst", { 'xydzidlst': [ obj['id'] for obj in jbxx ] })
            for obj in zxzj_lst:
                if obj['xydzid'] not in zxzj_dic:
                    zxzj_dic[ obj['xydzid'] ] = []
                zxzj_dic[ obj['xydzid'] ].append( '%s(%s)' % ( obj['mc'], obj['zjip'] ) )
        # 分析触发
        fxjgcf_lst = get_bmwh_bm( '10012', db=db )
        # 分析触发字典
        fxjgcf_dict = dict( [(xx['value'], xx['text']) for xx in fxjgcf_lst ] )
        # 对结果集中状态进行翻译
        for obj in jbxx:
            obj['fxjgcfmc'] = fxjgcf_dict.get( obj['fxjgcf'], obj['fxjgcf'] )
            obj['dzzxzj'] = zxzj_dic.get( obj['id'], '' )
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = jbxx
    # 将查询到的结果反馈给view
    return data

def xydz_add2upd_sel_service( sql_data ):
    """
    # 响应动作新增或编辑获取初始化页面数据
    # 传入参数：
        xydzid：响应动作id
    """
    # 初始化反馈前台信息
    data = { 'state': False, 'msg': '', 'xydz_lst': [{'id':'','zwmc':'请选择'}],
            'fxjgcf_lst': [], 'fqfs_lst': [],
            'dzzxzj_lst': [{'ip': '', 'mc': '请选择'}], 'xydzcs_lst': [],
            'xydz_dic': {} }
    with sjapi.connection() as db:
        # 响应动作[{id:id, zwmc:zwmc},{id:id, zwmc:zwmc},……]
        data['xydz_lst'].extend( get_hsxxb( db, 'dz' ) )
        # 分析结果触发
        data['fxjgcf_lst'].extend( get_bmwh_bm( '10012', db=db ) )
        # 发起方式
        data['fqfs_lst'].extend( get_bmwh_bm( '10004', db=db ) )
        # 动作执行主机 
        data['dzzxzj_lst'].extend( ModSql.yw_jkgl_006.execute_sql_dict(db, "select_zjxx") )
        # 如果编辑响应动作id存在，则获取编辑对象信息
        if sql_data['xydzid']:
            # 获取编辑信息
            rs_xydz = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_xydz_byidlst", { 'xydzidlst': [sql_data['xydzid']] })
            if rs_xydz:
                # 响应动作信息
                data['xydz_dic'] = rs_xydz[0]
                # 获取对应执行主机信息
                zxzj_lst = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_dzzxzj_byxydzidlst", { 'xydzidlst': [sql_data['xydzid']] })
                data['xydz_dic']['zxzj_lst'] = [ obj['zjip'] for obj in zxzj_lst ]
                data['xydz_dic']['zxzj_str'] = ','.join( [ obj['zjip'] for obj in zxzj_lst ] )
                data['xydz_dic']['zxzjmc_str'] = ','.join( [ '%s(%s)' % ( obj['mc'], obj['zjip'] ) for obj in zxzj_lst ] )
                # 获取对应的输入参数
                sql_data['sslb'] = '2'
                sql_data['crcsssid'] = data['xydz_dic']['dzid']
                sql_data['csdybssid'] = data['xydz_dic']['id']
                # 输入参数列表
                data['xydzcs_lst'] = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_csxx", sql_data)
                # 原参数信息
                data['ycsxx_str'] = '；'.join( [ '参数代码：%s，参数说明：%s，参数值：%s' % ( obj['csdm'], obj['cssm'], obj['csz'] ) for obj in data['xydzcs_lst'] ] )
                data['state'] = True
            else:
                data['msg'] = '编辑响应动作未查询到'
        else:
            data['state'] = True
    # 返回结果
    return data
    
def xydz_crcs_init_service( sql_data ):
    """
    # 响应动作输入参数列表
    """
    data = {'total':0, 'rows':[]}
    with sjapi.connection() as db:
        # 参数信息列表展示信息
        # 所属类别：2：响应动作
        sql_data['sslb'] = '2'
        sql_data['crcsssid'] = sql_data['dzid']
        sql_data['csdybssid'] = sql_data['xydzid']
        # 输入参数列表
        data['rows'] = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_csxx", sql_data)
    return data

def xydz_add_service( sql_data ):
    """
    # 响应动作新增提交 service
    """
    # 初始化反馈信息
    result = {'state':False, 'msg':''}
    # 数据库链接
    with sjapi.connection() as db:
        # 响应动作配置表
        # 主键
        sql_data['xydzid'] = get_uuid()
        ModSql.yw_jkgl_006.execute_sql_dict(db, "add_xydzpz",sql_data)
        # 循环插入到动作执行主机表（动作执行主机下拉框可以多选）
        for ip in [ ip for ip in sql_data['dzzxzj'].split(',') if ip != '' ]:
            zjxx_dic = { 'id': get_uuid(), 'zjip': ip, 'dzid': sql_data['xydzid'] }
            ModSql.yw_jkgl_006.execute_sql_dict(db, "add_dzzxzj", zjxx_dic)
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
                    # 更新参数对应表唯一码
                    update_wym_yw(db,'csdyb',sql_csdyb['id'])
                    csxx_lst.append( '参数代码：%s，参数说明：%s，参数值：%s' % ( row_lst[2], row_lst[3], row_lst[4] ) )
        # 更新监控分析配置唯一码
        update_wym_yw( db, 'jkpzgl', sql_data['ssjkfxid'] )
        # 操作日志
        # 获取监控分析配置名称
        rs_jkpz = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_jkpz_byid", { 'jkpzidlst': [sql_data['ssjkfxid']] })
        jkpzmc = rs_jkpz[0]['mc'] if rs_jkpz else sql_data['ssjkfxid']
        rz_add = '监控配置管理-新增响应动作：监控配置名称[%s],响应动作名称[%s]，分析结果触发[%s]，发起方式[%s]，计划时间[%s]，动作执行主机：[%s]，参数列表：[%s]'%(
            jkpzmc,sql_data['dzmc'],sql_data['fxjgcfmc'],sql_data['fqfsmc'],sql_data['jhsj'],sql_data['dzzxzjmc'],
            '；'.join( csxx_lst )
            )
        ins_czrz(db, rz_add, pt='wh', gnmc='监控配置管理-新增响应动作')
        result['state'] = True
        result['msg'] = '新增成功'
    
    return result

def xydz_upd_service( sql_data ):
    """
    # 响应动作编辑提交 service
    """
    # 初始化反馈信息
    result = {'state':False, 'msg':''}
    # 数据库链接
    with sjapi.connection() as db:
        # 首先获取原有信息
        yxydz_obj_lst = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_xydz_byidlst", { 'xydzidlst': [sql_data['xydzid']] })
        if not yxydz_obj_lst:
            result['msg'] = '未查询到响应动作配置信息，请刷新页面后重试'
            return result
        # 原响应动作配置信息
        yxydz_obj = yxydz_obj_lst[0]
        # 编辑响应动作信息
        # 执行sql
        ModSql.yw_jkgl_006.execute_sql_dict(db, "update_xydzpz",sql_data)
        # 循环插入到动作执行主机表（动作执行主机下拉框可以多选）
        yzxzj_lst = sorted( [ ip for ip in sql_data['zxzjstr'].split(',') if ip ] )
        zxzj_lst = sorted( [ ip for ip in sql_data['dzzxzj'].split(',') if ip ] )
        # 执行主机有修改，则先删除，在新增
        if yzxzj_lst != zxzj_lst:
            # 删除
            ModSql.yw_jkgl_006.execute_sql_dict(db, "delete_dzzxzj", { 'ssidlst': [sql_data['xydzid']] })
            # 新增
            for ip in zxzj_lst:
                zjxx_dic = { 'id': get_uuid(), 'zjip': ip, 'dzid': sql_data['xydzid'] }
                ModSql.yw_jkgl_006.execute_sql_dict(db, "add_dzzxzj", zjxx_dic)
        # 循环更新参数对应表
        # 执行删除参数对应表
        ModSql.yw_jkgl_006.execute_sql_dict( db, "delete_csdyb_byssid",{'ssid': sql_data['xydzid']} )
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
                    # 更新参数对应表唯一码
                    update_wym_yw(db,'csdyb',sql_csdyb['id'])
                    csxx_lst.append( '参数代码：%s，参数说明：%s，参数值：%s' % ( row_lst[2], row_lst[3], row_lst[4] ) )
        
        # 更新监控分析配置唯一码
        update_wym_yw( db, 'jkpzgl', yxydz_obj['ssjkfxid'] )
        # 登记操作日志
        # 修改前信息
        # 分析结果触发
        fxjgcf_lst = get_bmwh_bm( '10012', db=db )
        fxjgcf_dict = dict( [ ( obj['value'], obj['text'] ) for obj in fxjgcf_lst ] )
        # 发起方式
        fqfs_lst = get_bmwh_bm( '10004', db=db )
        fqfs_dict = dict( [ ( obj['value'], obj['text'] ) for obj in fqfs_lst ] )
        # 原有信息
        old_xx = '分析结果触发[%s]，发起方式[%s]，计划时间[%s]，动作执行主机：[%s]，参数列表：[%s]'%(
            fxjgcf_dict.get( yxydz_obj['fxjgcf'], '' ), fqfs_dict.get( yxydz_obj['fqfs'], '' ), 
            yxydz_obj['jhsj'] if yxydz_obj['jhsj'] else '', sql_data['zxzjmcstr'], sql_data['xydzycsxxstr'] )
        # 修改后信息
        now_xx = '分析结果触发[%s]，发起方式[%s]，计划时间[%s]，动作执行主机：[%s]，参数列表：[%s]'%(
            sql_data['fxjgcfmc'],sql_data['fqfsmc'],sql_data['jhsj'],sql_data['dzzxzjmc'],
            '；'.join( csxx_lst ) )
        # 最终编辑内容
        # 获取监控分析配置名称
        rs_jkpz = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_jkpz_byid", { 'jkpzidlst': [sql_data['ssjkfxid']] })
        jkpzmc = rs_jkpz[0]['mc'] if rs_jkpz else sql_data['ssjkfxid']
        nr = '监控配置管理-编辑响应动作：监控配置名称[%s]，响应动作名称[%s]，编辑前：[%s]，编辑后：[%s]' % ( 
            jkpzmc,sql_data['dzmc'],old_xx, now_xx )
        ins_czrz(db, nr, pt='wh', gnmc='监控配置管理-编辑响应动作')
        result['state'] = True
        result['msg'] = '编辑成功'
    
    return result
    
def xydz_del_service( sql_data ):
    """
    # 删除响应动作 service
    """
    # 数据库链接
    with sjapi.connection() as db:
        # 查询删除响应动作信息
        yxydz_obj_lst = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_xydz_byidlst", sql_data)
        # 根据动作id列表获取各个动作执行主机信息select_dzzxzj_byxydzidlst
        xydz_zxzj_lst = ModSql.yw_jkgl_006.execute_sql_dict( db, "select_dzzxzj_byxydzidlst", sql_data )
        xydzid2zxzj_dic = {}
        for obj in xydz_zxzj_lst:
            if obj['xydzid'] not in xydzid2zxzj_dic:
                xydzid2zxzj_dic[obj['xydzid']] = []
            xydzid2zxzj_dic[obj['xydzid']].append( obj['zjip'] )
        # 删除响应动作配置表
        ModSql.yw_jkgl_006.execute_sql_dict(db, "delete_xydzpz_byxydzidlst", sql_data)
        # 删除动作执行主机
        ModSql.yw_jkgl_006.execute_sql_dict(db, "delete_dzzxzj", {'ssidlst': sql_data['xydzidlst']})
        # 删除参数对应表
        ModSql.yw_jkgl_006.execute_sql_dict(db, "delete_csdyb_byssidlst", {'ssidlst': sql_data['xydzidlst']})
        
        # 更新监控分析配置唯一码
        update_wym_yw( db, 'jkpzgl', yxydz_obj_lst[0]['ssjkfxid'] )
        # 组织日志内容
        # 响应动作[{id:id, zwmc:zwmc},{id:id, zwmc:zwmc},……]
        xydz_lst = get_hsxxb( db, 'dz' )
        xydz_dic = dict( [ ( obj['id'], obj['zwmc'] ) for obj in xydz_lst ] )
        # 分析结果触发
        fxjgcf_lst = get_bmwh_bm( '10012', db=db )
        fxjgcf_dict = dict( [ ( obj['value'], obj['text'] ) for obj in fxjgcf_lst ] )
        # 发起方式
        fqfs_lst = get_bmwh_bm( '10004', db=db )
        fqfs_dict = dict( [ ( obj['value'], obj['text'] ) for obj in fqfs_lst ] )
        # 删除信息列表
        del_xydzpz_lst = []
        # 获取详细信息集合
        for xydzpz_obj in yxydz_obj_lst:
            del_xydzpz_lst.append('响应动作名称[%s]，分析结果触发[%s]，发起方式[%s]，计划时间[%s]，动作执行主机：[%s]' % (
                xydz_dic.get( xydzpz_obj['dzid'], xydzpz_obj['dzid'] ),
                fxjgcf_dict.get( xydzpz_obj['fxjgcf'], xydzpz_obj['fxjgcf'] ),
                fqfs_dict.get( xydzpz_obj['fqfs'], xydzpz_obj['fqfs'] ),
                xydzpz_obj['jhsj'], ','.join( xydzid2zxzj_dic.get(xydzpz_obj['id'],[]) )
                )
            )
        # 获取监控分析配置名称
        rs_jkpz = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_jkpz_byid", { 'jkpzidlst': [xydzpz_obj['ssjkfxid']] })
        jkpzmc = rs_jkpz[0]['mc'] if rs_jkpz else xydzpz_obj['ssjkfxid']
        nr = '监控配置管理-删除响应动作：监控配置名称[%s]：%s' % ( jkpzmc, '；'.join( del_xydzpz_lst ) )
        ins_czrz(db, nr, pt='wh', gnmc='监控配置管理-删除响应动作')
        # 返回消息结果
        return {'state':True,'msg':'删除成功'}
        
def xydz_csck_sel_service( sql_data ):
    """
    # 响应动作传入参数查看 service
    """
    # 初始化反馈前台信息
    data = { 'state': False, 'msg': '', 'xydzcs_lst': [] }
    with sjapi.connection() as db:
        # 获取对应的输入参数
        sql_data['sslb'] = '2'
        sql_data['crcsssid'] = sql_data['dzid']
        sql_data['csdybssid'] = sql_data['xydzid']
        # 输入参数列表
        data['xydzcs_lst'] = ModSql.yw_jkgl_006.execute_sql_dict(db, "select_csxx", sql_data)
        data['state'] = True
    
    # 返回结果
    return data