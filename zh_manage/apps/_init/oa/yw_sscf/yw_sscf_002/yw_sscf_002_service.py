# -*- coding: utf-8 -*-
# Action: 主机详细信息监控
# Author: zhangzhf
# AddTime: 2015-05-16
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行
import json,datetime,re,operator
from sjzhtspj import ModSql,get_sess_hydm
from sjzhtspj.common import ins_czrz,get_strftime,get_uuid,get_task_lsh,trans_io_dic,update_jhrw,trans_mem_dic,update_wym_yw
from ...yw_jkgl.yw_jkgl_002.yw_jkgl_002_service import able_service_common
# 进程更新公共函数
from sjzhtspj.esb import send_pm


def index_service(sql_data):
    """
    # 主机详细信息页面加载service
    """
    # 数据结构    
    data = {'yj':0,'yc':0,'sxpl':0,'zjmc':'','zt':'0'}
    # 数据库链接
    with sjapi.connection() as db:
        # 获取主机信息进行展示
        zjxx = ModSql.yw_sscf_002.execute_sql_dict(db, "get_zjxx", sql_data)
        sql_data['yjjb'] = '3'
        # 获取异常数量
        yc_r = ModSql.yw_sscf_002.execute_sql(db, "get_yj_yc_count", sql_data)
        if len(yc_r):
            data['yc'] = yc_r[0].count
        # 获取预警数量
        # 当前日期，预警级别2时显示当前日期
        sql_data['rq'] = datetime.datetime.now().strftime('%Y%m%d')
        sql_data['yjjb'] = '2'
        yj_r = ModSql.yw_sscf_002.execute_sql(db, "get_yj_yc_count", sql_data)
        if len(yj_r):
            data['yj'] = yj_r[0].count
        
        # 刷新频率
        data['sxpl'] = zjxx[0]['sxpl']
        # 主机名称
        data['zjmc'] = zjxx[0]['mc']
        # 主机状态
        data['zt'] = zjxx[0]['zt']
        return data
        
def zjxx_service(sql_data):
    """
    # 主机各个指标信息的service
    """
    # 数据结构    
    data = {'cpu':{}, 'zjjc':[], 'wj':{}, 'io':{}, 'wlnc':{}}
    sql_data['zbbm'] = 'get_cpu()'
    #当前时间
    now_time = datetime.datetime.now() 
    # 往前推两个小时
    jlsj_start = (now_time - datetime.timedelta(hours=2)).strftime('%Y%m%d%H%M%S')
    # 往前推一个小时
    jlsj_start1 = (now_time - datetime.timedelta(hours=1)).strftime('%Y%m%d%H%M%S')
    # 当前日期
    dqrq = datetime.datetime.now().strftime('%Y%m%d')
    if sql_data['mark'] == 'big':
        sql_data['jlsj_start'] = jlsj_start
    else:
        sql_data['jlsj_start'] = jlsj_start1
    sql_data['jlsj_end'] = now_time.strftime('%Y%m%d%H%M%S')
    # 数据库链接
    with sjapi.connection() as db:
        # cpu信息 {'keys':[], 'values':{}, 'time':[], 'time_l':[], 'length':1}
        cpuxx = {'key_c':['用户使用','系统使用','IO等待'], 'keys':['us','sy','wa'], 'values':{'us':[], 'sy':[], 'wa':[]}, 'time':[], 'time_l':[], 'length':1}
        # time 时间轴
        time = []
        # 查询cpu使用率
        cpuxx_r = ModSql.yw_sscf_002.execute_sql_dict(db, "get_cpu_info", sql_data)
        for cpu in cpuxx_r:
            b = cpu['nr'].split(':')
            c = [x.strip() for x in b[1].split(',')]
            #用户使用
            us = c[0].split('%')[0]  
            #系统使用
            sy = c[1].split('%')[0]  
            #IO等待
            wa = c[4].split('%')[0] 
            cpuxx['values']['us'].append(us)
            cpuxx['values']['sy'].append(sy)
            cpuxx['values']['wa'].append(wa)
            cpuxx['time'].append(formatetime((cpu['jlsj'])))
            # 如果是记录时间往前推一个小时那么就将时间放到time_1中
            if int(cpu['jlsj']) > int(jlsj_start1):
                cpuxx['time_l'].append(formatetime((cpu['jlsj'])))
        data['cpu'] = cpuxx
        #################################################################################
        # 主机进程查看条件
        sql_data['zbbm'] = 'get_process()'
        sql_data['dqsj'] = dqrq
        # 主机进程信息list 
        jcxx = {'jcxx':[], 'length':1}
        # 主机进程查看
        jcxx_r = ModSql.yw_sscf_002.execute_sql_dict(db, "get_jc_info", sql_data)
        for jc in jcxx_r:
            if jc['nr'] != None:
                jc['nr'] = jc['nr'].read() if jc['nr'] else ''
                jc_nr = eval(jc['nr'])
                n = {}
                for k,v in jc_nr.items():
                    # id是冗余，但是前台treegrid需要两个field，如不，就会在选中时出现异常。
                    n = {'id':get_uuid(),'state':'closed','parent':True,'jcmc':k,'children':[]}
                    for ls in v.split('\n'):
                        if ls:
                            n['children'].append({'id':get_uuid(),'jcmc':ls, 'parent':False})
                    jcxx['jcxx'].append(n)
        data['zjjc'] = jcxx
                
        #################################################################################
        cp_xx = {}
        cp_name = []
        # 文件系统使用率数据结构       
        cpkjsyl = {'xx':{}, 'time':[], 'keys':[], 'length':1, 'time_l':[]}
        sql_data['cjmc'] = 'get_filesystem()'
        # 文件系统使用率查看
        wjxt_r = ModSql.yw_sscf_002.execute_sql_dict(db, "get_xtxx", sql_data)
        # 获取磁盘名称对应的list
        for wj in wjxt_r:
            cp_name.append(wj['cjmc'].replace('filesystem',''))
        # 采集名称去重
        cp_name = list(set(cp_name))
        for wj in wjxt_r:
            wjxt_j = wj['nr'].split('|')
            # 使用率
            syl = int(wjxt_j[4].replace('%',''))
            # 未使用率
            wsyl = 1 - syl
            # cjmc
            cjmc_key = wj['cjmc'].replace('filesystem','')
            if (cjmc_key in list(cp_xx.keys())) == False:
                cp_xx[cjmc_key] = []
            # [wjxtmc = 文件系统名称,syl = 使用率, wsyl = 未使用率,ysy = 已使用,wsy = 未使用]
            cp_xx[cjmc_key].append([wjxt_j[0],syl,wsyl,int(wjxt_j[2]),int(wjxt_j[3])])
            cpkjsyl['time'].append(formatetime2(str(wj['jlsj'])))
            # 如果是记录时间往前推一个小时那么就将时间放到time_1中
            if int(wj['jlsj']) > int(jlsj_start1):
                cpkjsyl['time_l'].append(formatetime2(str(wj['jlsj'])))
        # 去重
        cpkjsyl['time'] = sorted(list(set(cpkjsyl['time'])))
        cpkjsyl['time_l'] = sorted(list(set(cpkjsyl['time_l'])))
        cpkjsyl['xx'] = cp_xx
        cpkjsyl['keys'] = sorted(cp_name)
        cpkjsyl['length'] = len(cp_name)
        data['wj'] = cpkjsyl    
        
        #################################################################################
        # io信息 {'keys':[], 'values':{}, 'time':[]}
        ioxx = {'keys':[], 'values':{}, 'time':[], 'length':1, 'time_l':[]}
        # time时间轴
        time = []
        # 磁盘I/O繁忙率
        sql_data['cjmc'] = 'get_io()'
        io_r = ModSql.yw_sscf_002.execute_sql_dict(db, "get_xtxx", sql_data)
        # 要解析的数据
        io_pt = []
        # keys
        keys = []
        # 组织要解析的数据
        for io in io_r:
            if io['nr'] == None:
                io['nr'] = ''
            io_pt.append(io['nr'])
        # 解析io数据
        iofml = trans_io_dic(io_pt)
         # 组织要解析的数据
        for io in io_r:
            time.append(formatetime(io['jlsj']))
            keys = list(iofml.keys())  
            # 如果是记录时间往前推一个小时那么就将时间放到time_1中
            if int(io['jlsj']) > int(jlsj_start1):
                ioxx['time_l'].append(formatetime((io['jlsj'])))  
        # 组织数据
        ioxx['keys'] = keys
        ioxx['values'] = iofml
        ioxx['time'] = time
        data['io'] = ioxx    
        
        #################################################################################
        wlncxx = {'xx':[], 'time':[], 'length':1, 'time_l':[]}
        # 查询物理内存
        sql_data['cjmc'] = 'get_ram()'
        wlnc_r = ModSql.yw_sscf_002.execute_sql_dict(db, "get_xtxx", sql_data)
        for wl in wlnc_r:
            nc = re.findall(r"\d+\.?\d*",wl['nr'])
            # 已使用
            ysy = int(nc[0])
            # 未使用
            wsy = int(nc[1])
            # [syl = 使用率,wsyl = 未使用率,ysy = 已使用,wsy =未使用]
            wlncxx['xx'].append([ysy/(ysy+wsy), wsy/(ysy+wsy), ysy, wsy])
            wlncxx['time'].append(formatetime2(wl['jlsj']))
            # 如果是记录时间往前推一个小时那么就将时间放到time_1中
            if int(wl['jlsj']) > int(jlsj_start1):
                wlncxx['time_l'].append(formatetime2(wl['jlsj']))
        data['wlnc'] = wlncxx   
        return data
        
def kr_jc_service(sql_data):
    """
    # 重启进程service
    """
    # 返回结果
    data = {'state':True, 'msg':'操作成功'}
    # 获取流水号
    lsh = get_task_lsh()
    # 数据库链接
    with sjapi.connection() as db:
        # 根据进程名称，获取进程信息
        jcxx_lst = ModSql.yw_sscf_002.execute_sql_dict(db, "get_jcxx_byjcmc", sql_data)
        if jcxx_lst:
            # 进程信息id
            sql_data['id'] = jcxx_lst[0]['id']
            # 原进程类型
            sql_data['old_jclx'] = jcxx_lst[0]['jclx']
            # 新进程类型
            sql_data['new_jclx'] = get_uuid()
            # 更新进程类型
            ModSql.yw_sscf_002.execute_sql_dict(db, "update_jcxx_jclx", sql_data)
        else:
            data = {'state':False, 'msg':'此进程未定义，无法重启'}
    # 更新进程类型成功
    if data['state'] == True:
        # 首先发送原来的进程类型，因为此进程类型已经修改，在进程信息表中不存在，所以此进程会停止
        content = { 'param':[sql_data['old_jclx']] }
        send_pm( content, sql_data['ip'] )
        # 第二次发送新的进程类型，此ip+进程类型存在，则会重启次进程
        content = { 'param':[sql_data['new_jclx']] }
        send_pm( content, sql_data['ip'] )
        with sjapi.connection() as db:
            # 获取所属ID
            ssid_r = ModSql.yw_sscf_002.execute_sql_dict(db, "get_ssid", sql_data)
            if len(ssid_r) > 0:
                ssid = ssid_r[0]
                # 对当前剩余的进程进行重新采集
                s_data = {'id':get_uuid(), 'lsh':lsh, 'rwlx':'cj', 'rq':datetime.datetime.now().strftime('%Y%m%d'),'zdfqpz':ssid['zdfqpz'], 'ssid':ssid['id'], 'ip':sql_data['ip'], 'jhfqsj':datetime.datetime.now().strftime('%H%M'), 'zt':'0', 'sfkbf':'0', 'yjjb':'1'}
                ModSql.yw_sscf_002.execute_sql(db, "add_drzxjh", s_data)
    
    return data
    
def set_refresh_service(sql_data):
    """
    # 刷新频率配置service
    """
    # 返回结果
    data = {'state':True, 'msg':'操作成功', 'sxpl':0}
    # 数据库链接
    with sjapi.connection() as db:
        sql_data['sxpl'] = int(sql_data['sxpl'])
        # 更新刷新频率
        ModSql.yw_sscf_002.execute_sql(db, "update_sxpl", sql_data)
        # 设置返回到前台的刷新频率
        data['sxpl'] = sql_data['sxpl']
        return data
        
def get_yjxx_service(sql_data):
    """
    # 获取预警信息service
    """
    # 返回结果
    data = {'rows':[], 'total':0}
    # 数据库链接
    with sjapi.connection() as db:
        # 若预警级别为2预警，只展示当天的即可
        if sql_data['yjjb'] == '2':
            # 当前日期
            sql_data['rq'] = datetime.datetime.now().strftime('%Y%m%d')
        data['rows'] = ModSql.yw_sscf_002.execute_sql_dict(db, "get_yjxx", sql_data)
        data['total'] = ModSql.yw_sscf_002.execute_sql(db, "get_yjxx_count", sql_data)[0].count
        return data
        
def get_xydzxx_service(sql_data):
    """
    # 获取响应动作列表service
    """
    # 返回结果
    data = {'rows':[], 'total':0}
    # 数据库链接
    with sjapi.connection() as db:
        data['rows'] = ModSql.yw_sscf_002.execute_sql_dict(db, "get_xydzxx", sql_data)
        data['total'] = ModSql.yw_sscf_002.execute_sql(db, "get_xydzxx_count", sql_data)[0].count
        for da in data['rows']:
            if da['jhsj']:
                da['jhsj'] = formatetime3(da['jhsj'])
            if da['dzzxsj']:
                da['dzzxsj'] = formatetime2(da['dzzxsj'])
        return data
        
def update_clgc_service(sql_data):
    """
    # 获取响应动作列表service
    """
    # 返回结果
    data = {'state':True, 'msg':'操作成功'}
    # 数据库链接
    with sjapi.connection() as db:
        sql_data['clr'] = get_sess_hydm()
        sql_data['clsj'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        # 根据执行计划ID更新处理过程
        ModSql.yw_sscf_002.execute_sql(db, "add_yccljg", sql_data)
        # 更新当日执行计划表
        ModSql.yw_sscf_002.execute_sql(db, "update_drzxjh", sql_data)
        nr = "主机详细信息-预警处理：函数名称[%(hsmc)s]，中文名称[%(zwmc)s]，规则描述[%(gzms)s]，流水号[%(lsh)s]" % sql_data
        # 调用公共函数保存数据库
        ins_czrz( db, nr, pt = 'wh', gnmc = '主机详细信息-预警处理' )
        return data
        
def able_jk_service(sql_data):
    """
    # 禁用启用监控service
    """
    # 返回结果
    data = {'state':True, 'msg':sql_data['z_zt']+'成功','zt':sql_data['zt']}
    # 需要禁用或者启用的id列表
    ids = ""
    # 数据库链接
    with sjapi.connection() as db:
        # 获取监控的对象列表
        dxid = ModSql.yw_sscf_002.execute_sql_dict(db, "get_jkdx", sql_data)
        # 整理对象id的数据list
        dxid_lst = [id['dxid'] for id in dxid]
        ids = ','.join(dxid_lst)
        # 启用禁用监控对象 ids,zt,wizt,xx,data,db
        able_service_common(ids,sql_data['zt'],sql_data['f_zt'],sql_data['z_zt'],{},db)
        # 记录操作日志
        nr = '主机详细信息-%(z_zt)s监控：主机名称[%(zjmc)s]，主机IP[%(ip)s]，%(z_zt)s监控' % sql_data
        ins_czrz( db, nr, pt = 'wh', gnmc = '主机详细信息-%(z_zt)s监控' % sql_data )
        return data

def jkpzgl_service(ip):
    """
    # 监控配置service
    """
    data = []
     # 数据库链接
    with sjapi.connection() as db:
        data = []
        jk_zt_dic = {}
        sql_data = {'zbbm':['get_cpu()','get_ram()','get_filesystem()','get_io()'],'ip':ip}
        # 获取监控配置
        re_data = ModSql.yw_sscf_002.execute_sql_dict(db, "get_jkpz", sql_data)
        # 存放监控指标的对象
        jk_dic = {'get_cpu()':[],'get_ram()':[],'get_filesystem()':[],'get_io()':[]}
        jk_zt_dic = {'get_cpu()':'','get_ram()':'','get_filesystem()':'','get_io()':''}
        # 形成监控指标和状态对应的字典
        for d in re_data:
            if len(jk_dic[d['zbbm']]) < 1:
                data.append(d)
            jk_dic[d['zbbm']].append(d['cjpzzt'])
        # 判断某一个指标的状态
        for k,v in jk_dic.items():
            if '1' in v:
                jk_zt_dic[k] = '1'
            elif None in v:
                jk_zt_dic[k] = ''
            else:
                jk_zt_dic[k] = '0'
        # 排序
        data.sort(key=operator.itemgetter('zbbm'),reverse=True)
        # 循环将状态给对应的
        for d in data:
            d['cjpzzt'] = jk_zt_dic[d['zbbm']]
        return data
        
def update_jkpzgl_service(ip,xx, oldxx):
    """
    # 更新监控配置service
    """
    data = {'state':True, 'msg':'操作成功'}
    xx = eval(str(json.loads(xx)))
    oldxx = eval(str(json.loads(oldxx)))
    xx_dic = {ob['zbbm']:ob['zt'] for ob in xx}
     # 数据库链接
    with sjapi.connection() as db:
        # 判断出现变化的监控配置
        o_dic = {ob['zbbm']:ob['cjpzzt'] for ob in oldxx}
        #chang = {[ob['zbbm']] : ob['zt'] for ob in xx if ob['zt'] != o_dic[ob['zbbm']]}
        zbbm_lst = list(xx_dic.keys())
        # 查询指标编码对应的crontab配置和对象采集配置的id
        dxcjpzxx = ModSql.yw_sscf_002.execute_sql_dict(db, "get_dxcjpzxx", {'ip':ip,'zbbm_lst':zbbm_lst})
        for dxc in dxcjpzxx:
            # 更新计划任务信息
            upd_dic = { 'zdfqpz': dxc['zdfqpz'],'zdfqpzsm': dxc['zdfqpzsm'], 'rwlx': 'cj','ssid': dxc['dxcjpzid'],'zt': xx_dic[dxc['zbbm']] }
            if dxc['lx'] == '2':
                # 调用公共更新方法
                ret,msg = update_jhrw( db, o_dic[dxc['zbbm']], dxc['zdfqpz'], upd_dic = upd_dic )
            # 将对象采集配置的采集配置状态
            ModSql.yw_sscf_002.execute_sql_dict(db, "update_dxcjpz_cjpzzt", {'cjpz_zt':xx_dic[dxc['zbbm']], 'id':dxc['dxcjpzid']})
        return data
        
def jkjcpz_service(sql_data):
    """
    # 监控进程配置管理service
    """
    data = {'rows':[], 'total':0}
     # 数据库链接
    with sjapi.connection() as db:
        # 获取监控进程
        data['rows'] = ModSql.yw_sscf_002.execute_sql_dict(db, "get_jcpzxx", sql_data)
        # 获取监控进程总条数
        data['total'] = ModSql.yw_sscf_002.execute_sql(db, "get_jcpzxx_count", sql_data)[0].count
        return data
        
def get_jclxzt_service(sql_data):
    """
    # 获取进程类型和进程状态service
    """
    data = {'jclx':[], 'jczt':[], 'jclx_w':[], 'txwjmc':[], 'zjmc':''}
     # 数据库链接
    with sjapi.connection() as db:
        sql_data['lx'] = '10027'
        # 获取进程类型
        data['jclx'].extend(ModSql.yw_sscf_002.execute_sql_dict(db, "get_bmwh", sql_data))
        sql_data['lx'] = '10001'
        # 获取状态
        data['jczt'].extend(ModSql.yw_sscf_002.execute_sql_dict(db, "get_bmwh", sql_data))
        # 通讯文件名称
        data['txwjmc'].extend(ModSql.yw_sscf_002.execute_sql_dict(db, "get_txwjmc", {}))
        data['jclx_w'].extend(data['jclx'])
        # 获取主机名称
        data['zjmc'] = ModSql.yw_sscf_002.execute_sql_dict(db, "get_zjmc", sql_data)[0]['mc']
        data['jclx'].insert(0,{'bm':'-1','mc':'请选择'})
        data['jczt'].insert(0,{'bm':'-1','mc':'请选择'})
        return data
        
def add_jcpz_service(sql_data):
    """
    # 进程配置添加service
    """
    data = {'state':True, 'msg':'新增成功'}
    # 数据库链接
    with sjapi.connection() as db:
        # 判断通讯文件名称-(启动类型)是否重复
        count = ModSql.yw_sscf_002.execute_sql(db, "get_jclxcount", sql_data)[0].count
        if count > 0:
            data['state'] = False
            data['msg'] = '同一主机，启动类型重复，请重新填写'
            return data
        sql_data['id'] = get_uuid()
        sql_data['czr'] = get_sess_hydm()
        sql_data['czsj'] = get_strftime()
        sql_data['jclx'] = get_uuid()
        # 添加进程
        ModSql.yw_sscf_002.execute_sql(db, "add_jcpz", sql_data)
        # 更新进程信息表中的唯一码
        update_wym_yw( db, 'jcxxpz', sql_data['id'] )
        # 登记操作日志
        nr = '主机详细信息-监控新增：主机IP[%(ip)s]，主机名称[%(zjmc)s]，进程名称[%(jcmc)s]，进程数量[%(jcsl)s]，查看命令[%(ckml)s]，启动命令[%(qdml)s]，通讯文件名称[%(txwjmc)s] ，状态[%(state)s]' % sql_data
        ins_czrz( db, nr, pt = 'wh', gnmc = '主机详细信息-进程新增' )
    # 启动进程
    content = { 'param':[sql_data['jclx']] }
    send_pm( content, sql_data['ip'] )
    # 反馈新增结果
    return data

def get_jcpz_edit_service(sql_data):
    """
    # 进程配置添加service
    """
    data = {'state':True, 'msg':'' , 'xx':{}}
     # 数据库链接
    with sjapi.connection() as db:
        data['xx'] = ModSql.yw_sscf_002.execute_sql_dict(db, "get_jcxx_edit", sql_data)[0]
        return data

def edit_jcpz_service(sql_data):
    """
    # 进程配置编辑service
    """
    data = {'state':True, 'msg':'编辑成功'}
    # 旧数据
    oldData = eval(str(json.loads(sql_data['oldData'])))
    # 数据库链接
    with sjapi.connection() as db:
        # 判断通讯文件名称-(启动类型)是否重复
        count = ModSql.yw_sscf_002.execute_sql(db, "get_jclxcount", sql_data)[0].count
        if count > 0:
            data['state'] = False
            data['msg'] = '同一主机，启动类型重复，请重新填写'
            return data
        sql_data['czr'] = get_sess_hydm()
        sql_data['czsj'] = get_strftime()
        # 铺地数据前台控件为禁用状态，数据获取不到
        if oldData['ly'] == 'pd':
            # 启动命令
            sql_data['qdml'] = oldData['qdml']
            # 启动类型（通讯文件名称）
            sql_data['txwjmc'] = oldData['txwjmc']
        # 更新进程
        ModSql.yw_sscf_002.execute_sql(db, "edit_jcpz", sql_data)
        # 修改前数据
        oldData['ip'] = sql_data['ip']
        oldData['zjmc'] = sql_data['zjmc']
        # 更新进程信息表中的唯一码
        update_wym_yw( db, 'jcxxpz', sql_data['id'] )
        # 登记操作日志
        nr_q = '主机IP[%(ip)s]，主机名称[%(zjmc)s]，进程数量[%(jcsl)s]，进程名称[%(jcmc)s]，查看命令[%(ckml)s]，启动命令[%(qdml)s]，通讯文件名称[%(txwjmc)s]，状态[%(zt)s]' % oldData
        nr_h = '主机IP[%(ip)s]，主机名称[%(zjmc)s]，进程数量[%(jcsl)s]，进程名称[%(jcmc)s]，查看命令[%(ckml)s]，启动命令[%(qdml)s]，通讯文件名称[%(txwjmc)s]，状态[%(state)s]' % sql_data
        nr = '主机详细信息-进程编辑，编辑前：【%(nr_q)s】，编辑后：【%(nr_h)s】' % {'nr_q':nr_q, 'nr_h':nr_h}
        ins_czrz( db, nr, pt = 'wh', gnmc = '主机详细信息-进程编辑' )
    
    # 更新进程
    content = { 'param':[oldData['jclx']] }
    send_pm( content, sql_data['ip'] )
    
    return data

def del_jcpz_service(rows,ip,zjmc):
    """
    # 删除进程信息service
    """
    # 初始化反馈信息
    data = {'state':True, 'msg':'删除成功'}
    # rows的data（ 删除详细信息 ）
    rows = eval(str(json.loads(rows)))
    # 数据库链接
    with sjapi.connection() as db:
        # 记录进程名称
        war_list = []
        # 校验进程有对应的采集信息
        for r in rows:
            sql_data = {'ip':ip,'jcmc':r['jcmc']}
            count = ModSql.yw_sscf_002.execute_sql(db, "check_jc_cj", sql_data)[0].count
            if count != 0: 
                war_list.append(r['jcmc'])
        if len(war_list) > 0:
            data['state'] = False
            data['msg'] = '【%s】进程有对应的采集信息，请先删除之后再来操作' % war_list
            return data
        jcid_lst = [r['id'] for r in rows]
        ModSql.yw_sscf_002.execute_sql(db, "del_jcxx", {'jcid_lst':jcid_lst})
        rizhi = []
        # 组织日志
        for r in rows:
            r['ip'] = ip
            r['zjmc'] = zjmc
            rz = '主机IP[%(ip)s]，主机名称[%(zjmc)s]，进程名称[%(jcmc)s]，进程数量[%(jcsl)s]，查看命令[%(ckml)s]，通讯文件名称[%(txwjmc)s] ，状态[%(zt)s]' % r
            rizhi.append(rz)
        nr = "进程配置管理-删除：%s" % rizhi
        ins_czrz( db, nr, pt = 'wh', gnmc = '进程配置管理-删除' )
    
    # 更新进程
    for jcxx in rows:
        content = { 'param':[jcxx['jclx']] }
        send_pm( content, ip )
    
    return data

def update_yj_yc_service(sql_data):
    """
    # 主机详细信息页面加载service
    """
    # 数据结构    
    data = {'yj':0,'yc':0}
    # 数据库链接
    with sjapi.connection() as db:
        sql_data['yjjb'] = '3'
        # 获取异常数量
        data['yc'] = ModSql.yw_sscf_002.execute_sql(db, "get_yjxx_count", sql_data)[0].count
        # 获取预警数量
        # 当前日期，预警级别2时显示当前日期
        sql_data['rq'] = datetime.datetime.now().strftime('%Y%m%d')
        sql_data['yjjb'] = '2'
        data['yj'] = ModSql.yw_sscf_002.execute_sql(db, "get_yjxx_count", sql_data)[0].count
        return data
        
def formatetime(time):
    """
    # 将时间格式化为   2014-11-21 13:00:00
    """
    time = time[8:10] + ':' + time[10:12] + ':' + time[12:14]
    return time
    
def formatetime2(time):
    """
    # 将时间格式化为   13:00:00
    """
    time = time[:4]+'-'+time[4:6]+'-'+time[6:8]+' '+time[8:10] + ':' + time[10:12] + ':' + time[12:14]
    return time
    
def formatetime3(time):
    """
    # 将时间格式化为   2014-11-21
    """
    time = time[:4]+'-'+time[4:6]+'-'+time[6:8]
    return time