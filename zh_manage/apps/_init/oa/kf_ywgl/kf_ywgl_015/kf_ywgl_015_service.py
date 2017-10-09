# -*- coding: utf-8 -*-
# Action: 流程-自动化测试编码
# Author: liuhh
# AddTime: 2015-2-15
# Standard: 注释仅能以“#”开头,sql可以是“--”；注释不能同代码在同一行

import copy,pickle,binascii
from sjzhtspj import ModSql
from sjzhtspj.common import lc_data_service, get_strftime, format_log, db_hex_to_binary, get_strfdate2, change_log_msg
from sjzhtspj.esb import readlog

def workflow_service(id,pc,lx,csalid):
    """
    # 查询出流程图中各普通节点和子流程节点的ID，及子流程下的节点ID
    """
    # 调用公共方法获取流程图
    workflow = lc_data_service(id,lx)
    with sjapi.connection() as db:
        key = 'ssjyid'
        # 列表数据结构
        zxbz_dic = {}
        # 节点高亮的list
        jdgl = []
        # 日志字典
        rz_dic = {}
        # 循环获取流程图的所有节点{'nodeid':{'sftg':'1','rzlsh':'1','zxjg':'1','fhz':''}, 'nodeid1':{'sftg':'1','rzlsh':'1','zxjg':'1','fhz':''}}
        return_data = {work['nodeid']:{'sftg':'','rzlsh':'','zxjg':'1','fhz':''} for work in workflow[0].values()}
        
        # 获取流程图中每个节点的执行结果
        # 获取日志列表
        rzlb = ModSql.kf_ywgl_015.execute_sql_dict(db, "get_rzlb", {"id":csalid, "pc":pc})
        for rz in rzlb:
            log = eval(rz['rzlb'].read())
            log = str(log).replace(',','\n').replace('[','').replace(']','')
            # 将日志组织成字典
            rz_dic[rz['jdcsalzxbz']] = log
            # 如果lb的数据中带有[,也就是[('1', '19cc8dca6b544478b336b36188c55830', '1')]这种数据格式，说明执行失败了。
            if rz['lb'].find('[') != -1:
                ev = eval(rz['lb'])[0]
                nodeid = ev[1]
                if return_data.get(nodeid):
                    return_data[nodeid]['zxjg'] = '0'
        # 获取节点的实际返回值
        jdfhz = ModSql.kf_ywgl_015.execute_sql_dict(db, "get_csal_jdxx_yslb_sjscz", {'pc':pc, 'jdcsalid':csalid, 'lx':lx})
        # 组织节点的实际返回值数据
        jdfhz_dic = {jz['jdcsalzxbz']:jz['sjscz'] for jz in jdfhz}
        
        idlst = ModSql.kf_ywgl_015.execute_sql_dict(db, "get_csalbz", {"id":csalid})
        idlst = idlst[0]['jdcsalzxbzlb'].split(',')
        # 获取该测试案例的执行步骤
        alxx = ModSql.kf_ywgl_015.execute_sql_dict(db, "get_csalxx", {"idlst":idlst})
        # 获取节点定义id
        jddyids = []
        if lx == 'lc':
            jddyids = ModSql.kf_ywgl_015.execute_sql_dict(db, "get_bjid_jy", {"value":id})
        else :
            jddyids = ModSql.kf_ywgl_015.execute_sql_dict(db, "get_bjid_zlc", {"value":id})
        jddy = {jd['jddyid']:jd['id'] for jd in jddyids}
        # 将执行步骤组织成固定数据
        for al in alxx:
            if return_data.get(al['ssdyid']) != None:
                return_data[al['ssdyid']]['sftg'] = al['sftg']
                return_data[al['ssdyid']]['rzlsh'] = al['rzlsh']
                # 如果是跳过类型的节点，直接将日志放到rzlsh中
                if al['sftg'] != '0':
                    return_data[al['ssdyid']]['rzlsh'] = rz_dic.get(al['id'])
                if al['sftg'] != '0':
                    # 如果是跳过节点的话，返回值就是测试案例步骤的返回值。
                    return_data[al['ssdyid']]['fhz'] = al.get('fhz')
                else:
                    return_data[al['ssdyid']]['fhz'] = jdfhz_dic.get(al['id'])
                # 设置节点的测试案例的步骤的返回值，也就是预期的返回值。
                return_data[al['ssdyid']]['fhz_y'] = al.get('fhz')
                if jddy.get(al['ssdyid']):
                    return_data[al['ssdyid']]['ssdyid'] = jddy.get(al['ssdyid'])
                else:
                    return_data[al['ssdyid']]['ssdyid'] = jddy.get('jystart')
                
                # 查询步骤的输出要素的执行结果
                # 如果节点返回值和节点执行结果不一致，就标注异常。
                if return_data[al['ssdyid']]['fhz'] != al.get('fhz'):
                    jdgl.append(al.get('ssdyid'))
        for jd in return_data.values():
            for w in workflow[1]:
                # 获取需要高亮的连接线【实际的流程走向】
                if jd.get('ssdyid') == w['source'] and jd.get('fhz') == w['label'] and (jd['fhz'] != '' and jd['fhz'] != None and jd['fhz'] != 'None'):
                    w['hl'] = True
                # 获取需要高亮的连接线【预期的流程走向】
                if jd.get('ssdyid') == w['source'] and jd.get('fhz_y') == w['label']:
                    w['hl_y'] = True
        workflow.append(return_data)
        workflow.append(jdgl)
        return workflow

def csal_jbxx_service(map):
    """
    # 获取流程-测试案例定义基本的信息
    """
    with sjapi.connection() as db:
        # 根据测试案例定义表ID查询测试案例
         csal = ModSql.kf_ywgl_009.execute_sql_dict(db, "get_csal_jbxx", map)[0]
         return csal

def csal_jdxx_service(map):
    """
    # 获取流程-测试案例定义节点的信息
    """
    with sjapi.connection() as db:
        #根据测试案例的ID获取节点测试案例执行步骤列表
        jdcsalzxbz = ModSql.kf_ywgl_009.execute_sql(db, "get_csal_jdxx_jdcsalzxbzlb_id", map)[0]
        jdcsalzxbzids = jdcsalzxbz['jdcsalzxbzlb'].split(",")
        # 根据测试案例定义表ID查询出的测试案例执行步骤,进行获取节点信息
        jdxxlb = ModSql.kf_ywgl_009.execute_sql_dict(db, "get_csal_jdxx_jdcsalzxbzlb_data", {"jdcsalzxbz":jdcsalzxbzids})
        # 按照执行步骤进行排序
        sortlst = [ [row for row in jdxxlb if row["id"] == i][0] for i in jdcsalzxbzids]
        if map['lx'] == 'lc':
            rs_jdmc = ModSql.common.execute_sql_dict(db, "get_jdmc", {'id_lst': [row['ssdyid'] for row in jdxxlb]})
            for row in sortlst:
                if row['ssdyid'] in [row['id'] for row in rs_jdmc if row['jdlx'] == '9']:
                    row['jdmc'] = '%s[%s]' % ('交易开始', row['jdmc'])
                elif row['ssdyid'] in [row['id'] for row in rs_jdmc if row['jdlx'] == '8']:
                    row['jdmc'] = '%s[%s]' % ('交易结束', row['jdmc'])
        if map['lx'] == 'zlc':
            sortlst.insert(0,{'sftg': '0', 'jdmc': '开始','id': '1', 'mc': '开始', 'lx': '-1', 'fhz': '0', 'demoid': ''})
            sortlst.insert(len(sortlst),{'sftg': '0', 'jdmc': '结束','id': '1', 'mc': '结束', 'lx': '-1', 'fhz': '0', 'demoid': ''})
        return {'rows':sortlst,'zxjg':map['zxjg'],'jgsm':map['jgsm']}

def csal_jdxx_jbxx_service(map):
    """
    # 获取流程-测试案例定义节点输入输出要素
    """
    with sjapi.connection() as db:
        # 根据节点测试案例执行步骤ID查询出输出要素的信息
        map['jd'] = 'false'
        map['lx'] = '2'
        scys = {}
        # 由于通讯子流程没有期望输出要素，所以，和普通的交易，节点，取值方式不一致。
        if map.get('lxdm') == '4':
            # 判断通讯的节点有没有执行
            count = ModSql.kf_ywgl_013.execute_sql(db, "get_txjd_run", map)[0].count
            if count > 0:
                # 如果执行了，就获取真实交易返回数据
                scys = ModSql.kf_ywgl_013.execute_sql_dict(db, "get_csal_jdxx_yslb_txlx", map)
            else:
                scys = ModSql.kf_ywgl_013.execute_sql_dict(db, "get_csal_jdxx_yslb", map)
        else:
            scys = ModSql.kf_ywgl_013.execute_sql_dict(db, "get_csal_jdxx_yslb", map)
        if scys:
            db_hex_to_binary(scys)
        # 根据节点测试案例执行步骤ID查询出输入要素的信息
        map['lx'] = '1'
        srys = ModSql.kf_ywgl_013.execute_sql_dict(db, "get_csal_jdxx_yslb", map)
        if srys:
            db_hex_to_binary(srys)
        return {'srys':srys, 'scys':scys, 'demoid':""}

def get_rz_service(pc,csalid,jdcsalzxbzid,mark):
    """
    # 获取日志信息
    """
    log_all = []
    with sjapi.connection() as db:
        # 日志
        log = ''
        # 获取系统日期( zcl 有从XTRQ中获取改为使用当前日期 )
        jyrq = get_strfdate2()
        if mark != 'all':
            # 根据测试案例执行步骤id获取日志流水号
            res = ModSql.kf_ywgl_015.execute_sql_dict(db, "get_rzlsh", {"jdcsalzxbzid":jdcsalzxbzid})[0]
            if res['sftg'] == '1':
                # 获取跳过的日志
                rzlb = ModSql.kf_ywgl_015.execute_sql_dict(db, "get_rzlb", {"id":csalid, "pc":pc, "jdcsalzxbzid":jdcsalzxbzid})
                if len(rzlb):
                    log = eval(rzlb[0]['rzlb'].read())
                    log = str(log).replace(',','\n').replace('[','').replace(']','')
            else:
                rzlsh = res['rzlsh']
                log_lst_dic = readlog(jyrq, rzlsh)
                log_all = change_log_msg( log_lst_dic )
                log = format_log(log_all)
            return {'state': True, 'msg': '', 'log': log}
        else:
            connector = []
            # 获取日志列表
            rzlb = ModSql.kf_ywgl_015.execute_sql_dict(db, "get_rzlb", {"id":csalid, "pc":pc})
            for rz in rzlb:
                if rz['rzlb'] != None:
                    rz['rzlb'] = eval(rz['rzlb'].read())
                    for r in rz['rzlb']:
                        if isinstance(r,list):
                            log_all.extend(r)
                        else:
                            # 请求核心的readlog方法获取日志
                            log_lst_dic = readlog(jyrq, r)
                            log_all.extend( change_log_msg( log_lst_dic ) )
            log = format_log(log_all)
            return {'state': True, 'msg': '', 'log': log}

def get_jdrz_service(rzlsh):
    """
    # 获取日志信息
    """
    with sjapi.connection() as db:
        # 获取系统日期
        jyrq = get_strfdate2()
        # 请求核心的readlog方法获取日志
        log_lst_dic = readlog(jyrq, rzlsh)
        log_all = change_log_msg( log_lst_dic )
        log = format_log(log_all)
        return {'state': True, 'msg': '', 'log': log}
