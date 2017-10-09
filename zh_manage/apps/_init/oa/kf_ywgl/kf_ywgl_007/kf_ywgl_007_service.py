# -*- coding: utf-8 -*-
# Action: 子流程列表B层
# Author: jind
# AddTime: 2015-01-06
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql,get_sess_hydm
from sjzhtspj.common import get_uuid,update_wym,ins_czrz,get_strftime

def index_service( ywid ):
    """
    # 获取业务名称
    # @param ywid:业务ID
    """
    with sjapi.connection() as db:
        # 查询业务总条数
        ywmc = ModSql.common.execute_sql(db, "get_ywdy",{'ywid':ywid})[0].ywmc
        return ywmc

def data_service( ywid,rn_start,rn_end):
    """
    # 获取子流程列表展示数据
    # @param ywid:业务ID
    # @param rn_start:开始的rownum
    # @param rn_end:结束的rownum
    """
    with sjapi.connection() as db:
        # 查询子流程总条数
        total = ModSql.kf_ywgl_007.execute_sql(db, "get_zlc_count",{'ywid':ywid})[0].count
        # 查询子流程信息
        jbxx = ModSql.kf_ywgl_007.execute_sql_dict(db, "get_zlcxx",{'ywid':ywid,'rn_start':rn_start,'rn_end':rn_end})
        return {'total':total,'rows':jbxx}
        
def data_add_service( ssyw,zlcmc,zlcbm,zlcms,lb ):
    """
    # 新增子流程
    # @param ssyw:所属业务ID
    # @param zlcmc:子流程名称
    # @param zlcbm:子流程编码
    # @param zlcms:子流程描述
    # @param lb:类别
    """
    with sjapi.connection() as db:
        # 校验子流程编码是否存在
        count = ModSql.kf_ywgl_007.execute_sql(db, "check_zlcbm",{'zlcbm':zlcbm})[0].count
        if count != 0:
            msg = '子流程编码[%s]已经存在，请重新输入' % zlcbm
            return {'state':False,'msg':msg}
        # 插入子流程定义表 类别2：普通子流程 
        zlcid = get_uuid()
        sql_data = {'id':zlcid, 'lb':lb, 'zlcbm':zlcbm, 'zlcmc':zlcmc, 'zlcms':zlcms, 'ssyw':ssyw, 'czr':get_sess_hydm(), 'czsj':get_strftime()}
        ModSql.kf_ywgl_007.execute_sql(db, "insert_zlcdy",sql_data)
        
        # 登记流程布局 - 开始节点 
        sql_data={'id':get_uuid(),'jdlx':'3','zlcid':zlcid,'x':50,'y':50}
        ModSql.kf_ywgl_007.execute_sql(db, "insert_lcbj",sql_data)
        
        # 登记流程布局 - 结束节点
        sql_data={'id':get_uuid(),'jdlx':'4','zlcid':zlcid,'x':300,'y':300}
        ModSql.kf_ywgl_007.execute_sql(db, "insert_lcbj",sql_data)
        
        # 调用公共函数保存数据库
        ins_czrz( db, '子流程编码[%s]，子流程名称[%s]，子流程类别[%s]，子流程描述[%s]' % (zlcbm, zlcmc, lb, zlcms), gnmc = '子流程管理_新增' )

        # 更新唯一码
        update_wym(db, 'zlc', zlcid)
        return {'state':True,'msg':'新增成功'}

def data_del_service( zlcids_lst ):
    """
    # 删除子流程
    # @param zlcids_lst:子流程ID列表
    """
    with sjapi.connection() as db:
        # 查询要删除的子流程是否已被使用
        rs_bm = ModSql.kf_ywgl_007.execute_sql(db,'get_bsyzlc',{'zlcids_lst':zlcids_lst})
        if rs_bm:
            msg = '子流程[%s]已被引用,请先查看引用情况,解除引用关系,再进行删除' % ( ",".join( [ obj.bm for obj in rs_bm] ) )
            return {'state':False,'msg':msg}
        # 获取要删除的子流程编码
        bm_lst = ModSql.kf_ywgl_007.execute_sql(db,'get_zlcbm',{'zlcids_lst':zlcids_lst})
        # 查询测试案例表，获取子流程所有的测试案例执行步骤
        rs = ModSql.kf_ywgl_007.execute_sql(db,'get_csalzxbz',{'zlcids_lst':zlcids_lst})
        # 节点测试案例执行步骤ID列表
        jdcsalzxbz_id_lst = []
        for obj in rs:
            jdcsalzxbzlb_lst = obj.jdcsalzxbzlb.split(",")
            jdcsalzxbz_id_lst.extend( jdcsalzxbzlb_lst )
        # 删除自动化测试临时表
        ModSql.kf_ywgl_007.execute_sql(db,'del_zdhcslsb',{'zlcids_lst':zlcids_lst})
        if jdcsalzxbz_id_lst:
            # 删除节点测试案例要素
            ModSql.kf_ywgl_007.execute_sql(db,'del_jdcsalys',{'jdcsalzxbz_id_lst':jdcsalzxbz_id_lst})
            # 删除节点测试案例执行步骤
            ModSql.kf_ywgl_007.execute_sql(db,'del_jdcsalzxbz',{'jdcsalzxbz_id_lst':jdcsalzxbz_id_lst})
        # 删除测试案例
        ModSql.kf_ywgl_007.execute_sql(db,'del_csal',{'zlcids_lst':zlcids_lst})
        # 删除流程布局
        ModSql.kf_ywgl_007.execute_sql(db,'del_lcbj',{'zlcids_lst':zlcids_lst})
        # 删除流程走向
        ModSql.kf_ywgl_007.execute_sql(db,'del_lczx',{'zlcids_lst':zlcids_lst})
        # 删除子流程定义
        ModSql.kf_ywgl_007.execute_sql(db,'del_zlcdy',{'zlcids_lst':zlcids_lst})
        # 删除BLOB管理表
        ModSql.common.execute_sql(db,'del_blob',{'ssid_lst':zlcids_lst,'lx':'zlc'})
        # 删除版本控制
        ModSql.common.execute_sql(db,'del_bbkz',{'ssid_lst':zlcids_lst,'lx':'zlc'})
        # 登记操作日志
        ins_czrz( db,'子流程[%s]已被删除' % (",".join( [obj.bm for obj in bm_lst] ) ), gnmc = '子流程管理_删除' )
        return {'state':True,'msg':'删除成功'}
