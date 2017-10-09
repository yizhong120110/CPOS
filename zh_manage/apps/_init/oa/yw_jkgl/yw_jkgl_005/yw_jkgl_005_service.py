# -*- coding: utf-8 -*-
# Action: 数据采集配置管理
# Author: zhangzhf
# AddTime: 2015-04-27
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行
import json
from sjzhtspj import ModSql,get_sess_hydm
from sjzhtspj.common import ins_czrz,get_strftime,del_waitexec_task,ins_waitexec_task,crontab_fy,get_uuid,del_waitexec_task,ins_waitexec_task,update_wym_yw
from ...yw_jkgl.yw_jkgl_002.yw_jkgl_002_service import able_service_common

def index_service():
    """
    # 获取监控管理-监控对象管理的对象类型，对象状态
    """
    # 数据结构    
    data = {'cjlb':[{'lbbm':'','lbmc':'请选择'}], 'sfbf':[{'bm':'','mc':'请选择'}], 'zt':[{'bm':'','mc':'请选择'}], 'cjzb':[{'id':'','zbmc':'请选择'}], 'lb_zb':{}}
    # 数据库链接
    with sjapi.connection() as db:
        lb_zb = {}
        # 查询采集类型
        cjlb = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_lb", {})
        # 查询是否可并发
        sfbf = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_bmwh", {'lx':'10007'})
        # 查询状态
        zt = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_bmwh", {'lx':'10001'})
        # 查询采集指标
        for lb in cjlb:
            cjzb = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_cjzb", {'cjlb':lb.get('lbbm')})
            lb_zb[lb.get('lbbm')] = cjzb
        # 将查询结果放到结果集中
        data['cjlb'].extend(cjlb)
        data['sfbf'].extend(sfbf)
        data['zt'].extend(zt)
        data['lb_zb'] = lb_zb
    return data
    
def data_service(sql_data):
    """
    # 获取数据采集配置管理grid数据
    """
    # 数据结构
    data = {'total':0, 'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询数据采集配置的条数
        count = ModSql.yw_jkgl_005.execute_sql(db, "get_cjpz_count", sql_data)[0].count
        # 查询数据采集配置
        cjpz = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_cjpz", sql_data)
        # 将查询结果放到结果集中
        data['total'] = count
        data['rows'] = cjpz
    return data

def edit_service(sql_data):
    """
    # 编辑数据采集配置
    """
    # 数据结构
    data = {'state':True, 'msg':'编辑成功','other':{}}
    # 中文发起频率
    z_fqpl = ''
    # crontab配置说明
    c_sm = ''
    if sql_data['sjcj_cjlx'] == '1':
        z_fqpl = '每%s秒发起一次' % (sql_data['fqpl'])
        # 类型为发起频率时，取发起频率的内容
        sql_data['zdfqjyzdfqpz'] = sql_data['fqpl']
        sql_data['zdfqjyzdfqpzsm'] = z_fqpl
        data['other']['c_sm'] = z_fqpl
    elif sql_data['sjcj_cjlx'] == '2':
        # 调用公共函数crontab_fy
        rd = crontab_fy(sql_data['zdfqjyzdfqpz'])
        if rd[0]:
            # 如果校验结果为true , 将翻译说明返回前台
            data['other']['c_sm'] = rd[1]
            # 类型为计划任务时，取crontab配置的内容
            sql_data['zdfqjyzdfqpzsm'] = rd[1]
        else:
            # 如果为False则将message信息，返回前台页面进行提示
            data['state'] = False
            data['msg'] = rd[2]
            return data
    # 将id,采集指标,采集类别返回给前台
    data['other']['id'] = sql_data['id']
    data['other']['cjlb'] = sql_data['cjlb']
    data['other']['cjzb'] = sql_data['cjzb']
    data['other']['state'] = sql_data['state']
    # 数据库链接
    with sjapi.connection() as db:
        # 标识计划任务表的id和状态
        jhrw_dic = {}
        # 计划任务id 的lst
        jhrw_lst = []
        # 查询未编辑前的数据，记录日志使用
        old_data = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_cjpz_old", {'id':sql_data['id']})[0]
        # 校验采集名称是否唯一
        count = ModSql.yw_jkgl_005.execute_sql(db, "check_cjmc", {'mc':sql_data['cjmc'],'id':sql_data['id']})
        if count[0].count > 0:
            data['state'] = False
            data['msg'] = '采集名称[%s]已经存在，请重新输入' % (sql_data['cjmc'])
            return data
        sql_data['czr'] = get_sess_hydm()
        sql_data['czsj'] = get_strftime()
        # 保存采集配置对象
        ModSql.yw_jkgl_005.execute_sql(db, "update_cjpz", sql_data)
        # 更新对象采集配置
        ModSql.yw_jkgl_005.execute_sql(db, "update_dxcjpz", sql_data)
        # 查询版本号 
        bbh = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_cjpz_bbh", {'id':sql_data['id']})
        if len(bbh) > 0:
            bbh = bbh[0]['bbh']
            # 类型为发起频率时，将版本号加1
            if sql_data['sjcj_cjlx'] == '1':
                bbh = bbh + 1
            elif sql_data['sjcj_cjlx'] == '2':
                # 类型为计划任务时，将版本号更新为-1
                bbh = -1
            # 更新对象采集配置表的版本号
            ModSql.yw_jkgl_005.execute_sql(db, "update_cjpz_bbh", {'bbh':bbh,'id':sql_data['id']})
        # 查询计划任务表中是否有对应数据
        jhrw_r = ModSql.yw_jkgl_005.execute_sql(db, "get_jhrw", {'id':sql_data['id']})
        if len(jhrw_r) < 1 and sql_data['sjcj_cjlx'] == '2':
            # 查询对象采集配置表中对应信息
            cjpzxx_lst = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_cjpzxx", {'id':sql_data['id']})
            for cjpzxx in cjpzxx_lst:
                xxzt = ''
                # 只有对象状态和采集配置状态都为启用时，此状态才为启用
                if cjpzxx['dxzt'] == '1' and cjpzxx['cjpzzt'] == '1' and cjpzxx['zdzjzt'] == '1':
                    xxzt = '1'
                else:
                    xxzt = '0'
                s_data = {'id':get_uuid(),'zdfqjyzdfqpz':sql_data['zdfqjyzdfqpz'],'zdfqjyzdfqpzsm':sql_data['zdfqjyzdfqpzsm'],'rwlx':'cj','cjpzid':cjpzxx['id'],'ip':cjpzxx['zdzjip'],'sfkbf':sql_data['sfbf'],'zt':xxzt}
                jhrw_lst.append(s_data['id'])
                jhrw_dic[s_data['id']] = xxzt
                ModSql.yw_jkgl_005.execute_sql(db, "add_jhrw", s_data)
        # 循环得到计划任务的id
        if len(jhrw_r) > 0:
            jhrw_lst = [jhrw['id'] for jhrw in jhrw_r]
            jhrw_dic = {jhrw['id']:jhrw['zt'] for jhrw in jhrw_r}
        # 若类型为发起频率，则将计划任务表中信息删除
        if sql_data['sjcj_cjlx'] == '1':
            # 将计划任务表中信息删除
            ModSql.yw_jkgl_005.execute_sql(db, "del_jhrw", {'id':sql_data['id']})
            for i in jhrw_lst:
                # 将当日计划表中当前时间往后的未执行任务删除
                del_waitexec_task(i,db)
        elif sql_data['sjcj_cjlx'] == '2' and sql_data['zdfqjyzdfqpz'] == old_data['zdfqpz']:
            # 若类型为计划任务，且crontab配置与页面隐藏域的原crontab配置一致，说明此项未修改，则更新计划任务表中数据
            ModSql.yw_jkgl_005.execute_sql(db, "update_jhrw", {'id':sql_data['id'], 'sfkbf':sql_data['sfbf']})
        elif sql_data['sjcj_cjlx'] == '2' and sql_data['zdfqjyzdfqpz'] != old_data['zdfqpz']:
            # 若类型为计划任务，但crontab配置与页面隐藏域的原crontab配置不一致，说明此项有修改，则更新计划任务表中数据
            ModSql.yw_jkgl_005.execute_sql(db, "update_jhrw_s", {'id':sql_data['id'], 'zdfqpz':sql_data['zdfqjyzdfqpz'], 'zdfqpzsm':sql_data['zdfqjyzdfqpzsm'], 'sfkbf':sql_data['sfbf']})
            for i in jhrw_lst:
                # 将当日计划表中当前时间往后的未执行任务删除
                del_waitexec_task(i,db)
        # 若类型为计划任务，且状态为启用，crontab配置有修改
        for i in jhrw_lst:
            if sql_data['sjcj_cjlx'] == '2' and sql_data['zdfqjyzdfqpz'] != old_data['zdfqpz'] and jhrw_dic[i] == '1':
                # 向当日计划表中插入当前时间往后的当日未执行任务
                ins_waitexec_task(i,db)
        old_rz = '采集名称[%(mc)s]，采集类别[%(sslbbm)s]，采集指标[%(zbid)s]，类型[%(lx)s]，发起频率[%(zdfqpz)s]，crontab配置[%(zdfqpz)s]，crontab配置说明[%(zdfqpzsm)s]，是否可并发[%(sfkbf)s]，描述[%(ms)s]' % old_data
        new_rz = '采集名称[%(cjmc)s]，采集类别[%(cjlb)s]，采集指标[%(cjzb)s]，类型[%(sjcj_cjlx)s]，发起频率[%(fqpl)s]，crontab配置[%(zdfqjyzdfqpz)s]，crontab配置说明[%(zdfqjyzdfqpzsm)s]，是否可并发[%(sfbf)s]，描述[%(cjms)s]' % sql_data
        # 更新采集配置表中唯一码
        update_wym_yw( db, 'sjcjpzgl', sql_data['id'] )
        # 登记操作日志
        sql_data = {'old_rz':old_data, 'new_rz':new_rz}
        rznr = '数据采集配置-编辑采集配置。编辑前； %(old_rz)s ， 编辑后：%(new_rz)s' % sql_data
        ins_czrz(db,rznr,'wh','数据采集配置-新增采集配置')
    return data
    
def add_cjpz_service(sql_data):
    """
    # 新增数据采集配置
    """
    # 数据结构
    data = {'state':True, 'msg':'新增成功','other':{}}
    # 中文发起频率
    z_fqpl = ''
    # crontab配置说明
    c_sm = ''
    #sql_data['state'] = '1' if sql_data['state'] == 'on' else '0'
    if sql_data['sjcj_cjlx'] == '1':
        z_fqpl = '每%s秒发起一次' % (sql_data['fqpl'])
        # 类型为发起频率时，取发起频率的内容
        sql_data['zdfqjyzdfqpz'] = sql_data['fqpl']
        sql_data['zdfqjyzdfqpzsm'] = z_fqpl
        data['other']['c_sm'] = z_fqpl
    elif sql_data['sjcj_cjlx'] == '2':
        # 调用公共函数crontab_fy
        rd = crontab_fy(sql_data['zdfqjyzdfqpz'])
        if rd[0]:
            # 如果校验结果为true , 将翻译说明返回前台
            data['other']['c_sm'] = rd[1]
            # 类型为计划任务时，取crontab配置的内容
            sql_data['zdfqjyzdfqpzsm'] = rd[1]
        else:
            # 如果为False则将message信息，返回前台页面进行提示
            data['state'] = False
            data['msg'] = rd[2]
            return data
    # 数据库链接
    with sjapi.connection() as db:
        # 校验采集名称是否唯一
        count = ModSql.yw_jkgl_005.execute_sql(db, "check_cjmc", {'mc':sql_data['cjmc']})
        if count[0].count > 0:
            data['state'] = False
            data['msg'] = '采集名称[%s]已经存在，请重新输入' % (sql_data['cjmc'])
            return data
        sql_data['id'] = get_uuid()
        sql_data['czr'] = get_sess_hydm()
        sql_data['czsj'] = get_strftime()
        # 将id返回给前台
        data['other']['id'] = sql_data['id']
        data['other']['cjlb'] = sql_data['cjlb']
        data['other']['cjzb'] = sql_data['cjzb']
        # 保存采集配置对象
        ModSql.yw_jkgl_005.execute_sql(db, "add_cjpz", sql_data)
        # 更新采集配置表中唯一码
        update_wym_yw( db, 'sjcjpzgl', sql_data['id'] )
        # 登记操作日志
        rznr = '数据采集配置-新增采集配置：采集名称[%(cjmc)s]，采集类别[%(cjlb)s]，采集指标[%(cjzb)s]，类型[%(sjcj_cjlx)s]，发起频率[%(fqpl)s]，crontab配置[%(zdfqjyzdfqpz)s]，crontab配置说明[%(zdfqjyzdfqpzsm)s]，是否可并发[%(sfbf)s]，描述[%(cjms)s]' % sql_data
        ins_czrz(db,rznr,'wh','数据采集配置-新增采集配置')
    return data
    
def get_cjpz_update_service(sql_data):
    """
    # 查询采集配置对象，编辑使用
    """
    # 数据结构
    data = {'state':True, 'msg':'','cjpz':{}}
    # 数据库链接
    with sjapi.connection() as db:
        # 获取采集对象类型
        data['cjpz'] = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_cjpz_update", sql_data)[0]
    return data
    
def get_cjlx_service():
    """
    # 获取采集对象类型
    """
    # 数据结构
    data = [{'lbbm':'','lbmc':'请选择'}]
    # 数据库链接
    with sjapi.connection() as db:
        # 获取采集对象类型
        cjlb = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_lb", {})
        # 将查询结果放到结果集中
        data.extend(cjlb)
    return data
    
def get_sfbf_service():
    """
    # 获取采集对象是否可并发
    """
    # 数据结构
    data = []
    # 数据库链接
    with sjapi.connection() as db:
        # 获取采集对象类型
        data = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_bmwh", {'lx':'10007'})
    return data
    
def get_cjzb_service(sql_data):
    """
    # 获取采集指标
    """
    # 数据结构
    data = [{'id':'','zbmc':'请选择'}]
    # 数据库链接
    with sjapi.connection() as db:
        # 获取采集对象类型
        cjzb = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_cjzb", sql_data)
        # 将查询结果放到结果集中
        data.extend(cjzb)
    return data
    
def get_dxmc_zdzj_service(sql_data):
    """
    # 对象名称下拉框,指定主机下拉列表内容
    """
    # 数据结构
    data = {'state':True,'msg':'','dxmc':[], 'zdzj':[], 'crcs':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 获取对象采集配置id
        cjpzids = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_cjpz_id", sql_data)
        if len(cjpzids) > 0:
            cjpzid_lst = (('id',c['dxid']) for c in cjpzids)
            sql_data['dxid'] = cjpzid_lst
        if sql_data['type'] == 'edit':
            # 获取适用对象
            sydx_r = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_sydxxx", {'sydxid':sql_data['sydxid']})
            if len(sydx_r) < 1:
                data['state'] = False
                data['msg'] = '适用对象已被删除'
                return data
            sql_data['zdzjip'] = sydx_r[0]['zdzjip']
        # 获取对象名称下拉框中的数据
        if sql_data['type'] == 'add':
            sql_data['zt'] = '1'
            data['dxmc'].extend(ModSql.yw_jkgl_005.execute_sql_dict(db, "get_cjdx_comb", sql_data))
            # 获取传入参数列表中参数信息
            data['crcs'].extend(ModSql.yw_jkgl_005.execute_sql_dict(db, "get_crcs", sql_data))
            # 获取指定主机下拉列表内容
            data['zdzj'].extend(ModSql.yw_jkgl_005.execute_sql_dict(db, "get_zj_comb", sql_data))
            data['dxmc'].insert(0,{'id':'','dxmc':'请选择'})
            data['zdzj'].insert(0,{'ip':'','mc':'请选择'})
        else:
            data['dxmc'].extend(ModSql.yw_jkgl_005.execute_sql_dict(db, "get_cjdx_comb_sydx", sql_data))
            # 获取传入参数列表中参数信息
            data['crcs'].extend(ModSql.yw_jkgl_005.execute_sql_dict(db, "get_crcs_for_edit", sql_data))
            # 获取指定主机下拉列表内容
            data['zdzj'].extend(ModSql.yw_jkgl_005.execute_sql_dict(db, "get_zj_comb", sql_data))
    return data

def add_sydx_service(sql_data):
    """
    # 新增适用对象
    """
    # 数据结构
    data = {'state':True,'msg':'新增成功'}
    sql_data['state'] = '1' if sql_data['state'] == 'true' else '0'
    # 数据库链接
    with sjapi.connection() as db:
        # 向对象采集配置表中插入的id
        cxcjpzid = get_uuid()
        #获取采集配置表中需同步到对象采集配置表及计划任务表中的信息
        cjpzxx = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_cjpz_tb_cj", sql_data)
        #获取对象状态，以便同步对象采集配置表时使用
        dxzt = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_dxdy", sql_data)
        # 获取主机状态
        zjzt = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_zjxxzt", {'zdzjip':sql_data['zdzjip']})
        if len(zjzt) > 0:
            zjzt = zjzt[0]['zt']
        else:
            zjzt = ''
        # 计划任务表id
        jh_id = get_uuid()
        sql_data['id'] = cxcjpzid
        sql_data['lx'] = cjpzxx[0]['lx']
        sql_data['cjpzzt'] = sql_data['state']
        sql_data['dxzt'] = dxzt[0]['zt']
        sql_data['zdzjzt'] = zjzt
        sql_data['czr'] = get_sess_hydm()
        sql_data['czsj'] = get_strftime()
        #若类型为发起频率，且适用对象状态，指定主机状态，采集配置状态都为启用，则版本号为0否则，版本号为-1
        if cjpzxx[0]['lx'] == '1' and sql_data['cjpzzt'] == '1' and sql_data['dxzt'] == '1' and sql_data['zdzjzt']:
            sql_data['bbh'] = 0
        else:
            sql_data['bbh'] = -1
        ModSql.yw_jkgl_005.execute_sql(db, "add_dxcjpz", sql_data)
        cs_rz = ''
        sql_data['crcs'] = json.loads(sql_data['crcs'])
        # 将前台传入的各项传入参数ID对应参数值循环插入到参数对应表中
        for c in sql_data['crcs']:
            if c['csz'] == None:
                c['csz'] = ''
            csdyb_id = get_uuid()
            ModSql.yw_jkgl_005.execute_sql(db, "add_csdyb", {'id':csdyb_id, 'crcsid':c['id'],'csz':c['csz'],'lx':'zb','ssid':cxcjpzid})
            # 更新参数对应表唯一码
            update_wym_yw(db,'csdyb',csdyb_id)
            # 生成日志
            cs_rz = cs_rz + '['+c['csdm']+']'+c['csz'] + ' , '
        # 若采集配置表类型为计划任务，则向计划任务表中插入数据
        if cjpzxx[0]['lx'] == '2':
            zt_z = '0'
            if sql_data['cjpzzt'] == '1' and zjzt == '1' and sql_data['dxzt'] == '1':
                zt_z = '1'
            cj_sqd = {'id':jh_id, 'zdfqjyzdfqpz':cjpzxx[0]['zdfqpz'],'zdfqjyzdfqpzsm':cjpzxx[0]['zdfqpzsm'],'rwlx':'cj','cjpzid':cxcjpzid,'ip':sql_data['zdzjip'],'sfkbf':cjpzxx[0]['sfkbf'],'zt':zt_z}
            ModSql.yw_jkgl_005.execute_sql(db, "add_jhrw", cj_sqd)
        if cjpzxx[0]['lx'] == '2' and sql_data['state'] == '1':
            ins_waitexec_task(jh_id,db)
        ri_d = {'cjpzmc':cjpzxx[0]['mc'], 'zdzj':sql_data['zdzjip'],'dxmc':sql_data['cjdxid'], 'cs_rz':cs_rz}
        # 更新数据采集配置表中唯一码
        update_wym_yw( db, 'sjcjpzgl', sql_data['cjpzid'] )
        # 登记操作日志
        rznr = '数据采集配置-新增适用对象：采集配置名称[%(cjpzmc)s]，对象id[%(dxmc)s]，指定主机[%(zdzj)s]，参数代码参数值：%(cs_rz)s' % ri_d
        ins_czrz(db,rznr,'wh','数据采集配置-新增适用对象')
    return data
    
def edit_sydx_service(sql_data):
    """
    # 编辑适用对象
    """
    # 数据结构
    data = {'state':True,'msg':'编辑成功'}
    # 数据库链接
    with sjapi.connection() as db:
        #获取采集配置表中需同步到对象采集配置表及计划任务表中的信息
        cjpzxx = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_cjpz_tb_cj", sql_data)
        # 向对象采集配置表中插入数据
        cxcjpzid = get_uuid()
        cs_rz = ''
        sql_data['crcs'] = json.loads(sql_data['crcs'])
        # 将前台传入的各项传入参数ID对应参数值循环插入到参数对应表中
        for c in sql_data['crcs']:
            if c['csz'] == None:
                c['csz'] = ''
            ModSql.yw_jkgl_005.execute_sql(db, "edit_csdyb", {'id':c['cs_id'], 'csz':c['csz']})
            # 更新参数对应的wym
            update_wym_yw(db,'csdyb',c['cs_id'])
            # 生成日志
            cs_rz = cs_rz + '['+c['csdm']+']'+c['csz'] + ' , '
        # 查询对象采集配置的版本号
        dxcjpz_re = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_dxcjpz_bbh_for_edit", {'id':sql_data['sydxid']})
        for dxc in dxcjpz_re:
            bbh = -1
            if dxc['dxzt'] == '1' and dxc['cjpzzt'] == '1' and dxc['zdzjzt'] == '1':
                bbh = int(dxc['bbh'])+1
            # 更新对象采集配置的版本号
            ModSql.yw_jkgl_005.execute_sql_dict(db, "upate_dxcjpz_bbh", {'id':sql_data['sydxid'],'bbh':bbh})
        ri_d = {'cjpzmc':cjpzxx[0]['mc'], 'zdzj':sql_data['zdzjip'],'dxmc':sql_data['cjdxid'], 'cs_rz':cs_rz}
        # 更新数据采集配置表中唯一码
        update_wym_yw( db, 'sjcjpzgl', sql_data['cjpzid'] )
        # 登记操作日志
        rznr = '数据采集配置-编辑适用对象：采集配置名称[%(cjpzmc)s]，对象id[%(dxmc)s]，指定主机[%(zdzj)s]，参数代码参数值：%(cs_rz)s' % ri_d
        ins_czrz(db,rznr,'wh','数据采集配置-编辑适用对象')
    return data
    
def del_sydx_service(ids,cjpzid,cjpzmc):
    """
    # 删除适用对象
    """
    # 数据结构
    data = {'state':True,'msg':'删除成功'}
    # 适用对象id
    ids_lst = ids.split(',')
    sql_data = {'cjpzid':cjpzid, 'ids_lst':ids_lst,'cjpzmc':cjpzmc}
    # 数据库链接
    with sjapi.connection() as db:
        # 后台先获取需删除的对象采集配置信息
        dxcjpzxx = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_dxcjpzxx", sql_data)
        # nr
        nr = []
        # 对象采集信息，指定主机Ip的list
        dxcjxx = []
        # 循环组织日志内容
        for dx in dxcjpzxx:
            nr.append({'对象名称':dx['dxmc'],'主机名称':dx['mc']})
            dxcjxx.append(dx['zdzjip'])
            
        # 查询类型为发起频率的对象采集配置，逻辑删除
        fqpl_dxcjpz = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_fqpl", {'lx':'1','ids_lst':ids_lst})
        fqpl_dxcjpz_lst = [dx['id'] for dx in fqpl_dxcjpz]
        if len(fqpl_dxcjpz_lst):
            # 逻辑删除类型为发起频率的对象采集配置
            ModSql.yw_jkgl_005.execute_sql(db, "del_fqpl", {'ids_lst':fqpl_dxcjpz_lst})
        # 查询类型为计划任务的对象采集配置，逻辑删除
        jhrw_dxcjpz = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_fqpl", {'lx':'2','ids_lst':ids_lst})
        jhrw_dxcjpz_lst = [dx['id'] for dx in jhrw_dxcjpz]
        if len(jhrw_dxcjpz_lst):
            # 删除类型为计划任务的对象采集配置中信息
            ModSql.yw_jkgl_005.execute_sql(db, "del_dxcjpzxx", {'ids_lst':jhrw_dxcjpz_lst})
        # 删除使用对象对应的参数对应表内容
        ModSql.yw_jkgl_005.execute_sql(db, "del_sydx_dxdyb", {'ids_lst':ids_lst})
        
        sql_data['ip_lst'] = dxcjxx
        # 查询计划任务表中信息
        jhrwbxx = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_jhrwxx", sql_data)
        # 获取计划任务ID列表
        jhlst = [jh['id'] for jh in jhrwbxx]
        # 删除计划任务表中信息
        ModSql.yw_jkgl_005.execute_sql(db, "del_jhrwxx", sql_data)
        for j in jhlst:
            del_waitexec_task(j,db)
        r_d = {'cjpzmc':cjpzmc, 'nr':nr}
        # 更新数据采集配置表中唯一码
        update_wym_yw( db, 'sjcjpzgl', cjpzid )
        # 记录操作日志
        rznr = '数据采集配置-适用对象删除：采集配置名称[%(cjpzmc)s]，删除的对象信息【%(nr)s】' % r_d
        ins_czrz(db,rznr,'wh','数据采集配置-适用对象删除')
        return data
        
def sydx_service(sql_data):
    """
    # 获取适用对象
    """
    # 数据结构
    data = {'total':0,'rows':[], 'csz':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 获取适用对象的grid的列（也就是参数值）
        csxx = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_csxx", sql_data)
        data['csz'].extend([{'csdm':'dxmc', 'cssm':'对象名称'},{'csdm':'zdzj', 'cssm':'指定主机'},{'csdm':'dxzt', 'cssm':'状态'}])
        data['csz'].extend(csxx)
        # 获取适用对象条数
        data['total'] = ModSql.yw_jkgl_005.execute_sql(db, "get_sydxs_count", sql_data)[0].count
        # 获取适用对象
        data['rows'].extend(ModSql.yw_jkgl_005.execute_sql_dict(db, "get_sydxs", sql_data))
        for r in data['rows']:
            # 查询参数
            cs = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_csdyb", {'ssid':r['id']})
            for c in cs:
                if c['csz'] == '' or c['csz'] == None:
                    r[c['csdm']] = c['mrz']
                else:
                    r[c['csdm']] = c['csz']
    return data
    
def del_cjpz_service(ids):
    """
    # 删除采集配置对象
    """
    # 数据结构
    data = {'state':True,'msg':'删除成功'}
    # 适用对象id
    ids_lst = ids.split(',')
    sql_data = {'ids_lst':ids_lst}
    # 数据库链接
    with sjapi.connection() as db:
        # 获取需删除的采集配置信息
        cjmc_r = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_del_cjpzxx", sql_data)
        cjmc = [mc['mc'] for mc in cjmc_r]
        # 获取采集配置下面的所有使用对象
        sydxid = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_sydx", {'ids_lst':ids_lst})
        del_ids = [id['id'] for id in sydxid]
        # 获取计划任务的id
        jhrwid_r = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_jhrwid", sql_data)
        jhrw = [jh['id'] for jh in jhrwid_r]
        # 如果是发起频率的话，就是逻辑删除
        ModSql.yw_jkgl_005.execute_sql(db, "update_del_cjpz", sql_data)
        # 如果是计划任务的话，就是物理删除
        ModSql.yw_jkgl_005.execute_sql(db, "update_del_dxcjpz", sql_data)
        
        # 删除采集配置表
        ModSql.yw_jkgl_005.execute_sql(db, "del_cjpz", sql_data)
        # 删除对象采集配置表
        ModSql.yw_jkgl_005.execute_sql(db, "del_dxcjpz", sql_data)
        if len(jhrw) > 0:
            sql_data['jhrw'] = jhrw
            # 删除计划任务表
            ModSql.yw_jkgl_005.execute_sql(db, "del_jhrw_for_id", sql_data)
        # 删除采集配置中所有适用对象的参数对应表的内容
        if len(del_ids) > 0:
            ModSql.yw_jkgl_005.execute_sql(db, "del_sydx_dxdyb", {'ids_lst':del_ids})
        for j in jhrw:
            del_waitexec_task(j,db)
        # 记录操作日志
        rznr = '数据采集配置-删除：删除的采集配置【%s】' % (cjmc)
        ins_czrz(db,rznr,'wh','数据采集配置-删除')
        return data
        
def able_sydx_service(ids,zt):
    """
    # 启用禁用监控管理-适用对象
    """
    xx = '启用' if zt == '1' else '禁用'
    wizt = '0' if zt == '1' else '1'
    # 数据结构
    data = {'state':True, 'msg':xx+'成功'}
    # 数据库链接
    with sjapi.connection() as db:
        # 监控对象id列表
        ids_lst = ids.split(',')
        sql_data = {'dxcjpz_ids':ids_lst}
        sql_data['wizt'] = wizt
        # 适用对象id
        dxcjpzxx = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_cjpzxx_id", sql_data)
        dx_lst = [c['id'] for c in dxcjpzxx]
        # 若筛选过后的dx_lst列表为空，返回前台提示信息
        if len(dx_lst) < 1:
            data['state'] = False
            data['msg'] = '选择的列表中的状态都为%s，无需再设' % xx
            return data
        sql_data['czr'] = get_sess_hydm()
        sql_data['czsj'] = get_strftime()
        sql_data['zt'] = zt
        # 计划任务 2
        sql_data['lx'] = '2' 
        # 获取对象采集配置为用户操作相反状态、类型为计划任务的数据
        dx_lst = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_dxcjpzxx_foru", sql_data)
        if zt == '1':
            sql_data['lx'] = '1' 
            # 获取需要更新版本好的对象采集配置信息
            bbh_re = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_dxcjpzxx_foru", sql_data)
            # 更新对象采集配置
            ModSql.yw_jkgl_005.execute_sql(db, "upate_dxcjpzxx", sql_data)
            for k in bbh_re:
                if k['dxzt'] == '1' and k['zdzjzt'] == '1':
                    bbh = int(k['bbh']) + 1
                    k['bbh'] = bbh
                    # 更新对象采集配置版本号
                    ModSql.yw_jkgl_005.execute_sql(db, "upate_dxcjpz_bbh", k)
            # 更新计划任务表状态为启用
            for dx in dx_lst:
                sql_data['dx_lst_id'] = dx['id']
                sql_data['dx_lst_ip'] = dx['zdzjip']
                sql_data['dx_lst_zdzjzt'] = dx['zdzjzt']
                sql_data['dx_lst_dxzt'] = dx['dxzt']
                # 获取计划任务表id
                jhrwid = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_jhrw_id", sql_data)
                if jhrwid:
                    jhrwid = jhrwid[0]['id']
                    # 3个状态为启用是才是启用，对象采集配置状态已经设置为启用，所以不需要判断对象采集配置状态了。
                    if sql_data['dx_lst_zdzjzt'] == '1' and sql_data['dx_lst_dxzt'] == '1':
                        sql_data['zt'] = '1'
                        # 更新计划任务表
                        ModSql.yw_jkgl_005.execute_sql(db, "update_jhrw_zt", sql_data)
                        ins_waitexec_task(jhrwid,db)
        elif zt == '0':
            if dxcjpzxx[0]['lx'] == '2':
                sql_data['wizt'] = wizt
                sql_data['dx_lst_id'] = []
                sql_data['dx_lst_ip'] = []
                for dx in dx_lst:
                    sql_data['dx_lst_id'].append(dx['id'])
                    sql_data['dx_lst_ip'].append(dx['zdzjip'])
                # 获取计划任务表状态为启用的数据
                jhrw = ModSql.yw_jkgl_005.execute_sql_dict(db, "get_jhrw_id_from_zt", sql_data)
                jhrw_lst = [jh['id'] for jh in jhrw]
                sql_data['jhrw_lst'] = jhrw_lst
                if len(jhrw_lst) > 0:
                    # 更新计划任务状态
                    ModSql.yw_jkgl_005.execute_sql(db, "update_jhrw_zts", sql_data)
                for l in jhrw_lst:
                    del_waitexec_task(l,db)
            # 更新对象采集配置表
            ModSql.yw_jkgl_005.execute_sql(db, "upate_dxcjpzxx_bbh", sql_data)
        rznr = '适用对象配置-状态%s：查询的%s' % (xx,dxcjpzxx)
        ins_czrz(db,rznr,'wh','适用对象-状态%s' % (xx))
    return data