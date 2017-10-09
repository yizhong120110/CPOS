# -*- coding: utf-8 -*-
# Action: 阈值校验业务配置
# Author: kongdq
# AddTime: 2015-04-28
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql,get_sess_hydm
from sjzhtspj.common import py_check, get_uuid,get_strftime,ins_czrz,update_wym_yw,get_bmwh_bm
import pickle

def data_service( sql_data ):
    """
    # 业务参数管理列表json数据 service
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询业务总条数
        total = ModSql.yw_gtpm_002.execute_sql(db, "data_count",sql_data)[0].count
        # 查询业务列表
        tmp = ModSql.yw_gtpm_002.execute_sql_dict(db, "data_htcx",sql_data)
        # 将总条数放到结果集中
        data['total'] = total
        # 将查询详情结果放到结果集中
        data['rows'] = tmp
    
    # 将查询到的结果反馈给view
    return data

def ssyw_service():
    """
    # 业务参数管理列表json数据 service
    """
    # 初始化反馈前台信息
    data = { 'ssyw_lst': [],'kzjyfs_lst':[] }

     # 数据库链接
    with sjapi.connection() as db:
        # 查询业务列表
        ssyw_lst = ModSql.yw_gtpm_002.execute_sql_dict(db, "data_ssyw")
        kzjyfs_lst = ModSql.yw_gtpm_002.execute_sql_dict(db, "data_kzjyfs")
        # 追加请选择选项
        ssyw_lst.insert( 0, {'value': '', 'ms': '', 'text': '请选择'} )
        kzjyfs_lst.insert(0,{'value':'','ms':'','text':'请选择'})
        # 将结果放到返回值中
        data['ssyw_lst'] = ssyw_lst
        data['kzjyfs_lst'] = kzjyfs_lst

    # 将查询到的结果反馈给view
    return data

#新增 服务
def add_service( sql_data ):
    """
    #查询数据库，若已存在，则返回 ‘该业务的阈值配置已经存在，请重新修改录入’
    """
    # 初始化返回值
    data = {'state':False, 'msg':""}

    # 数据库链接
    with sjapi.connection() as db:
        # 校验是否重复
        sql_para = {'ssyw':sql_data['ssyw']}
        total = ModSql.yw_gtpm_002.execute_sql(db,"data_jysfcf",sql_para)[0].num

        if total>0:
            #已存在重复，则返回错误信息
            data['msg'] = '该业务的阈值配置已经存在，请重新修改录入'
            return data

        #若扩展校验方式为模块代码，则校验代码合法性
        if sql_data['kzjyfs']=='MOD':
            # 校验函数内容的合法性
            check_hsnr = "def check_gs():\n" + sql_data['kzjyCode']
            check_hsnr = check_hsnr.replace( '\n', '\n    ' )
            str_check = py_check( check_hsnr )
            if str_check != '':
                return {'state':False, 'msg' : "扩展校验模块代码有语法错误：\n" + str_check, 'msg_show' : 'kzjy'}


        #若流水导入方式为模块代码，则校验代码合法性
        if sql_data['lsjyfs']=='MOD':
            # 校验函数内容的合法性
            check_hsnr = "def check_gs():\n" + sql_data['lsjyCode']
            check_hsnr = check_hsnr.replace( '\n', '\n    ' )
            str_check = py_check( check_hsnr )
            if str_check != '':
                return {'state':False, 'msg' : "流水导入模块代码有语法错误：\n" + str_check, 'msg_show' : 'lsdr'}

        #校验成功后插入数据库

        #所属业务
        ssyw = sql_data['ssyw']
        #文件类型
        wjlx = sql_data['wjlx']
        #阈值校验配置表_UUID
        yzjypz_id = get_uuid()
        #扩展校验方式
        kzjyfs = sql_data['kzjyfs']
        #流水导入方式
        lsdrfs = sql_data['lsjyfs']
        # 扣款明细金额sqlID:后台生成uuid.
        kkmxsqlid = get_uuid()
        # 流水导入ID：后台生成uuid.
        lsdrid = get_uuid()
        # 扩展校验ID：后台生成uuid.
        kzjyid = get_uuid()
        # 扣款明细数据查询sqlID:后台生成uuid.
        kkmxcxsqlid = get_uuid()
        # 异常全部通过sqlID：后台生成uuid.
        ycqbtgsqlid = get_uuid()
        # 异常全部撤销sqlID：后台生成uuid.
        ycqbcxsqlid = get_uuid()
        # 异常单笔状态更新sqlID：后台生成uuid.
        ycdbztgxsqlid = get_uuid()
        # 操作人：当前登录人
        czr = get_sess_hydm()
        # 操作时间：当前系统时间
        czsj = get_strftime()
        #插入阈值校验配置表
        sql_para = {'yzjypz_id':yzjypz_id,'ssyw':ssyw,'wjlx':wjlx,
                    'kkmxsqlid':kkmxsqlid,'lsdrfs':lsdrfs,'lsdrid':lsdrid,'kzjyfs':kzjyfs,
                    'kzjyid':kzjyid,'kkmxcxsqlid':kkmxcxsqlid,'ycqbtgsqlid':ycqbtgsqlid,
                    'ycqbcxsqlid':ycqbcxsqlid,'ycdbztgxsqlid':ycdbztgxsqlid,'czr':czr,'czsj':czsj
                    }
        ModSql.yw_gtpm_002.execute_sql_dict(db,"data_yzjypz_insert",sql_para)
        # 插入到blob表-扣款明细金额sql
        kkmxsql = pickle.dumps(sql_data['kkmxsql'])
        sql_para = {'id':kkmxsqlid,'lx':'gl_yzjypz','czr':czr,'czsj':czsj,'nr':kkmxsql}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_insert",sql_para)
        # 插入到blob表-流水导入信息
        lsdrnr = pickle.dumps(sql_data['lsdrnr'])
        sql_para = {'id':lsdrid,'lx':'gl_yzjypz','czr':czr,'czsj':czsj,'nr':lsdrnr}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_insert",sql_para)
        # 插入到blob表-扩展校验信息
        kzjynr = pickle.dumps(sql_data['kzjynr'])
        sql_para = {'id':kzjyid,'lx':'gl_yzjypz','czr':czr,'czsj':czsj,'nr':kzjynr}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_insert",sql_para)
        # 插入到blob表-扣款明细数据查询信息
        kkmxcx = pickle.dumps(sql_data['kkmxcx'])
        sql_para = {'id':kkmxcxsqlid,'lx':'gl_yzjypz','czr':czr,'czsj':czsj,'nr':kkmxcx}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_insert",sql_para)
        # 插入到blob表-异常全部通过sql信息
        ycqbtg = pickle.dumps(sql_data['ycqbtg'])
        sql_para = {'id':ycqbtgsqlid,'lx':'gl_yzjypz','czr':czr,'czsj':czsj,'nr':ycqbtg}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_insert",sql_para)
        # 插入到blob表-异常全部撤销sql信息
        ycqbcx = pickle.dumps(sql_data['ycqbcx'])
        sql_para = {'id':ycqbcxsqlid,'lx':'gl_yzjypz','czr':czr,'czsj':czsj,'nr':ycqbcx}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_insert",sql_para)
        # 插入到blob表-异常单笔状态更新sql信息
        ycdbztgx= pickle.dumps(sql_data['ycdbztgx'])
        sql_para = {'id':ycdbztgxsqlid,'lx':'gl_yzjypz','czr':czr,'czsj':czsj,'nr':ycdbztgx}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_insert",sql_para)
        
        # 所属业务名称查询
        ssyw_lst = ModSql.yw_gtpm_002.execute_sql_dict(db, "data_ssyw",{'ssyw':ssyw})
        # 更新阈值校验配置表中的唯一码
        update_wym_yw( db, 'yzjypz', yzjypz_id )
        
        #登记操作日志
        kzjyfs_r = '模块代码' if kzjyfs == 'MOD' else 'SQL'
        lsdrfs_r = '模块代码' if lsdrfs == 'MOD' else 'SQL'
        rznr = '阈值校验_业务配置管理-添加：所属业务名称['+ssyw_lst[0]['ywmc']+']，文件类型: ['+wjlx+']，扩展校验方式:['+ kzjyfs_r +']，流水导入方式: ['+lsdrfs_r+']'
        ins_czrz(db,rznr,'wh','阈值校验_业务配置管理-添加')
        
        #成功后返回成功信息
        data['msg'] = '新增记录成功'
        data['state'] = True
    # 将查询到的结果反馈给view
    return data

#更新 服务
def update_service( sql_data ):
    """
    #更新数据库信息
    """
    # 初始化返回值
    data = {'state':False, 'msg':""}
    # 数据库链接
    with sjapi.connection() as db:
        #若扩展校验方式为模块代码，则校验代码合法性
        if sql_data['kzjyfs']=='MOD':
            # 校验函数内容的合法性
            check_hsnr = "def check_gs():\n" + sql_data['kzjyCode']
            check_hsnr = check_hsnr.replace( '\n', '\n    ' )
            str_check = py_check( check_hsnr )
            if str_check != '':
                return {'state':False, 'msg' : "扩展校验模块代码有语法错误：\n" + str_check, 'msg_show' : 'kzjy'}

        #若流水导入方式为模块代码，则校验代码合法性
        if sql_data['lsjyfs']=='MOD':
            # 校验函数内容的合法性
            check_hsnr = "def check_gs():\n" + sql_data['lsjyCode']
            check_hsnr = check_hsnr.replace( '\n', '\n    ' )
            str_check = py_check( check_hsnr )
            if str_check != '':
                return {'state':False, 'msg' : "流水导入模块代码有语法错误：\n" + str_check, 'msg_show' : 'lsdr'}

        #校验成功后更新数据库
        #业务配置id
        ywpz_id = sql_data['id']
        #所属业务 业务名称
        ywmc = sql_data['ywmc']
        #文件类型
        wjlx = sql_data['wjlx']
        #扩展校验方式
        kzjyfs = sql_data['kzjyfs']
        #流水导入方式
        lsdrfs = sql_data['lsjyfs']
        # 操作人：当前登录人
        czr = get_sess_hydm()
        # 操作时间：当前系统时间
        czsj = get_strftime()
        #更新阈值校验配置表
        sql_para = {'ywpz_id':ywpz_id,'wjlx':wjlx,
                    'lsdrfs':lsdrfs,'kzjyfs':kzjyfs,'czr':czr,'czsj':czsj
                    }
        ModSql.yw_gtpm_002.execute_sql_dict(db,"yzjypz_update",sql_para)
        # 更新到blob表-扣款明细金额sql
        kkmxsql = pickle.dumps(sql_data['kkmxsql'])
        sql_para = {'ywpz_id':ywpz_id,'sqlid_name':['kkmxsqlid'],'czr':czr,'czsj':czsj,'nr':kkmxsql}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_update",sql_para)
        # 更新到blob表-流水导入信息
        lsdrnr = pickle.dumps(sql_data['lsdrnr'])
        sql_para = {'ywpz_id':ywpz_id,'sqlid_name':['lsdrid'],'czr':czr,'czsj':czsj,'nr':lsdrnr}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_update",sql_para)
        # 更新到blob表-扩展校验信息
        kzjynr = pickle.dumps(sql_data['kzjynr'])
        sql_para = {'ywpz_id':ywpz_id,'sqlid_name':['kzjyid'],'czr':czr,'czsj':czsj,'nr':kzjynr}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_update",sql_para)
        # 更新到blob表-扣款明细数据查询信息
        kkmxcx = pickle.dumps(sql_data['kkmxcx'])
        sql_para = {'ywpz_id':ywpz_id,'sqlid_name':['kkmxcxsqlid'],'czr':czr,'czsj':czsj,'nr':kkmxcx}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_update",sql_para)
        # 更新到blob表-异常全部通过sql信息
        ycqbtg = pickle.dumps(sql_data['ycqbtg'])
        sql_para = {'ywpz_id':ywpz_id,'sqlid_name':['YC_ALLPASS_SQLID'],'czr':czr,'czsj':czsj,'nr':ycqbtg}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_update",sql_para)
        # 更新到blob表-异常全部撤销sql信息
        ycqbcx = pickle.dumps(sql_data['ycqbcx'])
        sql_para = {'ywpz_id':ywpz_id,'sqlid_name':['YC_ALLCANCEL_SQLID'],'czr':czr,'czsj':czsj,'nr':ycqbcx}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_update",sql_para)
        # 更新到blob表-异常单笔状态更新sql信息
        ycdbztgx= pickle.dumps(sql_data['ycdbztgx'])
        sql_para = {'ywpz_id':ywpz_id,'sqlid_name':['YC_SINGLE_SQLID'],'czr':czr,'czsj':czsj,'nr':ycdbztgx}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_update",sql_para)
        # 原信息列表
        yxxlb = sql_data['yxxlb']
        # 更新阈值校验配置表中的唯一码
        update_wym_yw( db, 'yzjypz', ywpz_id )
        
        #登记操作日志 [原信息列表]，编辑后：[所属业务名称[xxxx]，文件类型: [xxxx]，扩展校验方式:[xxxx]，流水导入方式:[xxxx]]
        # 所属业务名称查询
        ssyw_lst = ModSql.yw_gtpm_002.execute_sql_dict(db, "select_ywmc",{'id':sql_data['id']})
        kzjyfs_r = '模块代码' if kzjyfs == 'MOD' else 'SQL'
        lsdrfs_r = '模块代码' if lsdrfs == 'MOD' else 'SQL'
        rznr = '阈值校验_业务配置管理-编辑：编辑前：'+ yxxlb +'，编辑后：所属业务名称['+ssyw_lst[0]['ywmc']+']，文件类型: ['+wjlx+']，扩展校验方式:['+ kzjyfs_r+']，流水导入方式: ['+lsdrfs_r+']'
        ins_czrz(db,rznr,'wh','阈值校验_参数配置管理-编辑')

        #成功后返回成功信息
        data['msg'] = '更新记录成功'
        data['state'] = True
    # 将查询到的结果反馈给view
    return data

def cx_ywpz_service(sql_data):
    """
    # 查询业务配置数据
    """
    # 初始化反馈前台信息
    data = {  }

     # 数据库链接
    with sjapi.connection() as db:
        # 查询业务列表
        yw_lst = ModSql.yw_gtpm_002.execute_sql_dict(db, "data_ssyw")
        fs_lst = ModSql.yw_gtpm_002.execute_sql_dict(db, "data_kzjyfs")
        yw_dict ={}
        fs_dict ={}
        for y in yw_lst:
            yw_dict[y['value']] = y['text']
        for y in fs_lst:
            fs_dict[y['value']] = y['text']
        #业务配置基本信息查询
        sql_para = {'ywpz_id':sql_data['ywpz_id']}
        nr = ModSql.yw_gtpm_002.execute_sql_dict(db, "yzjypz_select",sql_para)[0]
        ssyw = nr['ssywid']
        wjlx = nr['wjlx']
        lsdrfs = nr['lsdrfs']
        kzjyfs = nr['kzjyfs']
        #原信息列表所需字段
        ywmc = yw_dict[ssyw]
        #若扩展校验方式为空，则置为空
        if kzjyfs=='' or kzjyfs == None:
            kzjyfs_mc=''
        else:
            kzjyfs_mc = fs_dict[kzjyfs]
        lsdrfs_mc = fs_dict[lsdrfs]
        # sqlid list
        sqlid_name_lst = ['kkmxsqlid','kkmxcxsqlid','kzjyid','lsdrid','YC_ALLPASS_SQLID','YC_ALLCANCEL_SQLID','YC_SINGLE_SQLID']

        for sqlid_name in sqlid_name_lst:
            sql_para = {'ywpz_id':sql_data['ywpz_id'],'sqlid_name':[sqlid_name]}
            nr = ModSql.yw_gtpm_002.execute_sql_dict(db, "blob_select",sql_para)[0]
            sql_nr = pickle.loads(nr['nr'].read())
            data[sqlid_name] = sql_nr

        # 将结果放到返回值中
        data['ssyw'] = ssyw
        data['ywmc'] = ywmc
        data['wjlx'] = wjlx
        data['lsdrfs'] = lsdrfs
        data['kzjyfs'] = kzjyfs

        # 原信息列表：[{所属业务：业务名称字典.get(所属业务ID)，文件类型：文件类型，
        #               流水导入方式：模块执行方式字典.get(流水导入方式)，扩展校验方式：
        #               模块执行方式字典.get(扩展校验方式)}]
        yxxlb = "[{所属业务："+ywmc+"，文件类型："+wjlx+"，流水导入方式："+lsdrfs_mc+"，扩展校验方式："+kzjyfs_mc+"}]"
        data['yxxlb'] = yxxlb

    # 将查询到的结果反馈给view
    return data

#删除 服务
def delete_service( sql_data ):
    """
    #删除业务配置ID表对应记录
    """
    # 初始化返回值
    data = {'state':False, 'msg':""}
    #业务配置ID列表
    ids = sql_data['ids'].split(',')
    sql_para = { 'ids':ids}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询当前编码维护表中类型为10019的状态列表中值
        zt_lst = [ k['value'] for k in get_bmwh_bm( '10019', db=db ) ]
        # 业务配置信息所属ID列表
        ywpz_ssywid_lst = []
        # 根据前台传来的ID列表来查询当前业务配置的所属业务ID
        ywpz_ssywid = ModSql.yw_gtpm_002.execute_sql_dict(db, "select_yzjypz_ssywid", { 'id': ids } )
        # 循环查询文件处理登记表中所属业务ID跟当前业务配置的所属业务ID一致的且在阈值流水校验中显示的数据-即状态值在zt_lst中
        for k in ywpz_ssywid:
            data_count = ModSql.yw_gtpm_001.execute_sql(db, "select_wjcldjb", {'ssywid':k['ssywid'], 'zt':zt_lst})[0].count
            if data_count > 0:
                ywpz_ssywid_lst.append(k['ssywid'])
        # 不可删除的所属业务ID列表数据
        if ywpz_ssywid_lst:
            lb_lst = []
            ssyw_list = ModSql.yw_gtpm_001.execute_sql_dict(db, "data_ywmc_rs", {'ssywid':ywpz_ssywid_lst})
            for k in ssyw_list:
                lb_lst.append(k['ids'])
            data['msg'] = '阈值校验流水中存在%s未处理数据，请先处理后再进行删除'%(lb_lst)
            return data

        #查询阈值校验参数配置
        rs  = ModSql.yw_gtpm_002.execute_sql_dict(db,"del_select",sql_para)
        tmp = []
        #拼操作日志中的字符列表: 业务名称（业务编码）：文件类型
        for r in rs:
            tmp.append(r['ywmc']+'('+r['ywbm']+'):'+r['wjlx'])

        #删除记录阈值校验配置表
        sql_para = {'ids':ids}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"yzjycspz_delete",sql_para)

        # 删除记录到blob表-扣款明细金额sql
        sql_para = {'ids':ids,'sqlid_name':['kkmxsqlid']}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_delete",sql_para)

        # 删除记录到blob表-流水导入信息
        sql_para = {'ids':ids,'sqlid_name':['lsdrid']}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_delete",sql_para)

        # 删除记录到blob表-扩展校验信息
        sql_para = {'ids':ids,'sqlid_name':['kzjyid']}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_delete",sql_para)

        # 删除记录到blob表-扣款明细数据查询信息
        sql_para = {'ids':ids,'sqlid_name':['kkmxcxsqlid']}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_delete",sql_para)

        # 删除记录到blob表-异常全部通过sql信息
        sql_para = {'ids':ids,'sqlid_name':['YC_ALLPASS_SQLID']}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_delete",sql_para)

        # 删除记录到blob表-异常全部撤销sql信息
        sql_para = {'ids':ids,'sqlid_name':['YC_ALLCANCEL_SQLID']}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_delete",sql_para)

        # 删除记录到blob表-异常单笔状态更新sql信息
        sql_para = {'ids':ids,'sqlid_name':['YC_SINGLE_SQLID']}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"blob_delete",sql_para)

        # 删除记录到阈值校验配置表
        sql_para = {'ids':ids}
        ModSql.yw_gtpm_002.execute_sql_dict(db,"yzjypz_delete",sql_para)

        #登记操作日志
        rznrr = '阈值校验_业务配置-删除：待删除业务配置信息：【'+ ','.join(tmp) +'】'
        ins_czrz(db,rznrr,'wh','阈值校验_业务配置管理-删除')

        #成功后返回成功信息
        data['msg'] = '删除记录成功'
        data['state'] = True
    # 将查询到的结果反馈给view
    return data