# -*- coding: utf-8 -*-
# Action: 业务管理列表
# Author: gaorj
# AddTime: 2014-12-25
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import pickle, os
from sjzhtspj.esb import memcache_data_del
from sjzhtspj import ModSql, STATIC_DIR, settings, get_sess_hydm
from sjzhtspj.common import get_uuid, get_strftime, get_strftime2, ins_czrz


def data_service(rn_start, rn_end):
    """
    # 业务管理列表json数据
    """
    data = {'total':0, 'rows':[]}
    
    with sjapi.connection() as db:
        # 查询业务总条数
        total = ModSql.kf_ywgl_001.execute_sql(db, "count_yw")[0].count
        # 查询业务列表
        sql_data = {'rn_start': rn_start, 'rn_end': rn_end}
        jbxx = ModSql.kf_ywgl_001.execute_sql_dict(db, "get_ywlb", sql_data)
        # 查询业务导入次数 (ss_idlb所属ID列表：业务导入存放的是业务ID，通讯管理导入存放的是通讯ID，通讯管理导入有可能是个列表，支持多个通讯管理导入)
        drcs = ModSql.kf_ywgl_001.execute_sql(db, "get_drcs")
        drcs_dic = dict((k.id, k.count) for k in drcs)
        # 查询业务交易数量
        jycs = ModSql.kf_ywgl_001.execute_sql(db, "get_jycs")
        jycs_dic = dict((k.id, k.count) for k in jycs)
        
        # 将导入次数和交易数量放入基本信息列表中
        for k in jbxx:
            k['drcs'] = drcs_dic.get(k['id'], 0)
            k['jysl'] = jycs_dic.get(k['id'], 0)
        
        data['total'] = total
        data['rows'] = jbxx
    
    return data

def data_add_service(params):
    """
    # 业务新增
    """
    result = {'state':False, 'msg':''}
    
    with sjapi.connection() as db:
        # 校验业务简称是否存在
        sql_data = {'ywbm': params['ywbm']}
        rs = ModSql.kf_ywgl_001.execute_sql(db, "check_ywbm", sql_data)
        if rs:
            result['msg'] = '业务简称[%s]已经存在，请重新输入' % params['ywbm']
            return result
        # 插入业务定义表
        params.update({'id':get_uuid(), 'cjr':get_sess_hydm(), 'cjsj':get_strftime()})
        ModSql.kf_ywgl_001.execute_sql(db, "insert_ywdy", params)
        # 登记操作日志
        ins_czrz(db, '业务新增：业务编码[%s]，业务名称[%s]，业务描述[%s]' % (params['ywbm'], params['ywmc'], params['ywms']), gnmc = '业务管理_新增' )
        result['state'] = True
        result['msg'] = '新增成功'
    
    return result

def data_del_service(params):
    """
    # 业务删除
    """
    result = {'state':False, 'msg':''}
    ids = params['ywids'].split(',')
    ywids_data = {'ywids': ids}
    
    with sjapi.connection() as db:
        # 查询业务下的子流程
        rs = ModSql.kf_ywgl_001.execute_sql_dict(db, "get_ywzlc", ywids_data)
        zlcid_mc_dic = {row['id']:row['mc'] for row in rs}
        
        zlcsj = {}
        zlcids = set(zlcid_mc_dic)
        while zlcids:
            # 查询子流程的上级
            sql_data = {'zlcids': list(zlcids)}
            rs = ModSql.kf_ywgl_001.execute_sql_dict(db, "get_zlcsj", sql_data) if sql_data['zlcids'] else []
            # 新找出的上级子流程
            zlcids = {row['ssid'] for row in rs if row['lx']=='zlc'} - set(sum([sj['zlc'] for sj in zlcsj.values()], []))
            for row in rs:
                sj = zlcsj.setdefault(row['jddyid'], {'jy':[], 'zlc':[]})
                sj['jy'].extend([row['ssid'] for row in rs if row['lx']=='jy'])
                sj['zlc'].extend(list(zlcids))
        
        # 业务下子流程的父（交易）所属业务
        sql_data = {'jyids': sum([sj['jy'] for sj in zlcsj.values()], [])}
        rs_ssyw_jy = ModSql.kf_ywgl_001.execute_sql_dict(db, "get_jyssyw", sql_data) if sql_data['jyids'] else []
        
        # 业务下子流程的父（子流程）所属业务
        sql_data = {'zlcids': sum([sj['zlc'] for sj in zlcsj.values()], [])}
        rs_ssyw_zlc = ModSql.kf_ywgl_001.execute_sql_dict(db, "get_zlcssyw", sql_data) if sql_data['zlcids'] else []
        
        ywids = [row['ssywid'] for row in (rs_ssyw_jy + rs_ssyw_zlc)]
        
        sql_data = {'ywids': list(set(ywids) - set(ids))}
        if sql_data['ywids']:
            rs = ModSql.kf_ywgl_001.execute_sql(db, "get_ywdy", sql_data)
            ywid_mc_dic = {row['id']:row['ywmc'] for row in rs}
            for zlcid, mc in zlcid_mc_dic.items():
                # 子流程的上级交易
                sjjy = zlcsj.get(zlcid, {}).get('jy', [])
                # 子流程的上级子流程
                sjzlc = zlcsj.get(zlcid, {}).get('zlc', [])
                # 上级交易所属业务
                ssyw_jy = [row['ssywid'] for row in rs_ssyw_jy if row['id'] in sjjy]
                # 上级子流程所属业务
                ssyw_zlc = [row['ssywid'] for row in rs_ssyw_zlc if row['id'] in sjzlc]
                ywid_yy = set(ssyw_jy + ssyw_zlc) - set(ids)
                if ywid_yy:
                    ywmcs = ', '.join([ywid_mc_dic.get(ywid) for ywid in ywid_yy])
                    result['msg'] += '子流程[%s]已被业务[%s]引用，<br>' % (mc, ywmcs)
            
            result['msg'] += '请查看对应的引用情况，解除引用关系，再进行删除'
            return result
        
        # 查询业务名称
        rs_ywdy = ModSql.kf_ywgl_001.execute_sql(db, "get_ywdy", ywids_data)
        
        # 查询业务数据表名称
        rs = ModSql.kf_ywgl_001.execute_sql(db, "get_sjbmc", ywids_data)
        rs_dic = {}
        for row in rs:
            rs_dic.setdefault((row.ywbm, row.ywmc), []).append(row)
        
        # 业务表的drop语句txt文件写入目录
        # 文件列表
        fpath_lst = []
        path = os.path.join(STATIC_DIR, settings._T.APP_NAME, 'backup_dmp')
        for bm, mc in rs_dic:
            # 写文件
            fpath = os.path.join(path, 'drop_%s_%s_%s.txt' % (get_strftime2(), bm, mc))
            fpath_lst.append(fpath)
            f = open(fpath, 'w')
            for row in rs_dic[(bm, mc)]:
                f.write('drop table %s;\n' % row.sjbmc)
            f.close()
        
        # 删除业务相关数据需要执行的SQL
        sqlid_lst = [
            'del_blob_jy', 'del_blob_txzlc', 'del_blob_zlc', 'del_blob_gghs_bbkz', 'del_blob_gghs', 'del_blob_sjk', 
            'del_blob_dymb', 'del_bbkz_jy', 'del_bbkz_txzlc', 'del_bbkz_zlc', 'del_bbkz_gghs', 'del_bbkz_sjk', 
            'del_csdy_yw', 'del_csdy_jy', 'del_csdy_jdcsalys', 'del_csdy_jdcsalzxbz_jd', 'del_csdy_jdcsalzxbz_txzlc', 
            'del_zdhcslsb', 'del_csaldy', 'del_demo_jbxx', 'del_demo_sj', 'del_lczx', 'del_lcbj', 'del_lczx_txzlc', 
            'del_lcbj_txzlc', 'del_lczx_zlc', 'del_lcbj_zlc', 'del_sjktbxxb', 'del_sjktblsb', 'del_drzxrw', 'del_jhrw', 
            'del_jydy', 'del_wdqd', 'del_dbys', 'del_dbdy', 'del_txzlc', 'del_cdtx', 'del_zlc', 'del_yw', 'del_drls', 
            'del_dymb', 'del_gghs', 'del_sjkys', 'del_sjksy', 'del_sjkzdb', 'del_sjkmx'
        ]
        for sqlid in sqlid_lst:
            ModSql.kf_ywgl_001.execute_sql(db, sqlid, ywids_data)
        # 更新本业务导入、导出流水（nrlx：yw、jy）的状态为0（无效）
        ModSql.kf_ywgl_001.execute_sql(db, 'upd_drls', ywids_data)
        
        # 登记操作日志
        ins_czrz(db, '业务[%s]已被删除' % ', '.join([k.ywmc for k in rs_ywdy]), gnmc = '业务管理_删除' )
        # 清除memcache
        memcache_data_del([k.ywbm for k in rs_ywdy])
        
        msg = '业务删除成功'
        if fpath_lst:
            msg += '\n相关业务表的drop语句已保存到如下文件中，请确定是否删除业务表：\n'
            msg += '\n'.join(fpath_lst)
        result = {'state': True, 'msg': msg}
    
    return result
