# -*- coding: utf-8 -*-
# Action: 自动化测试 子流程测试案例 查看 service
# Author: 周林基
# AddTime: 2015-2-11
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行
# Explain: 由于本功能特殊，所以允许将sql下载此py中

import traceback
from sjzhtspj import ModSql, logger
from sjzhtspj.common import ins_czrz

def index_service( data_dic ):
    """
    # 自动化测试：子流程测试案例 查看
    # @param data_dic:字典参数
    """
    with sjapi.connection() as db:
        #根据测试案例定义的ID获取测试案例定义名称、描述
        param_dic = {'csaldyid': data_dic['csaldyid'], 'lblst': data_dic['lb'], 'sslb': data_dic['sslb']}
        if data_dic['lx'] == '2' or data_dic['lx'] == '4':
            csaldy_dic = ModSql.kf_ywgl_013.execute_sql_dict(db, "index_zdcs_zlc_csal_detail", param_dic)
        elif data_dic['lx'] == '3':
            csaldy_dic = ModSql.kf_ywgl_013.execute_sql_dict(db, "index_zdcs_jd_csal_detail", param_dic)
        else:
            csaldy_dic = ModSql.kf_ywgl_013.execute_sql_dict(db, "index_zdcs_csal_detail", param_dic)
        if csaldy_dic:
            if csaldy_dic[0]['jymc'] == None:
                csaldy_dic[0]['jymc'] = ''
            if csaldy_dic[0]['ms'] == None:
                csaldy_dic[0]['ms'] = ''
            if csaldy_dic[0]['mc'] == None:
                csaldy_dic[0]['mc'] = ''
        if csaldy_dic:
            return {'rows': csaldy_dic, 'csaldyid': data_dic['csaldyid'], 'lx': data_dic['lx']}
        else:
            return {'rows': [{'mc': "", 'ms': ""}], 'csaldyid': data_dic['csaldyid'], 'lx': data_dic['lx']}

def data_del_csaldy_service( csaldyid ):
    """
    # 删除测试案例定义表数据
    # @param csaldyid:测试案例定义数据表ID
    """
    result = {'state':False, 'msg':""}
    try:
        with sjapi.connection() as db:
            # 获取测试案例定义的类型
            lx = ModSql.kf_ywgl_013.execute_sql_dict( db, 'get_csal_lx', {'csalid': csaldyid})[0]['lb']
            # 获取测试案例执行步骤列表
            csbz_list = ModSql.kf_ywgl_013.execute_sql_dict( db, 'get_csbz_list', {'id': csaldyid})[0]['jdcsalzxbzlb'].split(',')
            if lx == '3' or lx == 3:
                # 步骤id
                bzid = ''
                # 如果测试案例类型是节点，则判断测试案例执行步骤表对应的测试案例定义id是否有值
                csaldy = ModSql.kf_ywgl_013.execute_sql_dict( db, 'get_csbz', {'id': csbz_list[0]})
                if len(csaldy) > 0 and (csaldy[0]['csaldyid'] == '' or csaldy[0]['csaldyid'] == None):
                    bzid = csaldy[0]['id']
                    # 查询测试案例执行步骤有没有被其他测试案例使用【交易，子流程，节点】
                    cs_count = ModSql.kf_ywgl_013.execute_sql( db, 'get_zxbz_use', {'id': bzid})[0].count
                    # 如果没有被引用的话   当查询结果为1时，说明就改步骤自己了，没有用这个步骤的了，此时可以删除
                    if cs_count <= 1:
                        # 删除步骤和要素
                        ModSql.kf_ywgl_013.execute_sql( db, 'del_csys', {'id': bzid})
                        # 没有引用的就直接删除测试案例步骤
                        ModSql.kf_ywgl_013.execute_sql( db, 'del_csbz', {'id': bzid})
                elif len(csaldy) > 0:
                    bzid = csaldy[0]['id']
                    # 如果有引用的，那么将测试案例定义id清空
                    ModSql.kf_ywgl_013.execute_sql( db, 'update_jdcsalid', {'id': bzid, 'csaldyid': csaldyid})
            else:
                # 循环节点测试案例执行步骤列表
                for bzid in csbz_list:
                    # 如果测试案例是交易，子流程，则判断测试案例执行步骤表对应的节点测试案例定义id是否有值
                    jdcsaldyid = ModSql.kf_ywgl_013.execute_sql_dict( db, 'get_csalbz_csaldyid', {'bzid': bzid})
                    if len(jdcsaldyid) > 0 and (jdcsaldyid[0]['jdcsaldyid'] == None or jdcsaldyid[0]['jdcsaldyid'] == ''):
                        # 查询测试案例执行步骤有没有被其他测试案例使用【交易，子流程，节点】
                        cs_count = ModSql.kf_ywgl_013.execute_sql( db, 'get_zxbz_use', {'id': bzid})[0].count
                        # 如果没有被引用的话
                        if cs_count <= 1:
                            # 删除步骤和要素
                            ModSql.kf_ywgl_013.execute_sql( db, 'del_csys', {'id': bzid})
                            # 没有引用的就直接删除测试案例步骤
                            ModSql.kf_ywgl_013.execute_sql( db, 'del_csbz', {'id': bzid})
                        # 检索 GL_CDTX的字段 DBSSID，判断是否有值在 1测试案例执行步骤ID中，若有则清空
                        ModSql.kf_ywgl_013.execute_sql( db, 'clear_bdssid', {'bzid': bzid})
                    else:
                        # 如果有引用的，那么将节点测试案例定义id清空
                        ModSql.kf_ywgl_013.execute_sql( db, 'update_csalid', {'id': bzid})
            # 删除数据库索引表
            ModSql.kf_ywgl_013.execute_sql( db, 'del_csaldy_by_id', {'id': csaldyid})
            # 登记操作日志
            ins_czrz( db,'数据表[测试案例定义]删除ID为[%s]的信息' % ( csaldyid ), gnmc = '数据表_测试案例删除'  )
            result['state'] = True
            result['msg'] = '删除成功'
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        ret_err_msg = error_msg[error_msg.find('cx_Oracle'):]
        result['msg'] = '删除失败！异常错误提示信息[%s]' % ret_err_msg

    return result