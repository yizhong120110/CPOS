# -*- coding: utf-8 -*-
# Action: 自动化测试 service
# Author: 周林基
# AddTime: 2015-2-10
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行
# Explain: 由于本功能特殊，所以允许将sql下载此py中

from sjzhtspj import ModSql

def data_service( data_dic ):
    """
    # 自动化测试：选择需测试的交易或节点树形结构
    # @param data_dic:字典参数
    """
    dg_data = {'total':0, 'rows':[]}
    tree_data = [
        { "id": 1, "text": "交易自动化测试",  "children": [] },
        { "id": 3, "text": "子流程自动化测试",  "children": [] },
        { "id": 2, "text": "节点自动化测试", "children": [] }
    ]
    # 数据库操作
    with sjapi.connection() as db:
        # 获取交易自动化测试信息
        data_jy_dic = ModSql.kf_ywgl_013.execute_sql_dict( db, 'index_zdcs_jy_lst', data_dic )
        # 判断是否存在此信息
        if data_jy_dic:
            tree_data[0]['children'] = data_jy_dic

        # 获取子流程自动化测试信息
        data_zlc_dic = ModSql.kf_ywgl_013.execute_sql_dict( db, 'index_zdcs_zlc_lst', data_dic )
        # 判断是否存在此信息
        if data_zlc_dic:
            for row in data_zlc_dic:
                chk_dic = {'id': row.get('id'), 'ssywid': data_dic.get('ssywid')}

                # 取得补充关联测试用到的所属交易
                zlc_ssjy_dic = ModSql.kf_ywgl_013.execute_sql_dict( db, 'index_zdcs_zlc_ssjy_lst', chk_dic )
                # 取得补充关联测试用到的所属子流程
                zlc_sszlc_dic = ModSql.kf_ywgl_013.execute_sql_dict( db, 'index_zdcs_zlc_zlc_lst', chk_dic )

                zlc_ssiy = [dic['ssjyid'] for dic in zlc_ssjy_dic]
                row['jd'] = ""
                for row_dic in zlc_ssiy:
                    row['jd'] = row['jd'] + row_dic + ","

                zlc_sszlc = [dic['sszlcid'] for dic in zlc_sszlc_dic]
                for row_dic in zlc_sszlc:
                    row['jd'] = row['jd'] + row_dic + ","

            tree_data[1]['children'] = data_zlc_dic;

        # 获取节点自动化测试信息
        data_jd_dic1 = ModSql.kf_ywgl_013.execute_sql_dict( db, 'index_zdcs_jd_jddy_lst_one', data_dic )
        data_jd_dic2 = ModSql.kf_ywgl_013.execute_sql_dict( db, 'index_zdcs_jd_jddy_lst_two', data_dic )
        jddyid = []
        # 判断是否存在此信息
        if data_jd_dic1 and data_jd_dic2:
            # 去除重复
            data_jd_dic1.extend(data_jd_dic2)
            jddyid_temp = []
            for row in data_jd_dic1:
                if row['jddyid'] not in jddyid_temp:
                    jddyid_temp.append(row['jddyid'])
                else:
                    data_jd_dic1.remove(row)
            jddyid = data_jd_dic1
        elif data_jd_dic1:
            jddyid = data_jd_dic1
        elif data_jd_dic2:
            jddyid = data_jd_dic2
        # 查询打解包节点
        rs_djbjd = ModSql.kf_ywgl_013.execute_sql_dict(db, 'get_djbjd', {'ywid': data_dic['ssywid']})
        for row in rs_djbjd:
            if row['dbjdid']:
                jddyid.append({'jddyid': row['dbjdid']})
            if row['jbjdid']:
                jddyid.append({'jddyid': row['jbjdid']})
        if jddyid:
            data_jd_dic = ModSql.kf_ywgl_013.execute_sql_dict( db, 'index_zdcs_jd_lst', {'jddyid':[jddy['jddyid'] for jddy in jddyid]} )
            # 判断是否存在此信息
            if data_jd_dic:
                for row in data_jd_dic:
                    chk_dic = {'id': row.get('id')}
                    # 取得补充关联测试用到的所属交易
                    jd_ssjy_dic = ModSql.kf_ywgl_013.execute_sql_dict( db, 'index_zdcs_jd_ssjy_lst', chk_dic )
                    # 取得补充关联测试用到的所属子流程
                    jd_sszlc_dic = ModSql.kf_ywgl_013.execute_sql_dict( db, 'index_zdcs_jd_zlc_lst', chk_dic )
                    
                    # 若改节点是打解包节点的话就需要单独查询关联的测试案例
                    csal_lst = ModSql.kf_ywgl_013.execute_sql_dict( db, 'get_csalssid_jdcsalid', chk_dic )
                    csalid_lst = []
                    for csal in csal_lst:
                        csalid_lst.append(csal['csaldyid'])
                        csalid_lst.append(csal['jdcsaldyid'])
                    csal_ssid = ModSql.kf_ywgl_013.execute_sql_dict( db, 'get_csalssid', {'csalid_lst':csalid_lst} )
                    # 节点关联的交易的id
                    jd_ssiy = [dic['ssjyid'] for dic in jd_ssjy_dic]
                    # 节点管理的子流程的id
                    jd_sszlc = [dic['sszlcid'] for dic in jd_sszlc_dic]
                    # 将查询的打解包对应的id分别放到jd_ssiy和jd_sszlc中
                    for ssid in csal_ssid:
                        # 交易测试案例
                        if ssid['lb'] == '1':
                            jd_ssiy.append(ssid['ssid'])
                        # 子流程,通讯子流程测试案例
                        elif ssid['lb'] == '2' or ssid['lb'] == '4':
                            jd_sszlc.append(ssid['ssid'])
                    row['jd'] = ""
                    for row_dic in jd_ssiy:
                        row['jd'] = row['jd'] + row_dic + ","

                    for row_dic in jd_sszlc:
                        row['jd'] = row['jd'] + row_dic + ","

                tree_data[2]['children'] = data_jd_dic;

    dg_data['total'] = len(tree_data[0]['children']) + len(tree_data[1]['children']) + len(tree_data[2]['children'])
    dg_data['rows'] = tree_data[0]['children'] + tree_data[1]['children'] + tree_data[2]['children']

    return [tree_data, dg_data]