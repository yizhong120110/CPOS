# -*- coding: utf-8 -*-
# Action: 响应动作管理
# Author: zhangzhf
# AddTime: 2015-04-15
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import pickle, traceback
from sjzhtspj import render_to_string,ModSql,get_sess_hydm,logger
from sjzhtspj.common import ins_czrz,get_strftime,py_check,get_uuid,check_jyhs,get_hscs,update_wym_yw
from sjzhtspj.esb import memcache_data_del


def index_service():
    """
    # 获取监控管理-监控对象管理的对象类型，对象状态
    """
    # 数据结构    
    data = { 'dmlx':[{'bm':'','mc':'请选择'}], 'dxzt':[{'bm':'','mc':'请选择'}], 'dxly':[{'bm':'','mc':'请选择'}] }
    # 数据库链接
    with sjapi.connection() as db:
        # 获取代码类型
        dmlx = ModSql.yw_jkgl_004.execute_sql_dict(db, "get_bmwh", {'lx':'10008'})
        # 查询对象状态
        dxzt = ModSql.yw_jkgl_004.execute_sql_dict(db, "get_bmwh", {'lx':'10001'})
        # 查询对象来源
        dxly = ModSql.yw_jkgl_004.execute_sql_dict(db, "get_bmwh", {'lx':'10017'})
        # 将查询结果放到结果集中
        data['dmlx'].extend(dmlx)
        data['dxzt'].extend(dxzt)
        data['dxly'].extend(dxly)
    return data
    
def data_service(sql_data):
    """
    # 获取响应动作管理列表数据
    """
    # 数据结构
    data = {'total':0, 'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询对象来源
        dxly = ModSql.yw_jkgl_004.execute_sql_dict(db, "get_bmwh", {'lx':'10017'})
        # 查询响应动作的条数
        count = ModSql.yw_jkgl_004.execute_sql(db, "get_xydz_count", sql_data)[0].count
        # 查询响应动作
        jkdx = ModSql.yw_jkgl_004.execute_sql_dict(db, "get_xydz", sql_data)
        if len(dxly) > 0:
            ly_dic = {k['bm']:k['mc'] for k in dxly}
            # 循环对应来源
            for j in jkdx:
                j['lymc'] = ly_dic.get(j['ly'])
        # 将查询结果放到结果集中
        data['total'] = count
        data['rows'] = jkdx
    return data

def add_service(sql_data):
    """
    # 添加响应动作
    """
    sql_data['zt'] = '1' if sql_data['zt'] == 'on' else '0'
    if sql_data['dmlx'] == '1':
        try:
            # 校验函数名校验
            exec("def " + sql_data['hsmc'] + ":pass")
        except:
            return {'state':False, 'msg' : "函数名称["+sql_data['hsmc']+"]不正确：" + traceback.format_exc()}
        # 校验函数内容的合法性
        check_hsnr = "def " + sql_data['hsmc'] + ":\n" + sql_data['nodeBox']
        check_hsnr = check_hsnr.replace( '\n', '\n    ' )
        str_check = py_check( check_hsnr )
        if str_check != '':
            return {'state':False, 'msg' : "函数内容有语法错误：\n" + str_check} 
    # 数据结构
    data = {'state':True, 'msg':'新增成功'}
    # 数据库链接
    with sjapi.connection() as db:
        # 调用公共函数check_jyhs校验函数名称在数据库中是否存在
        num = check_jyhs(sql_data['hsmc'],'gl_hsxxb',{'lb':'dz'},db)
        if num > 0:
            data['state'] = False
            data['msg'] = "动作函数名称[%s]已经存在，请重新输入" % (sql_data['hsmc'].split('(')[0])
            return data
        # 调用公共函数get_hscs获取函数名称中的参数信息并校验参数中是否有单‘*’的可变数量参数
        fhxx_lst = get_hscs(sql_data['hsmc'])
        # 注：fhxx_lst 格式为[True,[(csdm1,是否可空True/False,默认值),(csdm2,是否可空,默认值)],message]
        if fhxx_lst[0] == False:
            data['state'] = False
            data['msg'] = fhxx_lst[2]
            return data
        # 校验中文名称是否重复
        count = ModSql.yw_jkgl_004.execute_sql(db, "check_zwmc", sql_data)[0].count
        if count > 0:
            data['state'] = False
            data['msg'] = '中文名称[%s]已经存在，请重新输入' % (sql_data['zwmc'])
            return data
        # blob表的id
        blob_id = get_uuid()
        # 将函数信息插入blob
        ModSql.yw_jkgl_004.execute_sql(db, "insert_blob", {'id':blob_id,'lx':'gl_hsxx','czr':sql_data['czr'],'czsj':sql_data['czsj'],'nr':pickle.dumps(sql_data['nodeBox'])})
        # 插入函数信息表
        sql_data['lb'] = 'dz'
        sql_data['nr_id'] = blob_id
        ModSql.yw_jkgl_004.execute_sql(db, "insert_hsxxb", sql_data)
        # 将fhxx_lst[1]中的参数代码循环插入到数据表中
        xx_index = 0
        for xx in fhxx_lst[1]:
            xx_index=xx_index+1
            ModSql.yw_jkgl_004.execute_sql(db, "insert_crcs", {'id':get_uuid(),'csdm':xx[0],'cssm':'','sslb':'2','ssid':sql_data['id'],'sxh':xx_index,'sfkk':str(xx[1]),'mrz':xx[2]})
        # 更新函数信息表（响应动作）中唯一码
        update_wym_yw( db, 'xydzgl', sql_data['id'] )
        ri_data = {'hsmc':sql_data['hsmc'],'zwmc':sql_data['zwmc'], 'dmlx':sql_data['dmlx'] ,'zt':sql_data['zt'], 'ms':sql_data['ms']}
        # 登记操作日志
        rznr = '新增响应动作：动作函数名称【%(hsmc)s】，中文名称【%(zwmc)s】，类型【%(dmlx)s】，状态【%(zt)s】,动作描述【%(ms)s】' % ri_data
        ins_czrz(db,rznr,'wh','响应动作管理-添加')
    return data
    
def edit_service(sql_data):
    """
    # 编辑响应动作
    """
    if sql_data['dmlx'] == '1':
        try:
            # 校验函数名校验
            exec("def " + sql_data['hsmc'] + ":pass")
        except:
            return {'state':False, 'msg' : "函数名称["+sql_data['hsmc']+"]不正确：\n" + traceback.format_exc()}
        # 校验函数内容的合法性
        check_hsnr = "def " + sql_data['hsmc'] + ":\n" + sql_data['nodeBox']
        check_hsnr = check_hsnr.replace( '\n', '\n    ' )
        str_check = py_check( check_hsnr )
        if str_check != '':
            return {'state':False, 'msg' : "函数内容有语法错误：\n" + str_check} 
    # 数据结构
    data = {'state':True, 'msg':'编辑成功'}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询未修改之前的内容
        old_data = ModSql.yw_jkgl_004.execute_sql_dict(db, "get_oldxydz", {'id':sql_data['id']})[0]
        # 调用公共函数check_jyhs校验函数名称在数据库中是否存在
        num = check_jyhs(sql_data['hsmc'],'gl_hsxxb',{'lb':'dz', 'xydzid':sql_data['id']},db)
        if num > 0:
            data['state'] = False
            data['msg'] = "动作函数名称[%s]已经存在，请重新输入" % (sql_data['hsmc'].split('(')[0])
            return data
        # 校验中文名称是否重复
        count = ModSql.yw_jkgl_004.execute_sql(db, "check_zwmc", sql_data)[0].count
        if count > 0:
            data['state'] = False
            data['msg'] = '中文名称[%s]已经存在，请重新输入' % (sql_data['zwmc'])
            return data
        # 调用公共函数get_hscs获取函数名称中的参数信息并校验参数中是否有单‘*’的可变数量参数
        fhxx_lst = get_hscs(sql_data['hsmc'])
        # 注：fhxx_lst 格式为[True,[(csdm1,是否可空True/False,默认值),(csdm2,是否可空,默认值)],message]
        if fhxx_lst[0] == False:
            data['state'] = False
            data['msg'] = fhxx_lst[2]
            return data
        else:
            # 记录当前的的参数list
            cs_lst = []
            # 循环参数列表，将传入参数表中此响应动作的传入参数全部删除，再将fhxx_lst[1]中的参数代码循环插入到数据表中
            xx_index = 0
            for xx in fhxx_lst[1]:
                xx_index=xx_index+1
                # 查询参数说明
                cssm_tmp = ModSql.yw_jkgl_004.execute_sql_dict(db, "get_cssm", {'id':sql_data['id'], 'csdm':xx[0]})
                if len(cssm_tmp) > 0:
                    # 更新传入参数
                    ModSql.yw_jkgl_003.execute_sql(db, "update_crcs", {'csdm':xx[0],'ssid':sql_data['id'],'sxh':xx_index,'sfkk':str(xx[1]),'mrz':xx[2]})
                else:
                    # 插入传入参数
                    ModSql.yw_jkgl_003.execute_sql(db, "insert_crcs", {'id':get_uuid(),'csdm':xx[0],'cssm':'','sslb':'2','ssid':sql_data['id'],'sxh':xx_index,'sfkk':str(xx[1]),'mrz':xx[2]})
                cs_lst.append(('csdm',xx[0]))
            # 将没有用到的参数进行删除
            if len(cs_lst):
                ModSql.yw_jkgl_004.execute_sql(db, "del_crcs_not", {'id':sql_data['id'], 'csdm':cs_lst})
            else:
                # 将现有的参数信息全部删除
                ModSql.yw_jkgl_003.execute_sql(db, "del_crcs_all", {'id':sql_data['id']})
        # 将函数信息更新到blob
        ModSql.yw_jkgl_004.execute_sql(db, "edit_blob", {'nr_id':sql_data['nr_id'],'czr':sql_data['czr'],'czsj':sql_data['czsj'],'nr':pickle.dumps(sql_data['nodeBox'])})
        # 更新函数信息表
        ModSql.yw_jkgl_004.execute_sql(db, "edit_hsxxb", sql_data)
        # 更新函数信息表（响应动作）中唯一码
        update_wym_yw( db, 'xydzgl', sql_data['id'] )
        # 删除缓存
        memcache_data_del( [sql_data['id']] )
        # 登记操作日志
        ri_data = {'old_data':str(old_data), 'hsmc':sql_data['hsmc'], 'zwmc':sql_data['zwmc'], 'dmlx':sql_data['dmlx'], 'zt':old_data['zt'], 'ms':sql_data['ms']}
        rznr = '编辑响应动作，原始数据[%(old_data)s]，更新后数据：动作函数名称【%(hsmc)s】，中文名称【%(zwmc)s】，类型【%(dmlx)s】，状态【%(zt)s】,动作描述【%(ms)s】' % ri_data
        ins_czrz(db,rznr,'wh','响应动作管理-编辑')
    return data

def crcs_data_service(sql_data):
    """
    # 获取传入参数列表数据
    """
    # 数据结构
    data = {'total':0, 'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询传入参数的条数
        count = ModSql.yw_jkgl_004.execute_sql(db, "get_crcs_count", sql_data)[0].count
        # 查询传入参数
        crcs = ModSql.yw_jkgl_004.execute_sql_dict(db, "get_crcs", sql_data)
        # 将查询结果放到结果集中
        data['total'] = count
        data['rows'] = crcs
    return data

def del_service(ids):
    """
    # 删除响应动作
    """
    # 数据结构
    data = {'state':True, 'msg':'删除成功'}
    # 数据库链接
    with sjapi.connection() as db:
        # 响应动作id列表
        ids_lst = ids.split(',')
        # 获取响应动作
        zwmc = ModSql.yw_jkgl_004.execute_sql_dict(db, "get_zwmc", {'ids':ids_lst})
        # 响应动作列表[响应动作1，响应动作2]
        zwmclb = [dx['zwmc'] for dx in zwmc]
        if len(zwmclb) > 0:
            data['state'] = False
            data['msg'] = '响应动作%s已配置监控分析，请取消分析配置后再进行删除' % (str(zwmclb))
            return data
        # 查询要删除的函数信息
        scdz_lst = ModSql.yw_jkgl_004.execute_sql_dict(db, "get_del_hsxx", {'ids':ids_lst})
        nr_lst = [dx['nr_id'] for dx in scdz_lst]
        # 删除函数信息表中信息
        ModSql.yw_jkgl_004.execute_sql(db, "del_hsxx", {'ids':ids_lst})
        # 删除blob表中信息
        ModSql.yw_jkgl_004.execute_sql(db, "del_blob", {'nr_ids':nr_lst})
        # 删除blob表中信息
        ModSql.yw_jkgl_004.execute_sql(db, "del_crcss", {'ids':ids_lst})
        # 调用核心接口memcache_data_del将缓存中的响应动作信息清除
        for uuid in ids_lst:
            memcache_data_del( [uuid] )
        # 登记操作日志
        rznr = '删除响应动作：%s' % (str(scdz_lst))
        ins_czrz(db,rznr,'wh','响应动作管理-删除')
    return data
    
def able_service(ids,zt):
    """
    # 启用禁用监控管理-响应动作
    """
    xx = '启用' if zt == '1' else '禁用'
    wizt = '0' if zt == '1' else '1'
    # 数据结构
    data = {'state':True, 'msg':xx+'成功'}
    # 数据库链接
    with sjapi.connection() as db:
        # 监控对象id列表
        ids_lst = ids.split(',')
        # 获取响应动作ID列表对应的响应动作信息，用于登记日常运维流水
        qydz_lst = ModSql.yw_jkgl_004.execute_sql_dict(db, "get_del_hsxx", {'ids':ids_lst})
        # 获取需要启用的函数信息id
        hsxx_ids = ModSql.yw_jkgl_004.execute_sql_dict(db, "get_hsxx_able", {'ids':ids_lst,'zt':wizt})
        lst =  [dx['id'] for dx in hsxx_ids]
        if len(lst) < 1:
            data['state'] = False
            data['msg'] = '选择的列表中的状态都为%s，无需再设。' % (xx)
            return data
        # 更新响应动作信息
        ModSql.yw_jkgl_004.execute_sql(db, "edit_hsxx_zt", {'ids':lst,'zt':zt})
        # 更新函数信息表（响应动作）中的唯一码
        for id in lst:
            update_wym_yw(db, 'xydzgl', id)
            # 调用核心接口memcache_data_del将缓存中的响应动作信息清除
            memcache_data_del( [id] )
        ins_czrz(db,'设置响应动作状态为%s：【%s】' % (xx,str(qydz_lst)),'wh','响应动作管理-状态%s' % (xx))
    return data
def crcs_edit_service(sql_data):
    """
    # 编辑传入参数
    """
    # 数据结构
    data = {'state':True, 'msg':'编辑成功'}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询未修改前的传入参数
        old_data = ModSql.yw_jkgl_004.execute_sql_dict(db, "get_crcs", sql_data)[0]
        # 查询传入参数的条数
        ModSql.yw_jkgl_004.execute_sql(db, "edit_crcs", sql_data)
        # 更新函数信息表（响应动作）中的唯一码
        update_wym_yw(db, 'xydzgl', old_data['ssid'])
        ri_data = {'csdm':sql_data['csdm'], 'old_data':str(old_data), 'cssm':sql_data['cssm']}
        # 登记操作日志
        rznr = '编辑传入参数[%(csdm)s]：原参数说明[%(old_data)s]，更新后参数说明[%(cssm)s]' % ri_data
        ins_czrz(db,rznr,'wh','传入参数-编辑。')
    return data
    
def get_dmlx_service():
    """
    # 获取代码类型
    """
    # 数据结构
    data = {'state':True, 'msg':'','list':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 获取代码
        dmlx = ModSql.yw_jkgl_004.execute_sql_dict(db, "get_bmwh", {'lx':'10008'})
        data['list'].extend(dmlx)
    return data
    
def get_xydz_service(id):
    """
    # 获取需要编辑的响应动作的属性
    """
    # 数据结构
    data = {'state':True, 'msg':'','xydz':{}}
    # 数据库链接
    with sjapi.connection() as db:
        # 获取对象属性
        data['xydz'] = ModSql.yw_jkgl_004.execute_sql_dict(db, "get_xydz_edit", {'id':id})[0]
        if data['xydz']:
            if data['xydz']['nr']:
                data['xydz']['nr'] = pickle.loads(data['xydz']['nr'].read())
            else:
                data['xydz']['nr'] = ''
        # 判断响应动作是否被使用了。
        count = ModSql.yw_jkgl_004.execute_sql(db, "get_dz_count", {'dzid':id})[0].count
        if count > 0:
            data['flag'] = True
    return data