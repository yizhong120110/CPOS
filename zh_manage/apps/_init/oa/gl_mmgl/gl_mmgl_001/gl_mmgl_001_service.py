# -*- coding: utf-8 -*-
# Action: 菜单管理
# Author: luoss
# AddTime: 2015-06-09
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql
from sjzhtspj.common import get_sess_hydm, ins_czrz

def update_service( sql_data ):
    # 初始化返回值
    data ={'state':False,'msg':''}
    # 数据库链接
    with sjapi.connection() as db:
        # 获取当前行员代码
        sql_data['hydm'] = get_sess_hydm()
        # 查询当前登录帐号的密码
        mm = ModSql.gl_mmgl_001.execute_sql(db, "select_mm", sql_data)[0].mm
        # 判断前台传来的密码是否跟数据库密码匹配
        if sql_data['oldpass'] != mm:
            data['msg'] = '原密码不正确，请重新输入'
            return data
        if sql_data['newpass'] == mm:
            data['msg'] = '原密码和新密码相同，请重新输入'
            return data
        # 执行密码的修改
        ModSql.gl_mmgl_001.execute_sql_dict(db, "update_mm", sql_data)
        # 操作日志记录
        ins_czrz(db, '行员代码为[%s]的用户，成功进行密码修改'%(sql_data['hydm']), pt='gl', gnmc='密码管理')
        # 返回结果值
        data['state'] = True
        data['msg'] = '修改成功，请重新登录！'
        return data
