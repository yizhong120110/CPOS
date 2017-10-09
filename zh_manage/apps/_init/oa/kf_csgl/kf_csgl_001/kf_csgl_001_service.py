# -*- coding: utf-8 -*-
# Action: 系统参数管理B层
# Author: jind
# AddTime: 2015-01-21
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql,get_sess_hydm
from sjzhtspj.common import get_uuid,update_wym,ins_czrz,get_strftime,zz_nr

def data_service( search_name,search_value,rn_start,rn_end ):
    """
    # 获取参数管理列表展示数据
    # @param search_name:查询字段
    # @param search_value:查询字段值
    # @param rn_start:开始的rownum
    # @param rn_end:结束的rownum
    """
    # 参数状态需进行转换
    if search_name == 'zt':
        if  search_value   == '启用':
            search_value = '1'
        elif search_value   == '禁用':
            search_value = '0'
    if search_name == 'ly':
        if  search_value   == '自定义':
            search_value = '1'
        elif search_value   == '系统预置':
            search_value = '2'
    with sjapi.connection() as db:
        # 查询系统参数总条数
        sql_data = {'lx':'1', 'search_name': [search_name], 'search_value': search_value}
        #if search_value:
        #    searchFild_lst = [('a.'+search_name,search_value),]
        #    sql_data.update( {'searchFild_lst':searchFild_lst} )
        total = ModSql.common.execute_sql(db, "get_csdy_count",sql_data)[0].count
        # 查询系统参数信息
        sql_data.update( {'rn_start':rn_start,'rn_end':rn_end} )
        jbxx = ModSql.common.execute_sql_dict(db, "get_csdy",sql_data )
        return {'total':total,'rows':jbxx}
        
def data_add_service( csdm,csz,csms,cszt,lx, pt ):
    """
    # 新增系统参数
    # @param csdm:参数代码
    # @param csz:参数值
    # @param csms:参数描述
    # @param cszt:参数状态
    # @param lx:参数类型
    # @param pt:平台：kf，yw 默认kf
    """
    with sjapi.connection() as db:
        # 校验系统参数是否存在
        count = ModSql.common.execute_sql(db, "check_csdm",{'csdm':csdm,'lx':'1'})[0].count
        if count != 0:
            msg = '参数代码[%s]已经存在，请重新录入' % csdm
            return {'state':False,'msg':msg}
        # 插入参数定义表 lx(1:系统参数)
        id = get_uuid()
        sql_data = {'id':id, 'csdm':csdm, 'csms':csms, 'value':csz,'lx':lx, 'zt':cszt, 'czr':get_sess_hydm(), 'czsj':get_strftime(),'ssid':'' }
        ModSql.common.execute_sql(db, "insert_csdy",sql_data)
        # 更新唯一码
        update_wym( db,'cs',id )
        # 记录行员日常运维流水
        # 获取登记内容
        nr = zz_nr( db, sql_data, '系统参数管理-新增参数' )
        # 调用公共函数保存数据库
        ins_czrz( db, nr, pt = pt, gnmc = '系统参数管理' )
        
        return {'state':True,'msg':'新增成功'}

def data_edit_service( csid,csz,csms,cszt, pt ):
    """
    # 编辑系统参数
    # @param csid:参数ID
    # @param csz:参数值
    # @param csms:参数描述
    # @param cszt:参数状态
    """
    with sjapi.connection() as db:
        # 更新参数定义表
        sql = """
        """
        sql_data = { 'id':csid, 'csms':csms, 'value':csz,'zt':cszt, 'czr':get_sess_hydm(), 'czsj':get_strftime() }
        # 获取登记内容
        nr = zz_nr( db, sql_data, '系统参数管理-编辑参数', upd_id = csid )
        # 根据ID查询当前参数定义表中参数代码的值
        csdm_lst = ModSql.common.execute_sql_dict(db, "get_csdy_bm",sql_data)
        if csdm_lst:
            if csdm_lst[0]['csdm'] == 'YWZJ_IP':

                if len(sql_data['value']) > 15:
                    return {'state':False,'msg':'参数值长度不可超过15位'}

                # 需要计划任务中rwlx为fx的IP为修改后的value值
                ModSql.common.execute_sql(db, "update_jhrwb",sql_data)
                # 需要修改当日计划任务为0的信息的IP为修改后的value值
                ModSql.common.execute_sql(db, "update_drjhrw",sql_data)
                
        # 保存编辑信息
        ModSql.common.execute_sql(db, "update_csdy",sql_data)
        # 更新唯一码
        update_wym( db,'cs',csid )
        
        # 记录行员日常运维流水
        # 调用公共函数保存数据库
        ins_czrz( db, nr, pt = pt, gnmc = '系统参数管理' )
        
        # 组织返回值
        return {'state':True,'msg':'编辑成功'}

def data_del_service( id_lst, pt ):
    """
    # 删除系统参数
    # @param id_lst:删除的参数ID列表
    """
    with sjapi.connection() as db:
        # 获取被删除的参数编码
        rs = ModSql.common.execute_sql(db, "get_csdm",{'id_lst':id_lst})
        ## 删除系统参数
        ModSql.common.execute_sql(db, "delete_csdy",{'id_lst':id_lst})
        # 登记操作日志
        nr = '系统参数[%s]已被删除' % ( ",".join( [ obj.csdm for obj in rs ] ) )
        ins_czrz( db, nr, pt, gnmc = '系统参数管理' )
        
        return {'state':True,'msg':'删除成功'}