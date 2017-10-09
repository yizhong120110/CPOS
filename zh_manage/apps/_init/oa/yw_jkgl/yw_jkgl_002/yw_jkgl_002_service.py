# -*- coding: utf-8 -*-
# Action: 监控管理-监控对象管理
# Author: zhangzhf
# AddTime: 2015-04-08
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import render_to_string,ModSql,get_sess_hydm
from sjzhtspj.common import ins_czrz,get_strftime,ip_is_called,del_waitexec_task,ins_waitexec_task,get_uuid,update_wym_yw

def index_service():
    """
    # 获取监控管理-监控对象管理的对象类型，对象状态
    """
    # 数据结构    
    data = {'dxlx':[{'lbbm':'','lbmc':'请选择'}], 'dxzt':[{'bm':'','mc':'请选择'}]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询对象类型
        dxlx = ModSql.yw_jkgl_002.execute_sql_dict(db, "get_jklb", {})
        # 查询对象状态
        dxzt = ModSql.yw_jkgl_002.execute_sql_dict(db, "get_ztlb", {})
        # 将查询结果放到结果集中
        data['dxlx'].extend(dxlx)
        data['dxzt'].extend(dxzt)
    return data
    
def data_service(sql_data):
    """
    # 获取监控管理-监控对象管理grid数据
    """
    # 数据结构
    data = {'total':0, 'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询监控对象的条数
        count = ModSql.yw_jkgl_002.execute_sql(db, "get_jkdx_count", sql_data)[0].count
        # 查询监控对象
        jkdx = ModSql.yw_jkgl_002.execute_sql_dict(db, "get_jkdx", sql_data)
        # 将查询结果放到结果集中
        data['total'] = count
        data['rows'] = jkdx
    return data
    
def add_service(sql_data):
    """
    # 添加监控管理-监控对象
    """
    # 数据结构
    data = {'state':True, 'msg':'新增成功'}
    # 数据库链接
    with sjapi.connection() as db:
        sql_data['zt'] = '1' if sql_data['zt'] == 'on' else '0'
        # 对象编码和对象编码类型在对象定义表是联合索引，在插入之前需要先校验对象编码是否存在
        count = ModSql.yw_jkgl_002.execute_sql_dict(db, "check_dxbm", sql_data)[0]['count']
        # 如果对象编码存在
        if count > 0:
            data['state'] = False
            data['msg'] = '对象编码[%s]已经存在，请重新输入！' % (sql_data['dxbm'])
            return data
        # 对象名称和对象编码类型在对象定义表是联合索引，在插入之前需要先校验对象名称是否存在
        count = ModSql.yw_jkgl_002.execute_sql_dict(db, "check_dxmc", sql_data)[0]['count']
        # 如果对象名称存在
        if count > 0:
            data['state'] = False
            data['msg'] = '对象名称[%s]已经存在，请重新输入！' % (sql_data['dxmc'])
            return data
            
        sql_data.update( { 'id': get_uuid(), 'dxms': '监控对象管理', 'czr': get_sess_hydm(), 'czsj': get_strftime() } )
        # 如果所属类别编码是主机
        if sql_data['dxlx'] == 'Computer(zjip,dxcjpzid)':
            if len(sql_data['dxbm']) > 15:
                data['state'] = False
                data['msg'] = '对象编码在对象类型为主机时，长度不得超过15，请重新输入！'
                return data
            else:
                # 新增主机
                sql_data['zjid'] = get_uuid()
                ModSql.yw_jkgl_002.execute_sql(db, "add_zjxx", sql_data)
                # 获取监控对象信息(监控指标)
                # 监控指标：cpu使用率，内存使用率，i/o繁忙率，磁盘使用率
                zbbm_lst = [ 'get_cpu()', 'get_ram()', 'get_io()', 'get_filesystem()' ]
                # 根据条件进行查询
                jkzb_lst = ModSql.yw_sscf_001.execute_sql_dict( db, 'get_cjzb_bysslbbm', { 'sslbbm': 'Computer(zjip,dxcjpzid)', 'zbbm_lst': zbbm_lst } )
                for obj in jkzb_lst:
                    # 采集配置表
                    sql_data.update( { 'id_cjpz': get_uuid(), 'mc': '%s(%s)'%(obj['zbmc'],sql_data['dxbm']), 'ms': '监控对象管理', 'sslbbm': 'Computer(zjip,dxcjpzid)',
                                        'zbid': obj['id'], 'lx': '1', 'zdfqpz': '60', 'zdfqpzsm': '每60秒发起一次',
                                        'sfkbf': '' } )
                    ModSql.yw_jkgl_002.execute_sql( db, 'add_cjpzb', sql_data )
                    sql_data['sscjpzid'] = sql_data['id_cjpz']
                    # 对象采集配置
                    sql_data.update( { 'id_dxcjpz': get_uuid(), 'zdzjip': sql_data['dxbm'],'pid': '1',
                                    'zzzxbbh': '1', 'bbh': '1' if sql_data['zt'] == '1' else '-1', 'cjpzzt': '1', 'lx': '1' } )
                    ModSql.yw_jkgl_002.execute_sql( db, 'add_dxcjpz', sql_data )
                    # 更新数据采集配置表中唯一码
                    update_wym_yw(db, 'sjcjpzgl', sql_data['sscjpzid'])

        # 添加监控对象
        # 执行数据库
        ModSql.yw_jkgl_002.execute_sql(db, "add_jkdx", sql_data)
        # 更新对象表中的唯一码
        update_wym_yw(db, 'dxdy', sql_data['id'])

        # 组织操作日志字典
        ri_data = {'dxbm':sql_data['dxbm'], 'dxlx':sql_data['dxlx'], 'dxmc':sql_data['dxmc'],'dxms':sql_data['dxms'],'zt':sql_data['zt']}
        # 登记操作日志
        rznr = '新增监控对象：对象编码【%(dxbm)s】，所属类别编码【%(dxlx)s】，对象名称【%(dxmc)s】，对象描述【%(dxms)s】,对象状态【%(zt)s】' % ri_data
        ins_czrz(db,rznr,'wh','监控对象管理-添加')
    return data
    
def del_service(ids):
    """
    # 删除监控管理-监控对象
    """
    # 数据结构
    data = {'state':True, 'msg':'删除成功'}
    # 数据库链接
    with sjapi.connection() as db:
        # 监控对象id列表
        ids_lst = ids.split(',')
        # 获取对象列表
        dxlb = ModSql.yw_jkgl_002.execute_sql_dict(db, "get_dxlb", {'ids_lst':ids_lst})
        # 对象名称列表[对象名称1，对象名称2]
        dxmclb = [dx['dxmc'] for dx in dxlb]
        if len(dxmclb) > 0:
            data['state'] = False
            data['msg'] = '对象名称%s已配置采集配置，请取消采集配置后再进行删除' % (str(list(set(dxmclb))))
            return data
        # 查询主机ip
        zjip = ModSql.yw_jkgl_002.execute_sql_dict(db, "get_zjip", {'ids_lst':ids_lst})
        # 查询删除的是否有主机IP，若有，需要查看是否被调用
        ip_tmp = []
        # 循环ip列表
        for ip in zjip:
            # 查询删除的是否有主机IP，若有，需要查看是否被调用
            if ip_is_called(ip['dxbm'],db):
                ip_tmp.append(ip['dxbm'])
        # 若ip_tmp中有值，则返回前台错误信息
        if len(ip_tmp) > 0:
            data['state'] = False
            data['msg'] = '【%s】主机ip被调用，请先取消配置（采集，分析，响应动作），再进行删除' % (str(ip_tmp))
            return data
        # 查询需要删除的信息
        dxxx = ModSql.yw_jkgl_002.execute_sql_dict(db, "get_delxx", {'ids_lst':ids_lst})
        # 若有主机ip，删除主机信息表
        dxbm_lst = [bm['dxbm'] for bm in zjip]
        if len(dxbm_lst) > 0:
            ModSql.yw_jkgl_002.execute_sql(db, "del_zjxx", {'dxbm_lst':dxbm_lst})
        # 删除对象定义信息
        ModSql.yw_jkgl_002.execute_sql(db, "del_dxdy", {'ids_lst':ids_lst})
        rznr = '删除监控对象：%s' % (str(dxxx))
        ins_czrz(db,rznr,'wh','监控对象管理-删除')
    return data
    
def edit_service(sql_data):
    """
    # 编辑监控管理-监控对象
    """
    # 数据结构
    data = {'state':True, 'msg':'编辑成功'}
    # 数据库链接
    with sjapi.connection() as db:
        # 修改前先查询修改之前的内容，留作记录日志使用
        dxlb_old = ModSql.yw_jkgl_002.execute_sql_dict(db, "get_olddxlb", {'id':[sql_data['id']]})
        # 对象名称和对象编码类型在对象定义表是联合索引，在插入之前需要先校验对象名称是否存在
        count = ModSql.yw_jkgl_002.execute_sql_dict(db, "check_dxmc", sql_data)[0]['count']
        # 如果对象名称存在
        if count > 0:
            data['state'] = False
            data['msg'] = '对象名称[%s]已经存在，请重新输入！' % (sql_data['dxmc'])
            return data
        # 更新监控对象
        ModSql.yw_jkgl_002.execute_sql(db, "edit_jkdx", sql_data)
        # 更新对象表中的唯一码
        update_wym_yw(db, 'dxdy', sql_data['id'])
        # 如果所属类别编码是主机
        if sql_data['dxlx'] == 'Computer(zjip,dxcjpzid)' and sql_data['dxmc'] != sql_data['dxmc_old']:
            ModSql.yw_jkgl_002.execute_sql(db, "edit_zjxx", sql_data)
        ri_data = {'dxbm':sql_data['dxbm'], 'dxmc':sql_data['dxmc'], 'dxms':sql_data['dxms']}
        # 登记操作日志
        rznr = "编辑前%(old)s , 编辑后%(new)s" % {'old':dxlb_old[0], 'new':ri_data}
        ins_czrz(db,rznr,'wh','监控对象管理-编辑')
    return data
    
def able_service(ids,zt):
    """
    # 启用禁用监控管理-监控对象
    """
    wizt = '0' if zt == '1' else '1'
    xx = '启用' if zt == '1' else '禁用'
    # 数据结构
    data = {'state':True, 'msg':xx+'成功'}
    # 数据库链接
    with sjapi.connection() as db:
        return able_service_common(ids,zt,wizt,xx,data,db)
    
def get_dxlx_service():
    """
    # 获取对象类型
    """
    # 数据结构
    data = {'state':True, 'msg':'','list':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 获取对象类型
        dxlx = ModSql.yw_jkgl_002.execute_sql_dict(db, "get_jklb", {})
        data['list'].extend(dxlx)
    return data
    
def get_edit_service(id):
    """
    # 获取需要编辑的对象的属性
    """
    # 数据结构
    data = {'state':True, 'msg':'','jkdx':{}}
    # 数据库链接
    with sjapi.connection() as db:
        # 获取对象属性
        data['jkdx'] = ModSql.yw_jkgl_002.execute_sql_dict(db, "get_edit_jkdx", {'id':id})[0]
    return data
    
def able_service_common(ids,zt,wizt,xx,data,db):
    # 监控对象id列表
    ids_lst = ids.split(',')
    # 获取对象列表
    dxlb = ModSql.yw_jkgl_002.execute_sql_dict(db, "get_olddxlb", {'id':ids_lst})
    # 查询前台传送对象ID列表中是禁用或者启用
    jydxid = ModSql.yw_jkgl_002.execute_sql_dict(db, "get_jydx", {'ids_lst':ids_lst, 'zt':wizt})
    # 对象id列表[对象id1，对象id2]
    jydxid_lst = [dx['id'] for dx in jydxid]
    # 若筛选过后的对象ID列表为空
    if len(jydxid_lst) < 1:
        data['state'] = False
        data['msg'] = '选择的列表中的状态都为%s，无需再设' % (xx)
        return data
    # 筛选成功后，更新状态
    ModSql.yw_jkgl_002.execute_sql(db, "edit_jkdx_zt", {'ids_lst':jydxid_lst, 'zt':zt, 'czr':get_sess_hydm(),'czsj':get_strftime()})
    # 查询对象定义表中所属类别编码是主机的信息
    dxbm_lst = ModSql.yw_jkgl_002.execute_sql_dict(db, "get_zjip", {'ids_lst':jydxid_lst})
    if len(dxbm_lst) > 0:  
        dl = [bm['dxbm'] for bm in dxbm_lst]
        # 更新主机信息表
        ModSql.yw_jkgl_002.execute_sql(db, "edit_zjxx_zt", {'dxbm_lst':dl, 'zt':zt})
        # 查询对象采集配置表ID
        ids_dxcjpz = ModSql.yw_jkgl_002.execute_sql_dict(db, "select_dxcjpz_id", {'ids_lst':jydxid_lst})
        ds = []
        for k in ids_dxcjpz:
            ds.append(k['id'])
        # 修改对象采集表中的指定主机状态
        ModSql.yw_jkgl_002.execute_sql(db, "edit_dxcjpz_zdzjzt", {'zdzjzt_lst':ds, 'zt':zt})
    # 查询对象采集配置表
    dxcjpzxx_lst = ModSql.yw_jkgl_002.execute_sql_dict(db, "get_dxcjpz", {'ids_lst':jydxid_lst})
    # 类型是主机的时候，根据监控对象的对象编码查询对象采集配置。
    zjlx_dxbm_lst = []
    for dx in jydxid:
        # 如果是主机的话，需要去查询主机对应的对象采集配置
        if dx['sslbbm'] == 'Computer(zjip,dxcjpzid)':
            zjlx_dxbm_lst.append(dx['dxbm'])
    if zjlx_dxbm_lst:
        dxcjpzxx_lst.extend(ModSql.yw_jkgl_002.execute_sql_dict(db, "get_dxcjpz_from_zdzjip", {'zdzjip_lst':zjlx_dxbm_lst}))
    # 循环更新对象采集配置表
    for dxcjpzxx in dxcjpzxx_lst:
        bbh = 0
        bbh_data = {'bbh':dxcjpzxx['bbh'],'zt':'','dxzt':wizt,'lx':'','dxcjpzid':dxcjpzxx['id'], 'czr':get_sess_hydm(),'czsj':get_strftime()}
        bbh_data['dxzt'] = zt
        # 对象id条件
        bbh_data['dxid_lst'] = jydxid_lst
        # 更新对象采集配置表中的对象状态
        ModSql.yw_jkgl_002.execute_sql(db, "edit_dxcjpz_zt", bbh_data)
        # 查询对象采集配置的对象状态状态
        dxcjpz_dxzt = ModSql.yw_jkgl_002.execute_sql_dict(db, "get_dxcjpz_dxzt", {'id':dxcjpzxx['id']})[0]
        # 更新版本号
        if dxcjpzxx['cjpzzt'] == '1' and dxcjpzxx['lx'] == '1' and dxcjpz_dxzt['dxzt'] == '1' and dxcjpzxx['zdzjzt'] == '1':
            bbh_data['lx'] = '1'
            bbh_data['bbh'] = int(dxcjpzxx['bbh'])+1
        if zt == '0':
            bbh_data['lx'] = ''
            bbh_data['bbh'] = -1
        # 更新对象采集配置表中的版本号
        ModSql.yw_jkgl_002.execute_sql(db, "edit_dxcjpz_bbh", bbh_data)
        # 若对象采集配置状态为启用且类型为2（计划任务），则需更新计划任务表
        if dxcjpzxx['lx'] == '2' and zt == '1':
            # 查询计划任务表id
            rwbid = ModSql.yw_jkgl_002.execute_sql_dict(db, "get_jhrwid", {'sscjpzid':dxcjpzxx['id'],'zdzjip':dxcjpzxx['zdzjip']})
            # 更新计划任务表
            for rw in rwbid:
                lins_zt = '0'
                if dxcjpzxx['cjpzzt'] == '1' and dxcjpzxx['zdzjzt'] == '1':
                    lins_zt = '1'
                ModSql.yw_jkgl_002.execute_sql(db, "edit_jhrwzt", {'jhrwid':rw['id'], 'zt':lins_zt})
                # 更新成功后，往当日执行计划表中插入执行数据
                ins_waitexec_task(rw['id'],db)
        elif dxcjpzxx['lx'] == '2' and zt == '0':
            # 查询计划任务表id
            rwbid = ModSql.yw_jkgl_002.execute_sql_dict(db, "get_jhrwid", {'sscjpzid':dxcjpzxx['id'],'zdzjip':dxcjpzxx['zdzjip'],'zt':wizt})
            # 更新计划任务表
            for rw in rwbid:
                ModSql.yw_jkgl_002.execute_sql(db, "edit_jhrwzt", {'jhrwid':rw['id'], 'zt':zt})
                del_waitexec_task(rw['id'],db)
    ri_data = {'zt':xx,'dxlb':str(dxlb)}
    rznr = '设置监控对象状态为%(zt)s：【%(dxlb)s】' % ri_data
    gnmc = '监控对象管理-状态%(zt)s' % ri_data
    ins_czrz(db,rznr,'wh',gnmc)
    return data