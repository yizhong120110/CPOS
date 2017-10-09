# -*- coding: utf-8 -*-
# Action: 打印配置 service
# Author: zhangchl
# AddTime: 2015-01-08
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql
from sjzhtspj.common import update_wym, get_strftime, get_uuid, ins_czrz
from sjzhtspj.const import MBLX_BJLX_DIC
import pickle
from ..kf_ywgl_017.kf_ywgl_017_service import del_memcache_data


def data_service( data_dic ):
    """
    # 打印配置信息获取
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    # 数据库操作
    with sjapi.connection() as db:
        # 查询配置信息总条数
        sql_dic = { 'ywid': data_dic['ywid'] }
        total = ModSql.kf_ywgl_018.execute_sql( db, 'data_count', sql_dic )[0].count
        # 查询配置本页显示信息
        sql_dic.update( { 'rn_start': data_dic['rn_start'], 'rn_end': data_dic['rn_end'] } )
        dypzxx = ModSql.kf_ywgl_018.execute_sql_dict( db, 'data_rs', sql_dic )
        # 组织反馈信息
        data['total'] = total
        data['rows'] = dypzxx
    
    return data

def data_add_sel_service( data_dic ):
    """
    # 打印配置新增页面参数查询
    """
    # 反馈信息
    result = {'state': False, 'msg': '', 'ywid': data_dic['ywid'], 'mblx_lst': []}
    # 数据库操作
    with sjapi.connection() as db:
        # 查询模板类型，为新增打印模板时选择模板类型提供数据
        sql_dic = { 'ywid': data_dic['ywid'] }
        result['ywmc'] = ModSql.common.execute_sql( db, 'get_ywdy', sql_dic )[0].ywmc
        # 查询模板类型
        mblx_lst = ModSql.kf_ywgl_018.execute_sql_dict( db, 'data_add_sel_mblx', {} )
        # 模板类型中的xml设置为默认值
        for mblx in mblx_lst:
            if mblx['bm'] == 'xml':
                mblx['selected'] = 'true'
        result['mblx_lst'] = mblx_lst
    # 模板类型与编辑框类型对应字典
    result['mblx_bjlx_dic'] = MBLX_BJLX_DIC
    result['state'] = True
    
    return result
    
def data_add_service( data_dic ):
    """
    # 打印配置新增 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    # 操作时间
    czsj = get_strftime()
    # 主键id
    blob_id = get_uuid()
    dyid = get_uuid()
    
    # 数据库操作
    with sjapi.connection() as db:
        # 校验模板是否已存在
        sql_dic = { 'mbmc': data_dic['mbmc'] }
        count = ModSql.kf_ywgl_018.execute_sql( db, 'data_add_check_mbmc', sql_dic )[0].count
        if count != 0:
            result['msg'] = '模板名称[%s]已存在，请重新输入！' % data_dic['mbmc']
            return result
        
        # 将模板存储到数据库表中
        nr = pickle.dumps(data_dic['nr'])
        
        # 执行sql
        # BLOB
        blob_dic = { 'blobid': blob_id, 'lx': 'gl_dymbdy',
                    'czr': data_dic['hydm'], 'czsj': czsj,
                    'nr': nr }
        ModSql.common.execute_sql( db, 'add_blob', blob_dic )
        # 打印模板
        sql_data_dymb = { 'ywid': data_dic['ywid'], 'mblx': data_dic['mblx'],
        'mbmc': data_dic['mbmc'], 'mbms': data_dic['mbms'],
        'czsj': czsj, 'hydm': data_dic['hydm'], 'blob_id':blob_id,
        'dyid':dyid }
        ModSql.kf_ywgl_018.execute_sql( db, 'data_add_insert_dymb', sql_data_dymb )
        # 操作日志流水
        ins_czrz( db, '打印模版新增：打印模版名称[%s]，打印模版描述[%s]，打印模版类型[%s]' % (sql_data_dymb['mbmc'], sql_data_dymb['mbms'], sql_data_dymb['mblx'] ), gnmc = '打印模版管理_新增' )
        # 更新模板定义表中的唯一码
        update_wym(db, 'dy', dyid)
        
        # 清除memcache
        del_memcache_data( db, ywid = data_dic['ywid'] )
        
        # 组织反馈值
        result['state'] = True
        result['msg'] = '新增成功!'
    
    return result
    
def data_edit_sel_service( data_dic ):
    """
    # 打印配置编辑前查询
    """
    # 反馈信息
    result = {'state': False, 'msg':'', 'mblx_lst':''}
    with sjapi.connection() as db:
        # 查询模板定义表中的详细数据
        dyxx = ModSql.kf_ywgl_018.execute_sql_dict( db, 'data_edit_sel_dymbdy', { 'dymbdy_id': data_dic['dymbdy_id'] } )[0]
        result['nr'] = pickle.loads(dyxx['nr'].read())
        result['blobid'] = dyxx['blobid']
        result['wym'] = dyxx['wym']
        result['dyid'] = dyxx['dyid']
        result['mbmc'] = dyxx['mbmc']
        result['mbms'] = dyxx['mbms']
        result['mblx'] = dyxx['mblx']
        result['ywmc'] = dyxx['ywmc']
        
        # 查询模板类型
        mblx_lst = ModSql.kf_ywgl_018.execute_sql_dict( db, 'data_add_sel_mblx', {} )
        # 模板类型中的xml设置为默认值
        for mblx in mblx_lst:
            if mblx['bm'] == dyxx['mblx']:
                mblx['selected'] = 'true'
        result['mblx_lst'] = mblx_lst
        
    # 模板类型与编辑框类型对应字典
    result['mblx_bjlx_dic'] = MBLX_BJLX_DIC
    result['bjlx'] = MBLX_BJLX_DIC.get( dyxx['mblx'], '' )
    result['state'] = True
    
    return result
    
def data_edit_service( data_dic ):
    """
    # 打印配置编辑 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    # 操作时间
    czsj = get_strftime()
    
    # 数据库操作
    with sjapi.connection() as db:
        
        # 查询修改前的信息
        data = ModSql.kf_ywgl_018.execute_sql(db, "select_dymbdy", data_dic)[0]

        # 更新模板定义表中的数据，不更新唯一码 
        sql_data_dymb = { 'mblx': data_dic['mblx'], 'mbms': data_dic['mbms'],
        'hydm': data_dic['hydm'], 'czsj': czsj, 'dyid': data_dic['dyid'] }
        ModSql.kf_ywgl_018.execute_sql( db, 'data_edit_dymbdy', sql_data_dymb )
        
        # 更新BLOB管理表表中的模板内容
        nr = pickle.dumps(data_dic['nr'])
        sql_data_blob = { 'czr': data_dic['hydm'], 'czsj': czsj, 
        'pkid':data_dic['blob_id'], 'nr':nr }
        ModSql.common.execute_sql( db, 'edit_blob2', sql_data_blob )

        # 登记操作日志
        nr_bjq = '编辑前：打印模版名称[%s]，打印模版描述[%s]，打印模版类型[%s]' % (data['mbmc'], data['mbms'], data['mblx'])
        nr_bjh = '编辑后：打印模版名称[%s]，打印模版描述[%s]，打印模版类型[%s]' % (data['mbmc'], data_dic['mbms'],data_dic['mblx'])
        ins_czrz( db, '打印模版编辑：%s;%s' % (nr_bjq, nr_bjh), gnmc = '打印模版管理_编辑' )
        
        # 更新模板定义表中的唯一码
        update_wym(db, 'dy', data_dic['dyid'])
        
        # 清除memcache
        del_memcache_data( db, ywid = data_dic['ywid'], uuid_lst = [ data_dic['dyid'] ] )
        
        # 组织反馈值
        result['state'] = True
        result['msg'] = '编辑成功!'
    
    return result
    
def data_del_service( data_dic ):
    """
    # 打印配置删除 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    # 数据库操作
    with sjapi.connection() as db:
        id_lst = data_dic['ids'].split(',')
        sql_data = {'id_lst':id_lst}
        # 删除BLOB管理表的内容
        sql_data_blob = { 'zdlst':['nr_id'], 'tabname': ['gl_dymbdy'], 'pkid_lst': id_lst }
        ModSql.common.execute_sql( db, 'del_blob_ssid', sql_data_blob )
        
        # 删除选中的打印配置
        ModSql.kf_ywgl_018.execute_sql( db, 'data_del_dymbdy', sql_data )
        
        # 登记操作日志
        ins_czrz( db, '打印配置中模板:[%s]已被删除' % data_dic['dymss'], gnmc = '打印模版管理_删除' )
        
        # 清除memcache
        del_memcache_data( db, ywid = data_dic['ywid'], uuid_lst = id_lst )
        
        # 组织反馈值
        result['state'] = True
        result['msg'] = '删除成功!'
    
    return result