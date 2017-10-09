# -*- coding: utf-8 -*-
# Action: 角色管理
# Author: houpp
# AddTime: 2015-05-12
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql
from sjzhtspj.common import get_uuid, get_sess_hydm, get_strftime, get_strftime2, ins_czrz

def jsgl_service():
    # 初始化返回值
    data = {'jsfl_lst': []}
    # 追加请选择选项
    data['jsfl_lst'].insert(0, {'bm': '-1', 'mc': '请选择'})
    # 数据库链接
    with sjapi.connection() as db:
        # 执行角色分类查询
        jsfl_listt = ModSql.gl_jsgl_001.execute_sql_dict(db, "data_jsfl_rs")
        # 将角色分类结果集中放置到集合中
        data['jsfl_lst'].extend(jsfl_listt)
        return data

def data_service(sql_data):
    # 初始化返回值
    data = {'total': 0, 'rows': []}
    # 清理为空的查询条件
    search_lst = ['jsmc', 'jsfl']
    for k in list(sql_data.keys()):
        if k in search_lst and sql_data[k] == '':
            del sql_data[k]
    # 数据库链接
    with sjapi.connection() as db:
        
        # 查询角色列表信息条数
        data['total'] = ModSql.gl_jsgl_001.execute_sql(db, "data_count", sql_data)[0].count 
        # 查询角色列表信息
        data['rows'] = ModSql.gl_jsgl_001.execute_sql_dict(db, "data_rs", sql_data)

        # 将查询到的结果反馈给view
        return data

def data_add_service(params):
    """
    #角色新增
    :param params:
    :return:
    """
    result = {'state':False, 'msg':''}

    with sjapi.connection() as db:
        # 校验角色代码是否存在
        sql_data = {'jsdm': params['jsdm']}
        rs = ModSql.gl_jsgl_001.execute_sql(db, "check_jsdm", sql_data)
        if rs:
            result['msg'] = '角色代码[%s]已经存在，请重新输入' % params['jsdm']
            return result

        # 校验角色名称是否存在
        sql_data = {'jsmc': params['jsmc']}
        rs = ModSql.gl_jsgl_001.execute_sql(db, "check_jsmc", sql_data)
        if rs:
            result['msg'] = '角色名称[%s]已经存在，请重新输入' % params['jsmc']
            return result

        # 插入角色信息表
        params.update({'id':get_uuid(), 'czr':get_sess_hydm(), 'czsj':get_strftime()})
        ModSql.gl_jsgl_001.execute_sql(db, "insert_jsxx", params)

        #登记操作日志
        rznr = '角色管理-角色新增：角色名称[%s]，角色代码: [%s]' % (params['jsmc'], params['jsdm'])
        ins_czrz(db,rznr,'gl','角色管理-角色新增')
        result['state'] = True
        result['msg'] = '新增成功'
    return result

def data_edit_service(params):
    """
    #更新角色信息
    :param params:
    :return:
    """
    result = {'state':False, 'msg':''}

    with sjapi.connection() as db:
        # 获取编辑前数据
        sql_data = {'id':params['id']}
        old_data = ModSql.gl_jsgl_001.execute_sql(db, "get_jsxx_edit", sql_data)

        # 校验角色名称是否存在
        sql_data = {'jsmc': params['jsmc'],'id':params['id']}
        rs = ModSql.gl_jsgl_001.execute_sql(db, "check_jsmc", sql_data)
        if rs:
            result['msg'] = '角色名称[%s]已经存在，请重新输入' % params['jsmc']
            return result
        # 更新角色信息表
        params.update({'czr':get_sess_hydm(), 'czsj':get_strftime()})
        ModSql.gl_jsgl_001.execute_sql(db, "update_jsxx", params)

        # 记录行员日常运维流水
        # 获取登记内容
        rznr = '角色管理-角色编辑：编辑前角色信息[%s],编辑后角色信息[%s]' % (str(old_data), params)
        # 调用公共函数保存数据库
        ins_czrz(db,rznr,'gl','角色管理-角色编辑')
        result['state'] = True
        result['msg'] = '编辑成功'

    return result

def delete_service(sql_data):
    """
    #删除角色
    :return:
    """
    # 初始化返回值
    result = {'state':False, 'msg':""}
    #业务配置ID列表
    ids = sql_data['ids'].split(',')
    sql_para = { 'ids':ids}
    # 数据库链接
    with sjapi.connection() as db:
        #查询角色信息
        rs  = ModSql.gl_jsgl_001.execute_sql_dict(db,"select_js_rz",sql_para)
        #拼操作日志中的字符串: 角色名称（角色代码）
        rz = ', '.join(['%s(%s)' % (k['jsmc'], k['jsdm']) for k in rs])

        #删除角色权限表
        ModSql.gl_jsgl_001.execute_sql_dict(db,"delete_jsqxpz",sql_para)
        #删除用户角色配置表
        ModSql.gl_jsgl_001.execute_sql_dict(db,"delete_yhjspz",sql_para)
        # 删除角色信息表
        sql_para.update({'czr':get_sess_hydm(), 'czsj':get_strftime()})
        ModSql.gl_jsgl_001.execute_sql_dict(db,"delete_pl",sql_para)

        #登记操作日志
        rznr = '角色管理-删除：待删除角色信息：【'+ rz +'】'
        ins_czrz(db,rznr,'gl','角色管理-删除')

        #成功后返回成功信息
        result['msg'] = '删除记录成功'
        result['state'] = True
    # 将查询到的结果反馈给view
    return result

def get_jsxx_service(id):
    """
    # 获取角色信息
    :param id:
    :return:
    """
     # 数据结构
    data = {'state':True, 'msg':'','gnxx':{}}
    # 数据库链接
    with sjapi.connection() as db:
        # 获取对象属性
        data['jsxx'] = ModSql.gl_jsgl_001.execute_sql_dict(db, "get_jsxx_edit", {'id':id})[0]
    return data





