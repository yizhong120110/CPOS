# -*- coding: utf-8 -*-
# Action: 运维参数管理-交易参数
# Author: zhangchl
# AddTime: 2015-04-07
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj.esb import memcache_data_del
from sjzhtspj import ModSql, get_sess_hydm
from sjzhtspj.common import get_strftime, update_wym, ins_czrz, crontab_fy, update_jhrw


def data_service( sql_data ):
    """
    # 交易参数管理列表json数据 service
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    
    # 数据库链接
    with sjapi.connection() as db:
        # 查询交易总条数
        total = ModSql.yw_csgl_003.execute_sql(db, "data_count", sql_data)[0].count
        # 查询交易列表
        jbxx = ModSql.yw_csgl_003.execute_sql_dict(db, "data_rs", sql_data)
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = jbxx
    
    # 将查询到的几个反馈给view
    return data

def jbxx_edit_service(sql_data):
    """
    # 交易基本信息编辑 service
    """
    # 初始化反馈结果
    result = {'state':False, 'msg':'', 'zdfqpzsm': ''}
    
    with sjapi.connection() as db:
        # 自动发起配置如果不为空，则进行翻译
        if sql_data['zdfqpz']:
            # 返回信息：(True/False, 中文翻译, message)
            ret = crontab_fy(sql_data['zdfqpz'])
            # 翻译错误，将错误信息反馈前台
            if ret[0] == False:
                result['msg'] = ret[2]
                return result
            else:
                # 翻译成功，将中文翻译放在保存字典中
                sql_data['zdfqpzsm'] = ret[1]
        # 更新交易基本信息( 操作人、操作时间 )
        sql_data.update({'czr':get_sess_hydm(), 'czsj':get_strftime()})
        # 更新数据库
        ModSql.yw_csgl_003.execute_sql_dict(db, "update_jydy", sql_data)
        # 处理交易的计划任务信息
        # upd_dic = { 'zdfqpz': zdfqpz,'zdfqpzsm': zdfqpzsm,'rwlx': rwlx,'ssid':ssid,'zt':zt }
        upd_dic = { 'zdfqpz': sql_data['zdfqpz'],'zdfqpzsm': sql_data['zdfqpzsm'], 'rwlx': 'jy','ssid': sql_data['id'],'zt': sql_data['zt'] }
        # 调用公共函数
        update_jhrw( db, sql_data['yzt'], sql_data['yzdfqpz'], upd_dic = upd_dic )
        # 更新唯一码
        update_wym(db, 'jy', sql_data['id'])
        # 清除memcache
        memcache_data_del([sql_data['jym']])
        # 记录操作日志
        # 组织内容
        nr = "参数管理-交易参数基本信息编辑：编辑前[%s]，编辑后[交易超时时间：%s，交易自动发起配置：%s，状态：%s,自动发起配置说明：%s]" % (
            sql_data['updQ'], sql_data['timeout'], sql_data['zdfqpz'], sql_data['zt'], sql_data['zdfqpzsm']
        )
        # 调用公共函数保存数据库
        ins_czrz( db, nr, pt = 'wh', gnmc = '参数管理-交易参数基本信息编辑' )
        # 更新返回值
        result['state'] = True
        result['msg'] = '修改成功'
        result['zdfqpzsm'] = sql_data['zdfqpzsm']
    
    return result