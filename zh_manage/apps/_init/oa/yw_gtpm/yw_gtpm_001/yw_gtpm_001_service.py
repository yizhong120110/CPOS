# -*- coding: utf-8 -*-
# Action: 阈值校验 - 参数配置
# Author: luoss
# AddTime: 2015-05-04
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import pickle, os
from sjzhtspj.esb import memcache_data_del
from sjzhtspj import ModSql
from sjzhtspj.common import get_uuid, get_sess_hydm, get_strftime, ins_czrz, update_wym_yw

def cspz_service():
    # 初始化返回值
    data = { 'ssyw_lst': [{'id': '', 'ids': '请选择', 'ywbm': '','ywmc':''}], 'csdm_lst': [{'bm': '', 'bmmc': '请选择'}] }
    # 数据库链接
    with sjapi.connection() as db:
        # 执行所属业务、参数代码查询
        ssyw_list = ModSql.yw_gtpm_001.execute_sql_dict(db, "data_ywmc_rs")
        csdm_list = ModSql.yw_gtpm_001.execute_sql_dict(db, "data_csdm_rs")
        # 将所属业务、参数代码结果集中放置到集合中
        data['ssyw_lst'].extend(ssyw_list)
        data['csdm_lst'].extend(csdm_list)
        # 返回查询结果
        return data

def data_service( sql_data ):
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    # 清理为空的查询条件
    search_lst = [ 'csdm', 'ywid']
    for k in list(sql_data.keys()):
        if k in search_lst and sql_data[k] == '':
            del sql_data[k]
    # 数据库链接
    with sjapi.connection() as db:
        # 查询交易总条数
        total = ModSql.yw_gtpm_001.execute_sql(db, "data_count", sql_data)[0].count
        # 查询交易列表
        lbxx = ModSql.yw_gtpm_001.execute_sql_dict(db, "data_rs", sql_data)
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = lbxx
    # 将查询到的结果反馈给view
    return data

def search_service(data_dic):
    # 初始化返回值
    data = None
    # 数据库链接
    with sjapi.connection() as db:
        # 查询数据列表
        data = ModSql.yw_gtpm_001.execute_sql_dict(db, "update_search", data_dic)
    # 将查询到的结果反馈给view
    if data != []:
        return data[0]
    else:
        return None

def add_service(csdm, ywid, jksj, dbzdje, jyzq, jyyz, csms, cszt):
    """
    # 新增系统参数
    """
    sql_data = {'id': get_uuid(), 'ssywid': ywid, 'csdm': csdm, 'kgl': cszt, 'csz': None, 'csz2': None, 'csms': csms, 'czr': get_sess_hydm(), 'czsj': get_strftime()}
    with sjapi.connection() as db:
        # 校验系统参数是否存在
        count = ModSql.yw_gtpm_001.execute_sql(db, "check_yzjycspz",sql_data)[0].count
        if count != 0:
            msg = '参数代码[%s]已经在该业务下配置，请检查并重新选择'%(sql_data['csdm'])
            return {'state':False,'msg':msg}
        # 根据参数代码来选择性的给参数值赋值
        if csdm == 'YZJY_JK':
            sql_data['csz'] = jksj
            sql_data['csz2'] = ''
        elif csdm == 'YZJY_DBJE':
            sql_data['csz'] = dbzdje
            sql_data['csz2'] = ''
        elif csdm == 'YZJY_YZ':
            sql_data['csz'] = jyzq
            sql_data['csz2'] = jyyz
        elif csdm == 'YZJY_CFJE':
            sql_data['csz'] = ''
            sql_data['csz2'] = ''
        # 执行数据插入
        ModSql.yw_gtpm_001.execute_sql(db, "insert_ywjycspz", sql_data)
        # 根据传来的业务id和开关量的值来查询业务名称和开关量的名称
        jbxx_ssyw = ModSql.yw_gtpm_001.execute_sql(db, "update_select_ssyw", sql_data)
        jbxx_kgl = ModSql.yw_gtpm_001.execute_sql(db, "update_select_kgl", sql_data)
        # 为日志中的参数描述填写值
        csxx = None
        if sql_data['csdm'] == 'YZJY_JK':
            csxx =  '监控时间：[' + sql_data['csz'] + ']'
        elif sql_data['csdm'] == 'YZJY_DBJE':
            csxx =  '单笔最大金额：[' + sql_data['csz'] + ']'
        elif sql_data['csdm'] == 'YZJY_YZ':
            csxx =  '校验周期：[' + sql_data['csz'] + ']，校验阈值：['+  sql_data['csz2'] + ']'
        elif sql_data['csdm'] == 'YZJY_CFJE':
            csxx =  '[]'
        # 更新阈值校验参数配置表中的唯一码
        update_wym_yw( db, 'yzjycspz', sql_data['id'] )
        # 日志中的添加信息
        tjxx = '[所属业务名称[%s]，参数代码: [%s]，开关量:[%s]，参数信息: [%s]，参数描述:[%s]]'%(jbxx_ssyw[0]['ywmc'],sql_data['csdm'],jbxx_kgl[0]['mc'],csxx,sql_data['csms'])
        # 想日志中插入信息
        ins_czrz(db, '阈值校验_参数配置管理-添加：[%s]'%(tjxx), pt='wh', gnmc='阈值校验_参数配置管理-添加')
        return {'state':True,'msg':'新增成功'}

def update_service(csid, csdm, ywid, jksj, dbzdje, jyzq, jyyz, csms, cszt):
    """
    # 修改系统参数
    """
    with sjapi.connection() as db:
        sql_data = {'csid':csid, 'ssywid': ywid, 'csdm': csdm, 'kgl': cszt, 'csz': None, 'csz2': None, 'csms': csms, 'czr': get_sess_hydm(), 'czsj': get_strftime()}
        if csdm == 'YZJY_JK':
            sql_data['csz'] = jksj
            sql_data['csz2'] = ''
        elif csdm == 'YZJY_DBJE':
            sql_data['csz'] = dbzdje
            sql_data['csz2'] = ''
        elif csdm == 'YZJY_YZ':
            sql_data['csz'] = jyzq
            sql_data['csz2'] = jyyz
        elif csdm == 'YZJY_CFJE':
            sql_data['csz'] = ''
            sql_data['csz2'] = ''
        # 执行修改前数据的查询
        jbxx = ModSql.yw_gtpm_001.execute_sql(db, "update_select", sql_data)
        # 执行数据的修改
        ModSql.yw_gtpm_001.execute_sql(db, "update_ywjycspz", sql_data)
        # 查询修改后的所属业务名称
        jbxx_ssyw = ModSql.yw_gtpm_001.execute_sql(db, "update_select_ssyw", sql_data)
        # 查询修改前后的开关量的名称
        sql_jbxx = {'kgl': jbxx[0]['kgl']}
        jbxx_kgl_bjq = ModSql.yw_gtpm_001.execute_sql(db, "update_select_kgl", sql_jbxx)
        jbxx_kgl_bjh = ModSql.yw_gtpm_001.execute_sql(db, "update_select_kgl", sql_data)
        # 编辑前、后参数信息的赋值
        csxx_bjq  = None
        csxx_bjh  = None
        if sql_data['csdm'] == 'YZJY_JK':
            csxx_bjq =  '监控时间：[' + jbxx[0]['csz'] + ']'
            csxx_bjh =  '监控时间：[' + sql_data['csz'] + ']'
        elif sql_data['csdm'] == 'YZJY_DBJE':
            csxx_bjq =  '单笔最大金额：[%s]'%(jbxx[0]['csz'])
            csxx_bjh =  '单笔最大金额：[%s]'%(jbxx[0]['csz'])
        elif sql_data['csdm'] == 'YZJY_YZ':
            csxx_bjq =  '校验周期：[' + jbxx[0]['csz'] + ']，校验阈值：['+  jbxx[0]['csz2'] + ']'
            csxx_bjh =  '校验周期：[' + sql_data['csz'] + ']，校验阈值：['+  sql_data['csz2'] + ']'
        elif sql_data['csdm'] == 'YZJY_CFJE':
            csxx_bjq =  '[]'
            csxx_bjh =  '[]'
        # 更新阈值校验参数配置表中的唯一码
        update_wym_yw( db, 'yzjycspz', csid )
        # 编辑前的信息值
        bjq = '[业务：[%s]，参数代码：[%s]，开关量：[%s]，参数信息：[%s]'%(jbxx_ssyw[0]['ywmc'],jbxx[0]['csdm'],jbxx_kgl_bjq[0]['mc'],csxx_bjq)
        # 编辑后的信息值
        bjh = '[所属业务名称[%s]，参数代码: [%s]，开关量:[%s]，参数信息: [%s]，参数描述:[%s]]'%(jbxx_ssyw[0]['ywmc'],jbxx[0]['csdm'],jbxx_kgl_bjh[0]['mc'],csxx_bjh,jbxx[0]['csms'])
        # 执行修改信息日志的添加
        ins_czrz(db, '阈值校验_参数配置管理-编辑：编辑前：[%s]，编辑后：[%s]。'%(bjq,bjh), pt='wh', gnmc='阈值校验_参数配置管理-编辑')
        return {'state':True,'msg':'编辑成功'}

# 批量删除
def del_pl_service( csid ):
    """
    #删除信息
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}
    # 数据库链接
    with sjapi.connection() as db:
        # 阈值流水校验相关参数配置ID列表，状态为66、77、88
        ssywid_lst_mycl = []
        # 阈值流水校验相关参数配置ID列表，状态为12
        ssywid_lst_zbpk = []
        # 根据当前要删除信息的ID来查询当前信息的所属业务ID和参数代码
        ssyw_lst = ModSql.yw_gtpm_001.execute_sql_dict(db, "select_ssywid", {'id':csid.split(',')})
        ssyw_dic = {}
        for k in ssyw_lst:
            k['zt'] = ''
            if k['csdm'] == 'YZJY_CFJE':
                k['zt'] = '66'
            elif k['csdm'] == 'YZJY_DBJE':
                k['zt'] = '77'
            elif k['csdm'] == 'YZJY_YZ':
                k['zt'] = '88'
            if k['ssywid'] in ssyw_dic:
                ssyw_dic[k['ssywid']].extend([k['zt']])
            else:
                ssyw_dic.update({k['ssywid']:[k['zt']]})
                
        # 查询文件处理登记表中的数据，限制条件为：当前要删除信息的所属业务ID和参数代码-状态：66、77、88
        for k in ssyw_dic.items():
            data_count = ModSql.yw_gtpm_001.execute_sql(db, "select_wjcldjb", {'ssywid':k[0], 'zt':k[1]})[0].count
            if data_count > 0:
                ssywid_lst_mycl.append(k[0])

        # 初始化不可删除的所属业务ID列表和提示信息的标识
        check_ssywid_lst = []
        check_bz = ''
        if ssywid_lst_mycl:
            check_ssywid_lst = list(set(ssywid_lst_mycl))
            check_bz = 'msg_mycl'
        else:
            # 查询文件处理登记表中的数据，限制条件为：当前要删除信息的所属业务ID和参数代码-状态：12
            data_ssywid = ModSql.yw_gtpm_001.execute_sql_dict(db, "select_wjcldjb_ssywid", {'ssywid':list(ssyw_dic.keys()), 'zt':'12'})
            for k in data_ssywid:
                ssywid_lst_zbpk.append(k['ssywid'])
            check_ssywid_lst = ssywid_lst_zbpk
        
        # 当状态为66、77、88或者12时，对应的所属业务ID有值时，即进行消息提示
        if check_ssywid_lst:
            lb_lst = []
            ssyw_list = ModSql.yw_gtpm_001.execute_sql_dict(db, "data_ywmc_rs", {'ssywid':check_ssywid_lst})
            for k in ssyw_list:
                lb_lst.append(k['ids'])
            if check_bz == 'msg_mycl':
                data['msg'] = '阈值校验流水中存在%s未处理数据，请先处理后再进行删除'%(lb_lst)
            else:
                data['msg'] = '业务%s下有准备批扣的文件流水，请先处理后，再进行删除'%(lb_lst)
            return data

        sql_data = {'csid': csid.split(',')}
        # 查询该业务是否已经配置了阈值校验信息
        rs_jyxx  = ModSql.yw_gtpm_001.execute_sql_dict(db,"select_check_yw",sql_data)
        if rs_jyxx:
            glyw_lst = []
            for k in rs_jyxx:
                glyw_lst.append(k['ywmc']+'('+k['ywbm']+')')
            # 查询该业务的参数信息,获取业务名称
            return {'state':False, 'msg':'选中的参数已关联业务%s阈值校验配置，不可删除'%(glyw_lst)}

        # 删除信息日志查询
        rs_rzxx  = ModSql.yw_gtpm_001.execute_sql_dict(db,"select_rz",sql_data)
        rzxx_lst = []
        for k in rs_rzxx:
            # 多条信息删除时，日志信息的累加
            rzxx_lst.append('%s:%s(%s),'%(k['csdm'],k['ywmc'],k['ywbm']))
        # 删除当前信息
        rs_xxsc  = ModSql.yw_gtpm_001.execute_sql_dict(db,"delete_pl",sql_data)
        rzjl = '阈值校验_参数配置-删除参数：待删除参数信息：【%s】' % rzxx_lst
        # 删除信息日志记录
        ins_czrz(db, rzjl, pt='wh', gnmc='阈值校验_参数配置-删除参数')
    return {'state':True,'msg':'删除成功'}