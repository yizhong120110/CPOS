# -*- coding: utf-8 -*-
# Action: 大屏监控-大屏监控展示配置
# Author: zhangchl
# AddTime: 2015-05-28
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import datetime
from sjzhtspj import ModSql, get_sess_hydm
from sjzhtspj.common import ( get_strfdate2, get_xtcsdy, trans_mem_dic, get_time_lst, get_bmwh_bm, 
                            update_xtcsdy_bycsdm, get_strftime, get_uuid, ins_czrz, update_wym_yw )
def index_service():
    """
    # 大屏监控 主页面 service
    """
    # 初始化反馈值
    data = {}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询所有的主机信息
        data['zjxx_lst'] = ModSql.yw_sscf_001.execute_sql_dict( db, 'get_zjxx_lst' )
        # 大屏监控，刷新频率
        sxpl_dic = get_xtcsdy( db, 'SXPL' )
        if sxpl_dic:
            # 有值，取刷新频率
            data['sxpl'] = sxpl_dic['value']
        else:
            # 无值，默认60
            data['sxpl'] = '60'
    
    # 将结果反馈给view
    return data

#def page_reload_service():
#    """
#    # 获取页面刷新数据 service
#    """
#    # 初始化返回值
#    data = { 'state': False, 'msg': '', 'zjxx_lst': [], 'jybs_dic': {}, 'ywjymx_lst': [], 'sjkhhs_dic': {}, 'sxpl': '60' }
#    # 数据库链接
#    with sjapi.connection() as db:
#        # 从参数表中获取页面刷新频率(刷新频率默认为60秒)
#        sxpl = get_xtcsdy( db, 'SXPL' ).get( 'value', '60' )
#        data['sxpl'] = sxpl
#        # 获取需要监控的主机IP和名称(正常的)
#        zjjbxx_lst = ModSql.yw_sscf_001.execute_sql_dict( db, 'get_zjxx_lst', {'zt':'1'} )
#        # 获取各个主机异常数量
#        zjyc_lst = ModSql.yw_sscf_001.execute_sql_dict( db, 'get_ip_yjxx', {'fxgzjg': 'True', 'yjjb':'3'} )
#        # 将结果集转化为字典
#        ip_zjyc_dic = dict( [ ( obj['ip'], obj['num'] ) for obj in zjyc_lst ] )
#        # 获取各个主机预警数量(只获取当天未处理的)
#        zjyj_lst = ModSql.yw_sscf_001.execute_sql_dict( db, 'get_ip_yjxx', {'fxgzjg': 'True', 'yjjb':'2','rq': get_strfdate2()} )
#        # 将结果集转化为字典
#        ip_zjyj_dic = dict( [ ( obj['ip'], obj['num'] ) for obj in zjyj_lst ] )
#        # 获取各个主机的CPU使用率
#        sql_data = { 'sxpl': sxpl, 'cjmc': 'cpu', 'ip_lst': [ obj['ip'] for obj in zjjbxx_lst ] }
#        # 获取cpu使用情况
#        cpu_lst = []
#        if zjjbxx_lst:
#            cpu_lst = ModSql.yw_sscf_001.execute_sql_dict( db, 'get_cjjg', sql_data )
#        # 各个ip对应cpu使用情况
#        cpu_dic = {}
#        for obj in cpu_lst:
#            if obj['ip'] not in cpu_dic:
#                cpu_dic[obj['ip']] = []
#            cpusyl = 100 - float(obj['nr'].split(",")[3].split("%")[0])
#            cpu_dic[obj['ip']].append( round(cpusyl, 2) )
#        # 获取各个主机内存使用率
#        sql_data['cjmc'] = 'ncsy'
#        ncsy_lst = []
#        if zjjbxx_lst:
#            ncsy_lst = ModSql.yw_sscf_001.execute_sql_dict( db, 'get_cjjg', sql_data )
#        # 调用公共函数对查询结果进行调整数据类型
#        ncsy_lst = trans_mem_dic( ncsy_lst )
#        # 各个主机内存使用率字典
#        ncsy_dic = {}
#        for ncsydic in ncsy_lst:
#            # ip
#            ip = list( ncsydic.keys() )[0]
#            # 各个使用率字典
#            syl_dic = list( ncsydic.values() )[0]
#            # 判断此ip是否存在
#            if ip not in ncsy_dic:
#                ncsy_dic[ip] = []
#            # 计算使用率
#            dqwlncyz = (float(syl_dic.get('p_use','0'))/(float(syl_dic.get('p_use','0'))+float(syl_dic.get('p_un_use','0'))))*100
#            ncsy_dic[ip].append( round(dqwlncyz, 2) )
#        # 已获取的主机IP开始循环获取主机信息，只处理状态为“启用”的IP
#        zjxx_lst = []
#        for obj in zjjbxx_lst:
#            # 初始化
#            zjxx_dic = { 'ip': obj['ip'], 'mc': obj['mc'], 'zj_id': obj['id'], 'yjjb': '1', 'yjsl': '0', 
#                        'cpu_lst': ['0'], 'cpu_subtext': '', 'mem_lst': ['0'], 'mem_subtext': '' }
#            # 预警信息 TODO
#            # 首先查看是否有异常
#            if ip_zjyc_dic.get( zjxx_dic['ip'], 0 ) > 0:
#                zjxx_dic['yjjb'] = '3'
#                zjxx_dic['yjsl'] = ip_zjyc_dic.get( zjxx_dic['ip'], 0 )
#            # 如果没有异常，查看是否有预警
#            elif ip_zjyj_dic.get( zjxx_dic['ip'], 0 ) > 0:
#                zjxx_dic['yjjb'] = '2'
#                zjxx_dic['yjsl'] = ip_zjyj_dic.get( zjxx_dic['ip'], 0 )
#            # cpu使用率
#            zjxx_dic['cpu_lst'] = cpu_dic.get( obj['ip'],['0'] )
#            if zjxx_dic['cpu_lst']:
#                zjxx_dic['cpu_subtext'] = '%s%%' % ( str( zjxx_dic['cpu_lst'][-1] ) )
#            # 内存使用率
#            zjxx_dic['mem_lst'] = ncsy_dic.get( obj['ip'], ['0'] )
#            if zjxx_dic['mem_lst']:
#                zjxx_dic['mem_subtext'] = '%s%%' % ( str( zjxx_dic['mem_lst'][-1] ) )
#            # 将总结出的结果放到结果集中
#            zjxx_lst.append( zjxx_dic)
#        data['zjxx_lst'] = zjxx_lst
#        # 获取交易笔数信息
#        # 获取交易笔数间隔时间（秒）DPJK_JYBS_JKJG
#        jybs_jyjg_dic = get_xtcsdy( db, 'DPJK_JYBS_JKJG' )
#        # 刷新频率默认为30分钟
#        jybs_jyjg = jybs_jyjg_dic.get('value','18000') 
#        # 获取交易日期( zcl 有从XTRQ中获取改为使用当前日期 )
#        jyrq = get_strfdate2()
#        # 调用公共函数获取时间点列表
#        time_lst = get_time_lst( jyrq, seconds_bj = str(jybs_jyjg) )
#        # 查询各个时间点对应的交易信息
#        # 时间点列表
#        sjd_lst = []
#        # 交易总笔数列表
#        jyzbs_lst = []
#        # 失败总笔数列表
#        sbzbs_lst = []
#        # 异常总笔数列表
#        yczbs_lst = []
#        # 成功总笔数列表
#        cgbs_lst = []
#        # 查询当日到最新事件点交易情况
#        jyxx_lst = ModSql.yw_sscf_001.execute_sql( db, 'get_jyxx_byjysj', {'jyrq': jyrq,'jysj': time_lst[-1]} )
#        # 查询从零点到各个时间点的交易笔数信息
#        for jysj in time_lst:
#            # 总笔数
#            jyzbs = 0
#            # 失败总笔数( 10:失败 )
#            sbzbs = 0
#            # 异常总笔数（88：异常）
#            yczbs = 0
#            # 成功总笔数（01：成功）
#            cgzbs = 0
#            for jyxx in jyxx_lst:
#                if jysj.replace(':','') >= jyxx.jysj:
#                    # 总笔数
#                    jyzbs += 1
#                    if jyxx.zt == '10':
#                        sbzbs += 1
#                    elif jyxx.zt == '88':
#                        yczbs += 1
#                    elif jyxx.zt == '01':
#                        cgzbs += 1
#            # 将本时间点上的信息追加到结果集中
#            sjd_lst.append( jysj[:5] )
#            jyzbs_lst.append( jyzbs )
#            sbzbs_lst.append( sbzbs )
#            yczbs_lst.append( yczbs )
#            cgbs_lst.append( cgzbs )
#        
#        # 将处理后的结果放在结果集中
#        data['jybs_dic'] = {
#            'sjd_lst': sjd_lst,
#            'jyzbs_lst': jyzbs_lst,
#            'sbzbs_lst': sbzbs_lst,
#            'yczbs_lst': yczbs_lst,
#            'cgzbs_lst': cgbs_lst
#        }
#        # 业务交易明细
#        # 将交易日期放在查询条件中
#        sql_data = {'jyrq': jyrq}
#        # 总笔数
#        total_lst = ModSql.yw_sscf_001.execute_sql( db, 'get_yw_jybs', sql_data )
#        # 失败总笔数( 10:失败 )
#        sql_data['zt'] = '10'
#        failed_lst = ModSql.yw_sscf_001.execute_sql( db, 'get_yw_jybs', sql_data )
#        # 异常总笔数（88：异常）
#        sql_data['zt'] = '88'
#        err_lst = ModSql.yw_sscf_001.execute_sql( db, 'get_yw_jybs', sql_data )
#        # 成功总笔数（01：成功）
#        sql_data['zt'] = '01'
#        success_lst = ModSql.yw_sscf_001.execute_sql( db, 'get_yw_jybs', sql_data )
#        # 整理数据
#        # 对当前查询数据：失败数、异常数、成功数进行数据格式处理
#        failed_dic = dict([(k['ywmc'],k['jybs']) for k in failed_lst])
#        err_dic = dict([(k['ywmc'],k['jybs']) for k in err_lst])
#        success_dic = dict([(k['ywmc'],k['jybs']) for k in success_lst])
#        # 组织业务交易明细监控反馈值( 初始化中先将总笔数进行初始化 )
#        data['ywjymx_lst'] = [{ 'ID': obj['ywid'], 'ywmc': obj['ywmc'],'total': obj['jybs'] } for obj in total_lst]
#        # 初始化其他状态类型的数据
#        for jyxx_dic in data['ywjymx_lst']:
#            jyxx_dic['success'] = success_dic.get(jyxx_dic['ywmc'],0)
#            jyxx_dic['failed'] = failed_dic.get(jyxx_dic['ywmc'],0)
#            jyxx_dic['err'] = err_dic.get(jyxx_dic['ywmc'],0)
#        # 数据库会话数
#        # 获取当日数据库会话采集信息
#        hhs_rs = ModSql.yw_sscf_001.execute_sql_dict( db, 'get_cjjg_day', {'cjmc': 'get_conversation'} )
#        # 首先获取涉及到的数据库用户
#        username_lst = []
#        for obj in hhs_rs:
#            # 数据库回话数( 
#            # [{'username': None, 'count': 17}, {'username': 'JNGT', 'count': 1}] )
#            content = eval( obj['nr'] )
#            username_lst.extend( [ xx_dic['username'] for xx_dic in content if xx_dic['username'] ] )
#        # 去除重复的用户
#        username_lst = list( set(username_lst) )
#        # 初始化统计时间列表
#        db_sjd_lst = []
#        # 给每个用户初始化列表
#        user_hhs_dict = dict( [ ( username, [] ) for username in username_lst ] )
#        # 组织各个时间点，各个用户的会话数
#        for obj in hhs_rs:
#            # 记录时间
#            jlsj = '%s:%s:%s' % ( obj['jlsj'][:2], obj['jlsj'][2:4], obj['jlsj'][4:] )
#            db_sjd_lst.append( jlsj )
#            # 数据库会话数
#            content = eval( obj['nr'] )
#            content_dic = dict( [ ( xx_dic['username'], xx_dic['count'] ) for xx_dic in content if xx_dic['username'] ] )
#            # 给每个用户初始化此时点的会话数
#            for username in username_lst:
#                user_hhs_dict[username].append( content_dic.get(username,0) )
#        # 将用户会话数字典，转化为列表
#        user_hhs_lst = []
#        for username in username_lst:
#            user_hhs_lst.append( { 'username': username, 'hhs_lst': user_hhs_dict.get( username,[0] ) } )
#        # 将数据库会话信息追加到反馈信息中
#        # sjd_lst:统计时间点
#        # username_lst： 会话涉及到的用户列表
#        # user_hhs_lst： 各个用户对应的会话列表[{'username':username, 'hhs_lst': hhs_lst},……]
#        data['sjkhhs_dic'] = {
#            'sjd_lst': db_sjd_lst if db_sjd_lst else ['00:00(无数据)'],
#            'username_lst': username_lst if username_lst else ['无数据'],
#            'user_hhs_lst': user_hhs_lst if user_hhs_lst else [{ 'username': '无数据', 'hhs_lst': [0] }]
#        }
#        # 标志获取成功
#        data['state'] = True
#    # 将组织后的结果发送给view
#    return data
    
def page_reload_sjkhhs_service():
    """
    # 获取页面刷新数据 service
    """
    # 初始化返回值
    data = { 'state': False, 'msg': '', 'zjxx_lst': [], 'jybs_dic': {}, 'ywjymx_lst': [], 'sjkhhs_dic': {}, 'sxpl': '60' }
    # 数据库链接
    with sjapi.connection() as db:
        # 数据库会话数
        # 获取当日数据库会话采集信息
        hhs_rs = ModSql.yw_sscf_001.execute_sql_dict( db, 'get_cjjg_day', {'cjmc': 'get_conversation'} )
        # 首先获取涉及到的数据库用户
        username_lst = []
        for obj in hhs_rs:
            # 数据库回话数( 
            # [{'username': None, 'count': 17}, {'username': 'JNGT', 'count': 1}] )
            content = eval( obj['nr'] )
            username_lst.extend( [ xx_dic['username'] for xx_dic in content if xx_dic['username'] ] )
        # 去除重复的用户
        username_lst = list( set(username_lst) )
        # 初始化统计时间列表
        db_sjd_lst = []
        # 给每个用户初始化列表
        user_hhs_dict = dict( [ ( username, [] ) for username in username_lst ] )
        # 组织各个时间点，各个用户的会话数
        for obj in hhs_rs:
            # 记录时间
            jlsj = '%s:%s:%s' % ( obj['jlsj'][:2], obj['jlsj'][2:4], obj['jlsj'][4:] )
            db_sjd_lst.append( jlsj )
            # 数据库会话数
            content = eval( obj['nr'] )
            content_dic = dict( [ ( xx_dic['username'], xx_dic['count'] ) for xx_dic in content if xx_dic['username'] ] )
            # 给每个用户初始化此时点的会话数
            for username in username_lst:
                user_hhs_dict[username].append( content_dic.get(username,0) )
        # 将用户会话数字典，转化为列表
        user_hhs_lst = []
        for username in username_lst:
            user_hhs_lst.append( { 'username': username, 'hhs_lst': user_hhs_dict.get( username,[0] ) } )
        # 将数据库会话信息追加到反馈信息中
        # sjd_lst:统计时间点
        # username_lst： 会话涉及到的用户列表
        # user_hhs_lst： 各个用户对应的会话列表[{'username':username, 'hhs_lst': hhs_lst},……]
        data['sjkhhs_dic'] = {
            'sjd_lst': db_sjd_lst if db_sjd_lst else ['00:00(无数据)'],
            'username_lst': username_lst if username_lst else ['无数据'],
            'user_hhs_lst': user_hhs_lst if user_hhs_lst else [{ 'username': '无数据', 'hhs_lst': [0] }]
        }
        # 标志获取成功
        data['state'] = True
    # 将组织后的结果发送给view
    return data
    
def page_reload_ywjymx_service():
    """
    # 获取业务交易明细数据 service
    """
    # 初始化返回值
    data = { 'state': False, 'msg': '', 'ywjymx_lst': [] }
    # 数据库链接
    with sjapi.connection() as db:
        # 获取交易日期( zcl 有从XTRQ中获取改为使用当前日期 )
        jyrq = get_strfdate2()
        # 业务交易明细
        # 将交易日期放在查询条件中
        sql_data = {'jyrq': jyrq}
        # 总笔数
        total_lst = ModSql.yw_sscf_001.execute_sql( db, 'get_yw_jybs', sql_data )
        # 失败总笔数( 10:失败 )
        sql_data['zt'] = '10'
        failed_lst = ModSql.yw_sscf_001.execute_sql( db, 'get_yw_jybs', sql_data )
        # 异常总笔数（88：异常）
        sql_data['zt'] = '88'
        err_lst = ModSql.yw_sscf_001.execute_sql( db, 'get_yw_jybs', sql_data )
        # 成功总笔数（01：成功）
        sql_data['zt'] = '01'
        success_lst = ModSql.yw_sscf_001.execute_sql( db, 'get_yw_jybs', sql_data )
        # 整理数据
        # 对当前查询数据：失败数、异常数、成功数进行数据格式处理
        failed_dic = dict([(k['ywmc'],k['jybs']) for k in failed_lst])
        err_dic = dict([(k['ywmc'],k['jybs']) for k in err_lst])
        success_dic = dict([(k['ywmc'],k['jybs']) for k in success_lst])
        # 组织业务交易明细监控反馈值( 初始化中先将总笔数进行初始化 )
        data['ywjymx_lst'] = [{ 'ID': obj['ywid'], 'ywmc': obj['ywmc'],'total': obj['jybs'] } for obj in total_lst]
        # 初始化其他状态类型的数据
        for jyxx_dic in data['ywjymx_lst']:
            jyxx_dic['success'] = success_dic.get(jyxx_dic['ywmc'],0)
            jyxx_dic['failed'] = failed_dic.get(jyxx_dic['ywmc'],0)
            jyxx_dic['err'] = err_dic.get(jyxx_dic['ywmc'],0)
        # 标志获取成功
        data['state'] = True
    # 将组织后的结果发送给view
    return data
    
def page_reload_jybs_service():
    """
    # 获取交易笔数数据 service
    """
    # 初始化返回值
    data = { 'state': False, 'msg': '', 'jybs_dic': {}}
    # 数据库链接
    with sjapi.connection() as db:
        # 获取交易笔数信息
        # 获取交易笔数间隔时间（秒）DPJK_JYBS_JKJG
        jybs_jyjg_dic = get_xtcsdy( db, 'DPJK_JYBS_JKJG' )
        # 刷新频率默认为30分钟
        jybs_jyjg = jybs_jyjg_dic.get('value','18000') 
        # 获取交易日期( zcl 有从XTRQ中获取改为使用当前日期 )
        jyrq = get_strfdate2()
        # 调用公共函数获取时间点列表
        time_lst = get_time_lst( jyrq, seconds_bj = str(jybs_jyjg) )
        # 查询各个时间点对应的交易信息
        # 时间点列表
        sjd_lst = []
        # 交易总笔数列表
        jyzbs_lst = []
        # 失败总笔数列表
        sbzbs_lst = []
        # 异常总笔数列表
        yczbs_lst = []
        # 成功总笔数列表
        cgbs_lst = []
        # 查询当日到最新事件点交易情况
        jyxx_lst = ModSql.yw_sscf_001.execute_sql( db, 'get_jyxx_byjysj', {'jyrq': jyrq,'jysj': time_lst[-1]} )
        # 查询从零点到各个时间点的交易笔数信息
        for jysj in time_lst:
            # 总笔数
            jyzbs = 0
            # 失败总笔数( 10:失败 )
            sbzbs = 0
            # 异常总笔数（88：异常）
            yczbs = 0
            # 成功总笔数（01：成功）
            cgzbs = 0
            for jyxx in jyxx_lst:
                if jysj.replace(':','') >= jyxx.jysj:
                    # 总笔数
                    jyzbs += 1
                    if jyxx.zt == '10':
                        sbzbs += 1
                    elif jyxx.zt == '88':
                        yczbs += 1
                    elif jyxx.zt == '01':
                        cgzbs += 1
            # 将本时间点上的信息追加到结果集中
            sjd_lst.append( jysj[:5] )
            jyzbs_lst.append( jyzbs )
            sbzbs_lst.append( sbzbs )
            yczbs_lst.append( yczbs )
            cgbs_lst.append( cgzbs )
        
        # 将处理后的结果放在结果集中
        data['jybs_dic'] = {
            'sjd_lst': sjd_lst,
            'jyzbs_lst': jyzbs_lst,
            'sbzbs_lst': sbzbs_lst,
            'yczbs_lst': yczbs_lst,
            'cgzbs_lst': cgbs_lst
        }
        # 标志获取成功
        data['state'] = True
    # 将组织后的结果发送给view
    return data
    
def page_reload_zjxx_service():
    """
    # 获取主机信息数据 service
    """
    # 初始化返回值
    data = { 'state': False, 'msg': '', 'zjxx_lst': [], 'sxpl': '60' }
    # 数据库链接
    with sjapi.connection() as db:
        # 从参数表中获取页面刷新频率(刷新频率默认为60秒)
        sxpl = get_xtcsdy( db, 'SXPL' ).get( 'value', '60' )
        data['sxpl'] = sxpl
        # 获取需要监控的主机IP和名称(正常的)
        zjjbxx_lst = ModSql.yw_sscf_001.execute_sql_dict( db, 'get_zjxx_lst', {'zt':'1'} )
        # 获取各个主机异常数量
        zjyc_lst = ModSql.yw_sscf_001.execute_sql_dict( db, 'get_ip_yjxx', {'fxgzjg': 'True', 'yjjb':'3'} )
        # 将结果集转化为字典
        ip_zjyc_dic = dict( [ ( obj['ip'], obj['num'] ) for obj in zjyc_lst ] )
        # 获取各个主机预警数量(只获取当天未处理的)
        zjyj_lst = ModSql.yw_sscf_001.execute_sql_dict( db, 'get_ip_yjxx', {'fxgzjg': 'True', 'yjjb':'2','rq': get_strfdate2()} )
        # 将结果集转化为字典
        ip_zjyj_dic = dict( [ ( obj['ip'], obj['num'] ) for obj in zjyj_lst ] )
        # 获取各个主机的CPU使用率
        sql_data = { 'sxpl': sxpl, 'cjmc': 'cpu', 'ip_lst': [ obj['ip'] for obj in zjjbxx_lst ] }
        # 获取cpu使用情况
        cpu_lst = []
        if zjjbxx_lst:
            cpu_lst = ModSql.yw_sscf_001.execute_sql_dict( db, 'get_cjjg', sql_data )
        # 各个ip对应cpu使用情况
        cpu_dic = {}
        for obj in cpu_lst:
            if obj['ip'] not in cpu_dic:
                cpu_dic[obj['ip']] = []
            cpusyl = 100 - float(obj['nr'].split(",")[3].split("%")[0])
            cpu_dic[obj['ip']].append( round(cpusyl, 2) )
        # 获取各个主机内存使用率
        sql_data['cjmc'] = 'ncsy'
        ncsy_lst = []
        if zjjbxx_lst:
            ncsy_lst = ModSql.yw_sscf_001.execute_sql_dict( db, 'get_cjjg', sql_data )
        # 调用公共函数对查询结果进行调整数据类型
        ncsy_lst = trans_mem_dic( ncsy_lst )
        # 各个主机内存使用率字典
        ncsy_dic = {}
        for ncsydic in ncsy_lst:
            # ip
            ip = list( ncsydic.keys() )[0]
            # 各个使用率字典
            syl_dic = list( ncsydic.values() )[0]
            # 判断此ip是否存在
            if ip not in ncsy_dic:
                ncsy_dic[ip] = []
            # 计算使用率
            dqwlncyz = (float(syl_dic.get('p_use','0'))/(float(syl_dic.get('p_use','0'))+float(syl_dic.get('p_un_use','0'))))*100
            ncsy_dic[ip].append( round(dqwlncyz, 2) )
        # 已获取的主机IP开始循环获取主机信息，只处理状态为“启用”的IP
        zjxx_lst = []
        for obj in zjjbxx_lst:
            # 初始化
            zjxx_dic = { 'ip': obj['ip'], 'mc': obj['mc'], 'zj_id': obj['id'], 'yjjb': '1', 'yjsl': '0', 
                        'cpu_lst': ['0'], 'cpu_subtext': '', 'mem_lst': ['0'], 'mem_subtext': '' }
            # 预警信息 TODO
            # 首先查看是否有异常
            if ip_zjyc_dic.get( zjxx_dic['ip'], 0 ) > 0:
                zjxx_dic['yjjb'] = '3'
                zjxx_dic['yjsl'] = ip_zjyc_dic.get( zjxx_dic['ip'], 0 )
            # 如果没有异常，查看是否有预警
            elif ip_zjyj_dic.get( zjxx_dic['ip'], 0 ) > 0:
                zjxx_dic['yjjb'] = '2'
                zjxx_dic['yjsl'] = ip_zjyj_dic.get( zjxx_dic['ip'], 0 )
            # cpu使用率
            zjxx_dic['cpu_lst'] = cpu_dic.get( obj['ip'],['0'] )
            if zjxx_dic['cpu_lst']:
                zjxx_dic['cpu_subtext'] = '%s%%' % ( str( zjxx_dic['cpu_lst'][-1] ) )
            # 内存使用率
            zjxx_dic['mem_lst'] = ncsy_dic.get( obj['ip'], ['0'] )
            if zjxx_dic['mem_lst']:
                zjxx_dic['mem_subtext'] = '%s%%' % ( str( zjxx_dic['mem_lst'][-1] ) )
            # 将总结出的结果放到结果集中
            zjxx_lst.append( zjxx_dic)
        data['zjxx_lst'] = zjxx_lst
        # 标志获取成功
        data['state'] = True
    # 将组织后的结果发送给view
    return data

def sxpl_edit_service( sql_data ):
    """
    # 更新页面刷新频率 service
    """
    # 数据库链接
    with sjapi.connection() as db:
        # 调用公共函数更新页面刷新频率
        update_xtcsdy_bycsdm( db, 'SXPL', sql_data['sxpl'] )
        # 操作日志
        nr = '大屏监控-页面刷新频率：参数定义[编码为：SXPL（刷新频率）]，编辑前：[%s]，编辑后：[%s]' % ( sql_data['ysxpl'], sql_data['sxpl'] )
        ins_czrz(db, nr, pt='wh', gnmc='大屏监控')
    # 将执行结果发送给view
    return { 'state': True, 'msg': '编辑成功' }

def server_add_sel_service():
    """
    # 服务器新增获取页面初始化数据 service
    """
    # 初始化返回值
    data = { 'zjxx_lst': [{'value': '', 'ms': '', 'text': '请选择'}], 'state': False, 'msg': '' }
    # 数据库连接
    with sjapi.connection() as db:
        # 主机类型
        data['zjxx_lst'].extend( get_bmwh_bm( '10028', db=db ) )
        # 标志获取成功
        data['state'] = True
    # 返回结果给view
    return data

def server_add_service( sql_data ):
    """
    # 服务器新增提交 service
    """
    # 初始化返回值
    data = { 'state': False, 'msg': '' }
    # 数据库链接
    with sjapi.connection() as db:
        # 判断服务器名称是否重复
        check_count =  ModSql.yw_sscf_001.execute_sql( db, 'check_zjxx', { 'mc': sql_data['mc'] } )[0].count
        if check_count > 0:
            data['msg'] = '服务器名称[%s]已经存在，请重新输入' % sql_data['mc']
            return data
        # 判断服务器地址是否重复
        check_count =  ModSql.yw_sscf_001.execute_sql( db, 'check_zjxx', { 'ip': sql_data['ip'] } )[0].count
        if check_count > 0:
            data['msg'] = '服务器hostname[%s]已经存在，请重新输入' % sql_data['ip']
            return data
        # 记录主机信息表
        sql_data.update( { 'zt': '1', 'sxpl': '60', 'ycsl': '0', 'yjsl': '0', 'id': get_uuid() } )
        # 追加主机信息
        ModSql.common.execute_sql( db, 'add_zjxx', sql_data )
        # 操作日志内容
        zjlx_lst = get_bmwh_bm( '10028', db=db )
        zjlx_dic = dict( [ ( obj['value'], obj['text'] ) for obj in zjlx_lst ] )
        nr = '大屏监控-添加主机：服务器名称[%s],服务器hostname[%s],服务器类型[%s]' % ( sql_data['mc'], sql_data['ip'], zjlx_dic.get( sql_data['zjlx'], sql_data['zjlx'] ) )
        # 记录对象定义表
        sql_data.update( { 'id': get_uuid(), 'dxbm': sql_data['ip'], 'dxlx': 'Computer(zjip,dxcjpzid)',
        'dxmc': sql_data['mc'], 'dxms': '大屏监控添加', 'czr': get_sess_hydm(), 'czsj': get_strftime() } )
        # 执行数据库
        ModSql.yw_jkgl_002.execute_sql( db, 'add_jkdx', sql_data )
        # 更新对象表中的唯一码
        update_wym_yw(db, 'dxdy', sql_data['id'])
        # 初始化对象id用于“对象采集配置”新增数据
        sql_data['dxid'] = sql_data['id']
        # 获取监控对象信息(监控指标)
        # 监控指标：cpu使用率，内存使用率，i/o繁忙率，磁盘使用率
        zbbm_lst = [ 'get_cpu()', 'get_ram()', 'get_io()', 'get_filesystem()' ]
        # 根据条件进行查询
        jkzb_lst = ModSql.yw_sscf_001.execute_sql_dict( db, 'get_cjzb_bysslbbm', { 'sslbbm': 'Computer(zjip,dxcjpzid)', 'zbbm_lst': zbbm_lst } )
        for obj in jkzb_lst:
            # 采集配置表
            sql_data.update( { 'id': get_uuid(), 'mc': '%s(%s)'%(obj['zbmc'],sql_data['ip']), 'ms': '大屏监控配置', 'sslbbm': 'Computer(zjip,dxcjpzid)',
                                'zbid': obj['id'], 'lx': '1', 'zdfqpz': '60', 'zdfqpzsm': '每60秒发起一次',
                                'sfkbf': '' } )
            ModSql.yw_sscf_001.execute_sql( db, 'add_cjpzb', sql_data )
            sql_data['sscjpzid'] = sql_data['id']
            # 对象采集配置
            sql_data.update( { 'id': get_uuid(), 'zdzjip': sql_data['ip'], 'pid': '1',
                            'zzzxbbh': '1', 'bbh': '1', 'cjpzzt': '1', 'dxzt': '1', 'lx': '1' } )
            ModSql.yw_sscf_001.execute_sql( db, 'add_dxcjpz', sql_data )
            # 更新数据采集配置表中唯一码
            update_wym_yw(db, 'sjcjpzgl', sql_data['sscjpzid'])
            
        # 操作日志保存
        ins_czrz(db, nr, pt='wh', gnmc='大屏监控')
        # 定义返回值
        data['state'] = True
        data['msg'] = '新增成功'
    # 返回结果给view
    return data