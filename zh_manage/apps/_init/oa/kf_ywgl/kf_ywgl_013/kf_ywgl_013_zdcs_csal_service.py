# -*- coding: utf-8 -*-
# Action: 自动化测试 测试案例流程列表 service
# Author: 周林基
# AddTime: 2015-2-10
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行
# Explain: 由于本功能特殊，所以允许将sql下载此py中

from sjzhtspj import ModSql 
from sjzhtspj.common import db_hex_to_binary

def data_service( data_dic ):
    """
    # 自动化测试：交易自动化测列表
    # @param data_dic:字典参数
    """
    dg_data = {'total':0, 'rows':[]}

    # 数据库操作
    with sjapi.connection() as db:
        if data_dic['gl'] == 'True' or data_dic['gl'] == True:
            jddyid = data_dic['jddyid']
            # 节点定义id分割
            if jddyid == '' or jddyid == None:
                return dg_data
            jddyid = jddyid.split(',')
            # 查询此节点的关联交易及子流程
            jyzlc = ModSql.kf_ywgl_013.execute_sql_dict(db, "get_jy_zlc", {'jddyid':jddyid})
            # 查询节点的类型为8,9，也就是8:流程打包节点 9:流程解包节点，对应的测试案例ID和节点测试案例ID
            csalid_lst = ModSql.kf_ywgl_013.execute_sql_dict(db, "get_csalid_for_dj", {'jddyid':jddyid})
            csals = []
            for id in csalid_lst:
                csals.append(id['csaldyid'])
                csals.append(id['jdcsaldyid'])
            # 关联交易ID列表
            jyidlst = [jz['ssjyid'] for jz in jyzlc]
            # 关联子流程ID列表
            zlcidlst = [jz['sszlcid'] for jz in jyzlc]
            # 查询关联交易、子流程及本节点的测试案例
            ids = []
            ids.extend(jyidlst)
            ids.extend(zlcidlst)
            ids.extend(jddyid)
            csal = ModSql.kf_ywgl_013.execute_sql_dict(db, "get_jy_zlc_csal", {'ids':ids,'csalids':csals,'rn_start': data_dic['rn_start'],'rn_end': data_dic['rn_end']})
            csal_count = ModSql.kf_ywgl_013.execute_sql_dict(db, "get_jy_zlc_csal_count", {'ids':ids,'csalids':csals})[0]['count']
            dg_data['rows'] = csal
            dg_data['total'] = csal_count
            return dg_data
        else:
            data_dic_param = { 'csaldyssid': data_dic['csaldyssid'], 'rn_start': data_dic['rn_start'], 'rn_end': data_dic['rn_end']}
            # 获取交易自动化测试信息
            if data_dic['lx'] == 'jd':
                data_dic_param['lblst'] = ['3']
                data_dic_param['sslb'] = '3'
            elif data_dic['lx'] == 'zlc':
                data_dic_param['lblst'] = ['2','4']
                data_dic_param['sslb'] = '2'
            else:
                data_dic_param['lblst'] = ['1']
                data_dic_param['sslb'] = '1'
            data_jy_dic = ModSql.kf_ywgl_013.execute_sql_dict( db, 'index_zdcs_csal_lst', data_dic_param )
            data_jy_di_count = ModSql.kf_ywgl_013.execute_sql_dict( db, 'index_zdcs_csal_lst_count', data_dic_param )[0]['count']

            for row in data_jy_dic:
                row['lx'] = data_dic['lxmc']
                row['dxmc'] = data_dic['dxmc']
                row['lxdm'] = data_dic['lx']

            dg_data['total'] = data_jy_di_count
            dg_data['rows'] = data_jy_dic
            return dg_data
        
def csalxx_service(jdcsalid,pc):
    """
    # 获取流程-测试案例定义节点输入输出要素
    """
    with sjapi.connection() as db:
        zxbz = ModSql.kf_ywgl_013.execute_sql_dict(db, "get_csalbz", {'id':jdcsalid})
        bzids = [zb['jdcsalzxbzlb'] for zb in zxbz]
        map = {'zxbzid':bzids,'jdcsalid':jdcsalid,'pc':pc}
        # 根据节点测试案例执行步骤ID查询出输出要素的信息
        map['lx'] = '2'
        scys = ModSql.kf_ywgl_013.execute_sql_dict(db, "get_csal_jdxx_yslb", map)
        if scys:
            db_hex_to_binary(scys)
        # 根据节点测试案例执行步骤ID查询出输入要素的信息
        map['lx'] = '1'
        srys = ModSql.kf_ywgl_013.execute_sql_dict(db, "get_csal_jdxx_yslb", map)
        if srys:
            db_hex_to_binary(srys)
        return {'srys':srys, 'scys':scys, 'demoid':""}
        
def zxjgms_service(jdcsalid,pc):
    """
    # 获取节点执行结果已经说明
    """
    with sjapi.connection() as db:
        # 查询执行结果和结果说明
        zxjgsm = ModSql.kf_ywgl_013.execute_sql_dict(db, "get_zxjg", {'id':jdcsalid, 'pc':pc})[0]
        return {'zxjg':zxjgsm['zxjg'] ,'jgsm':zxjgsm['jgsm']}
