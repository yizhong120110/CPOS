# -*- coding: utf-8 -*-
# Action: 计划任务管理-自动发起交易列表
# Author: zhangchl
# AddTime: 2015-04-09
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行


from sjzhtspj import ModSql
from sjzhtspj.common import get_bmwh_bm, get_sess_hydm, get_strftime, update_wym, ins_czrz , update_jhrw, crontab_fy
from sjzhtspj.esb import memcache_data_del


def zdfqjylb_service( sql_data ):
    """
    # 初始化自动发起交易列表页面数据准备 service
    """
    # 初始化反馈值
    data = { 'zt_lst': [] }
    # 查询状态列表
    zt_lst = get_bmwh_bm( '10001' )
    # 追加请选择选项
    zt_lst.insert( 0, {'value': '', 'ms': '', 'text': '请选择'} )
    # 将结果放到返回值中
    data['zt_lst'] = zt_lst
    # 将结果反馈给view
    return data

def zdfqjylb_data_service( sql_data ):
    """
    # 自动发起交易列表json数据 service
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    # 清理为空的查询条件
    search_lst = [ 'ywmc', 'jym', 'jymc', 'jyzt' ]
    for k in list(sql_data.keys()):
        if k in search_lst and sql_data[k] == '':
            del sql_data[k]
    # 数据库链接
    with sjapi.connection() as db:
        # 查询交易总条数
        total = ModSql.yw_jhrw_001.execute_sql(db, "data_count", sql_data)[0].count
        # 查询交易列表
        jbxx = ModSql.yw_jhrw_001.execute_sql_dict(db, "data_rs", sql_data)
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = jbxx
    
    # 将查询到的结果反馈给view
    return data
    
def zdfqjylb_edit_sel_service( data_dic ):
    """
    # 编辑页面初始化组织数据 service
    """
    # 初始化反馈信息
    result = {'state':False, 'msg':'','jyjbxx_dic': {}}
    # 获取交易基本信息
    with sjapi.connection() as db:
        obj_lst = ModSql.common.execute_sql_dict( db, 'get_jyxx2pz', data_dic )
        # 查询出结果，对交易基本信息字典进行赋值
        if obj_lst:
            result['jyjbxx_dic'] = obj_lst[0]
    # 是否成功标记为True
    result['state'] = True
    # 将查询到的结果反馈给view
    return result
    
def zdfqjylb_edit_service( sql_data ):
    """
    # 编辑提交 service
    """
    # 初始化返回值
    result = {'state':False, 'msg':''}
    # 数据库连接
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
        # 处理交易的计划任务信息
        # 组织保存数据
        upd_dic = { 'zdfqpz': sql_data['zdfqpz'],'zdfqpzsm': sql_data['zdfqpzsm'], 'rwlx': 'jy','ssid': sql_data['id'],'zt': sql_data['zt'] }
        # 调用公共更新方法
        ret,msg = update_jhrw( db, sql_data['yzt'], sql_data['yzdfqpz'], upd_dic = upd_dic )
        # 如果更新成功，继续做其他数据库操作
        if ret == True:
            # 更新交易基本信息
            sql_data.update( {'czr':get_sess_hydm(), 'czsj':get_strftime()} )
            ModSql.yw_jhrw_001.execute_sql_dict( db, "update_jydy", sql_data )
            # 更新唯一码
            update_wym( db, 'jy', sql_data['id'] )
            # 清除memcache
            memcache_data_del( [sql_data['jym']] )
            # 登记操作日志
            # 组织内容
            nr = "自动发起交易列表-编辑自动发起交易：编辑前[%s]，编辑后 [业务名称：%s，交易码：%s，交易名称：%s，crontab配置：%s，状态：%s]" % (
                sql_data['ynr'], sql_data['ywmc'], sql_data['jym'], sql_data['jymc'], sql_data['zdfqpz'], sql_data['zt']
            )
            # 调用公共函数保存数据库
            ins_czrz( db, nr, pt = sql_data['pt'], gnmc = '自动发起交易列表-编辑自动发起交易' )
            # 组织反馈值
            result['state'] = True
            result['msg'] = '编辑成功'
        # 更新失败，将错误信息反馈给前台
        else:
            result['msg'] = msg
    # 将查询到的结果反馈给view
    return result
