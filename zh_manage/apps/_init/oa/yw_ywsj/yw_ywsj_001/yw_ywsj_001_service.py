# -*- coding: utf-8 -*-
# Action: 导入历史 service
# Author: zhangchl
# AddTime: 2015-01-12
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql
from sjzhtspj.common import ins_czrz
import json

def data_service( sql_dic ):
    """
    # 导入历史：获取显示数据
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    # 数据库操作
    sql_dic.update( { 'nrlx': 'wh', 'czlx': 'dr'} )
    with sjapi.connection() as db:
        if sql_dic['search_value']:
            sql_dic['searchFild_lst'] = [(sql_dic['search_name'],sql_dic['search_value'])]
            sql_dic['search_name'] = [sql_dic['search_name']]
        total = ModSql.yw_ywsj_001.execute_sql( db, 'data_count', sql_dic )[0].count
        # 获取当前页面显示信息
        data_row = ModSql.yw_ywsj_001.execute_sql_dict( db, 'data_rs', sql_dic )
        
        # 判断行信息是否有回退按钮
        max_id = get_dr_maxid( db )
        if max_id:
            for dr_obj in data_row:
                if dr_obj['id'] == max_id:
                    dr_obj['sfht'] = 'TRUE'
        # 如果是交易、通讯管理，需要获取对应名称
        ss_idlb_lst = []
        # 所属类别是交易id
        ss_idlb_jy_lst = []
        # 所属类别是通讯id
        ss_idlb_tx_lst = []
        # 所属类别是业务id
        ss_idlb_yw_lst = []
        for dr_obj in data_row:
            # 初始化每一行的通讯id,交易id
            dr_obj['ss_idlb_tx_lst'] = []
            dr_obj['ss_idlb_jy_lst'] = []
            dr_obj['ss_idlb_yw_lst'] = []
            if dr_obj['nrlx'] in ['tx','jy','yw']:
                # 首先获取所属id列表
                if dr_obj['ss_idlb']:
                    idlb =  [ idlbxx for idlbxx in dr_obj['ss_idlb'].split(',') if idlbxx]
                    ss_idlb_lst.extend( idlb )
                    if dr_obj['nrlx'] == 'jy':
                        ss_idlb_jy_lst.extend( idlb )
                        dr_obj['ss_idlb_jy_lst'] = idlb
                    elif dr_obj['nrlx'] == 'tx':
                        ss_idlb_tx_lst.extend( idlb )
                        dr_obj['ss_idlb_tx_lst'] = idlb
                    elif dr_obj['nrlx'] == 'yw':
                        ss_idlb_yw_lst.extend( idlb )
                        dr_obj['ss_idlb_yw_lst'] = idlb
        # 如果存在则获取对应名称
        if ss_idlb_tx_lst:
            get_dr_tx( db, ss_idlb_tx_lst, data_row )
        if ss_idlb_jy_lst:
            get_dr_jy( db, ss_idlb_jy_lst, data_row )
        if ss_idlb_yw_lst:
            get_dr_yw( db, ss_idlb_yw_lst, data_row )
        # 组织反馈值
        data['total'] = total
        data['rows'] = data_row
    
    return data

def get_dr_tx( db, ss_idlb_lst, data_row ):
    """
    # 导入流水涉及到的通讯名称
    # @params: ss_idlb_lst: 所属id列表
    # @params: data_row:查询导入历史结果集
    """
    # 本次涉及到的所属id名称
    data_dic = { 'ids': ss_idlb_lst }
    rs_txxx = ModSql.common.execute_sql_dict( db, 'get_txgl_mc', data_dic )
    txxx_dic = dict( ( obj['id'], obj['mc'] ) for obj in rs_txxx )
    
    for dr_obj in data_row:
        if dr_obj['nrlx'] == 'tx':
            ss_idlb_mc = [ txxx_dic.get( idlb, '' ) for idlb in dr_obj['ss_idlb_tx_lst'] ]
            dr_obj['jy_txmc'] = ','.join( idlb_mc for idlb_mc in ss_idlb_mc if idlb_mc )
def get_dr_yw( db, ss_idlb_lst, data_row ):
    """
    # 导入流水涉及到的业务名称
    # @params: ss_idlb_lst: 所属id列表
    # @params: data_row:查询导入历史结果集
    """
    # 本次涉及到的所属id名称
    data_dic = { 'ids': ss_idlb_lst }
    rs_txxx = ModSql.yw_ywsj_001.execute_sql_dict( db, 'get_ywgl_mc', data_dic )
    txxx_dic = dict( ( obj['id'], obj['mc'] ) for obj in rs_txxx )
    for dr_obj in data_row:
        if dr_obj['nrlx'] == 'yw':
            ss_idlb_mc = [ txxx_dic.get( idlb, '' ) for idlb in dr_obj['ss_idlb_yw_lst'] ]
            dr_obj['jy_txmc'] = ','.join( idlb_mc for idlb_mc in ss_idlb_mc if idlb_mc )
def get_dr_jy( db, ss_idlb_lst, data_row ):
    """
    # 导入流水涉及到的交易名称
    # @params: ss_idlb_lst: 所属id列表
    # @params: data_row:查询导入历史结果集
    """
    # 本次涉及到的所属id名称
    data_dic = { 'ids': ss_idlb_lst }
    rs_txxx = ModSql.common.execute_sql_dict( db, 'get_jydy_mc', data_dic )
    txxx_dic = dict( ( obj['id'], obj['jymc'] ) for obj in rs_txxx )
    
    for dr_obj in data_row:
        if dr_obj['nrlx'] == 'jy':
            ss_idlb_mc = [ txxx_dic.get( idlb, '' ) for idlb in dr_obj['ss_idlb_jy_lst'] ]
            dr_obj['jy_txmc'] = ','.join( idlb_mc for idlb_mc in ss_idlb_mc if idlb_mc )

def get_dr_maxid( db ):
    """
    # 获取导入流水最大值id
    """
    max_id = ''
    max_rs = ModSql.yw_ywsj_001.execute_sql_dict( db, 'get_dr_maxid' )
    if max_rs:
        max_id = max_rs[0]['id']
    
    return max_id

def data_edit_sel_service( data_dic ):
    """
    # 导入历史：信息编辑 页面初始化 service
    """
    result = {'state': False, 'msg':'', 'drid':'', 'czms': '', 'bz': ''}
    with sjapi.connection() as db:
        drxx = ModSql.yw_ywsj_001.execute_sql_dict( db, 'get_drxx', data_dic )
        if drxx:
            result['state'] = True
            result['drlsid'] = drxx[0]['id']
            result['czms'] = drxx[0]['czms']
            result['bz'] = drxx[0]['bz']
        else:
            result['msg'] = '获取编辑信息失败，编辑信息不存在'
    
    return result
    
def data_edit_service( data_dic ):
    """
    # 导入历史：信息编辑 提交 service
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    with sjapi.connection() as db:
        drxx = ModSql.yw_ywsj_001.execute_sql_dict( db, 'get_drxx', data_dic )[0]
        ModSql.yw_ywsj_001.execute_sql_dict( db, 'upd_drxx', data_dic )

        # 登记操作日志
        nr_bjq = '编辑前：%s' % drxx
        drxx['czms'] = data_dic['czms']
        drxx['bz'] = data_dic['bz']
        nr_bjh = '编辑后：%s' % drxx
        ins_czrz( db, '【业务升级配置】导入历史信息_编辑：%s;%s' % (nr_bjq, nr_bjh), gnmc = '【业务升级配置】导入历史信息_编辑' )

        # 反馈信息
        result['state'] = True
        result['msg'] = '修改成功'
    
    return result
    
def get_yw_tx_service( data_dic ):
    """
    # 获取通讯或者业务的列表
    """
    # 查询
    rs_txxx = []
    with sjapi.connection() as db:
        if data_dic['lx'] == 'tx':
            rs_txxx = ModSql.yw_ywsj_001.execute_sql_dict( db, 'get_tx', {} )
            if data_dic['dr'] == 'dr':
                rs_txxx.insert(0,{'id':'-1', 'mc':'导入新通讯'})
        elif data_dic['lx'] == 'yw':
            rs_txxx = ModSql.yw_ywsj_001.execute_sql_dict( db, 'get_yw', {} )
        return json.dumps(rs_txxx)    
        
        