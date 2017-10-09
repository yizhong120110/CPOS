# -*- coding: utf-8 -*-
# Action: 交易列表Service
# Author: zhangzf
# AddTime: 2015-1-4
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import logger, get_sess_hydm, ModSql
from sjzhtspj.common import update_wym, get_strftime, get_uuid, ins_czrz, update_jhrw
from sjzhtspj.esb import memcache_data_del

def index_service(ywid):
    """
    # 交易列表首页
    """
    data = {'ywmc':None, 'ywid': ywid}
    with sjapi.connection() as db:
        re = ModSql.kf_ywgl_024.execute_sql_dict(db, "get_yw", {'ywid':ywid})[0]
        data['ywmc'] = re['ywmc']
    return data
    
def data_service(ywid, search_name, search_value, rn_start, rn_end):
    """
    # 交易列表查询
    """
    data = {'total':0, 'rows':[]}
    # 存在查询条件
    with sjapi.connection() as db:
        sql_data_count = {'ywid':ywid}
        sql_data = {'ywid':ywid, 'rn_start': rn_start, 'rn_end': rn_end}
        if search_value:
            sql_data_count['searchFild_lst'] = [(search_name,search_value)]
            sql_data['searchFild_lst'] = [(search_name,search_value)]
        # 查询交易总条数
        data['total'] = ModSql.kf_ywgl_024.execute_sql(db, "get_jydy_count", sql_data_count)[0].count
        # 查询交易
        data['rows'] = ModSql.kf_ywgl_024.execute_sql_dict(db, "get_jydy", sql_data)
        # 查询唯一码，用于判断流程是否有未提交的修改
        wym = ModSql.kf_ywgl_024.execute_sql_dict(db, "get_wym", {'ywid':ywid})
        row_dic = dict((row['id'], '1' if row['wym1']==row['wym2'] else '0') for row in wym)
        for row in data['rows']:
            row['bbsftj'] = row_dic[row['id']]
    
    return data

def add_service(ssywid, jymc, jym, jyms, jyzt):
    """
    # 添加交易
    """
    
    # 当前登录人
    hydm = get_sess_hydm()
    # id
    id = get_uuid()
    # 操作时间
    czsj = get_strftime()
    # 超时时间
    timeout = 50
    result = {'state':False, 'msg':''}
    # 查询数据库中是否有该交易码
    with sjapi.connection() as db:
        total = ModSql.kf_ywgl_024.execute_sql(db, "check_wym", {'jym':jym})[0].count
        if(total>0):
            result['msg'] = '交易码['+jym+']已经存在，请重新输入'
            return result
        # 插入开始节点
        sql_data = {'lcid':get_uuid(), 'ssjyid':id, 'type':'10', 'type_bj':'5', 'x':50, 'y':50}
        ModSql.kf_ywgl_024.execute_sql(db, "add_jd", sql_data)
        # 插入结束节点
        sql_data = {'lcid':get_uuid(), 'ssjyid':id, 'type':'11', 'type_bj':'6', 'x':300, 'y':300}
        ModSql.kf_ywgl_024.execute_sql(db, "add_jd", sql_data)
        # 添加定义
        sql_data = {'id':id, 'ssywid':ssywid, 'jym':jym, 'jymc':jymc, 'jyms':jyms,'timeout':timeout, 'hyobj':hydm, 'czsj':czsj, 'jyzt':jyzt}
        ModSql.kf_ywgl_024.execute_sql(db, "add_jydy", sql_data)
        # 更新唯一码
        update_wym(db,'jy',id)
        # 操作流水登记
        ins_czrz( db, '交易新增：交易码[%s]，交易名称[%s]，交易描述[%s]，交易状态[%s]，所属业务ID[%s]' % ( jym, jymc, jyms, jyzt, ssywid), gnmc = '交易管理_新增' )
    result['state'] = True
    result['msg'] = '新增成功'
    return result

def del_service(ids_lst):
    """
    # 删除交易
    """
    
    # 要删除的交易名称
    rs_jymc = []
    result = {'state':False, 'msg':''}
    # 查询交易名称
    with sjapi.connection() as db:
        rs_jymc = ModSql.kf_ywgl_024.execute_sql_dict(db, "get_jy_name", {'ids_lst':ids_lst})
        # 删除节点要素，节点要素步骤，交易参数案例定义，流程走向，流程布局，（导入流水'del_drls'，已修改），参数定义，交易定义
        del_list = ['del_jdys', 'del_jdysbz', 'del_jycsaldy', 'del_lczx', 'del_lcbj', 'del_csdy', 'del_drzxrw', 'del_jhrw', 'del_jydy']
        for db_method in del_list:
            ModSql.kf_ywgl_024.execute_sql_dict(db, db_method, {'ids_lst':ids_lst})
        # 删除blob内容，版本控制内容
        del_list = ['del_blob', 'del_bbkz']
        for db_method in del_list:
            ModSql.common.execute_sql(db, db_method, {'lx':'jy', 'ssid_lst':ids_lst})
        # 登记操作日志
        ins_czrz(db, '交易[%s]已被删除' % ','.join([k['jym']+':'+(k['jymc'] or '') for k in rs_jymc]), gnmc = '交易管理_删除')
    
    result['state'] = True
    result['msg'] = '删除成功'
    return result

def jyzt_upd_service( data_dic ):
    """
    # 批量修改交易状态
    # cztype:操作类型: qy(启用):0， jy（禁用）:1
    """
    result = {'state':False, 'msg':''}
    with sjapi.connection() as db:
        # 查询交易详细信息
        jymx_lst = ModSql.kf_ywgl_024.execute_sql_dict(db, "select_byidlst", data_dic)
        if len( jymx_lst ) == 0:
            result['msg'] = '没有符合操作条件的交易信息'
            return result
        # 更新交易基本信息
        data_dic.update({'czr':get_sess_hydm(), 'czsj':get_strftime(), 
                        'zt': '1' if data_dic['cztype'] == '0' else '0', 'czmc': '启用' if data_dic['cztype'] == '0' else '禁用'})
        ModSql.kf_ywgl_024.execute_sql_dict(db, "update_jyzt", data_dic)
        # 处理计划任务
        for obj in jymx_lst:
            # 处理交易的计划任务信息
            upd_dic = { 'zdfqpz': obj['zdfqpz'],'zdfqpzsm': obj['zdfqpzsm'], 'rwlx': 'jy','ssid': obj['id'],'zt': data_dic['zt'] }
            # 调用公共函数
            update_jhrw( db, obj['zt'], obj['zdfqpz'], upd_dic = upd_dic )
        # 登记操作日志
        jym_lst = [ obj['jym'] for obj in jymx_lst ]
        nr = '批量%s[%s]的交易状态' % ( data_dic['czmc'], ','.join( jym_lst ) )
        ins_czrz( db, nr, gnmc = '交易列表' )
        # 处理缓存和唯一码
        for obj in jymx_lst:
            # 更新唯一码
            update_wym(db, 'jy', obj['id'])
            # 清除memcache
            memcache_data_del([obj['jym']])
        # 组织反馈信息
        result['state'] = True
        result['msg'] = '%s成功' % data_dic['czmc']
    return result