# -*- coding: utf-8 -*-
# Action: 阈值校验业务配置
# Author: kongdq
# AddTime: 2015-04-28
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import logger, request, render_to_string
from .yw_gtpm_002_service import data_service, ssyw_service,add_service,cx_ywpz_service,update_service,delete_service

@register_url('GET')
def index_view():
    """     
    # GTP管理- 业务配置
    """
    # 初始化反馈前台信息
    data = { 'ssyw_lst': [],'kzjyfs_lst':[] }
    try:
        # 获取下拉列表信息
        data = ssyw_service()
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    return render_to_string("yw_gtpm/yw_gtpm_002/yw_gtpm_002.html",data)

@register_url('GET')
def data_view():
    """
    # 业务信息json数据
    """

    # 初始化返回值
    data = {'total':0, 'rows':[]}
    try:
        # 组织查询信息
        # 翻页开始下标
        rn_start = request.rn_start
        # 翻页结束下标
        rn_end = request.rn_end
        # 查询字段名称
        wjlx = request.GET.wjlx
        ssyw = request.GET.ssyw
        # 请求字典
        sql_data = { 'rn_start': rn_start, 'rn_end': rn_end,'wjlx':wjlx,'ssyw':ssyw }
        # 调用service
        data = data_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())

    # 将结果反馈给前台
    return data

@register_url('GET')
def ywpz_view():
    """     
    # GTP管理- 业务配置新增和编辑页面跳转
    """
    # 获取前台信息
    id = request.GET.id
    data = { 'ssyw_lst': [],'kzjyfs_lst':[]}
    try:
        # 获取下拉列表信息
        data = ssyw_service()
        data['id'] = id
        # 页面跳转
        return render_to_string("yw_gtpm/yw_gtpm_002/yw_gtpm_002_ywpz.html",data)
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())

@register_url('POST')
def add_ywpz_view():
    """
    # 新增业务配置记录
    """

    # 初始化返回值
    data = {'state':False, 'msg':''}
    #所属业务与文件类型
    ssyw = request.POST.ssywbm
    wjlx = request.POST.wjlx
    #扩展交易内容 sql or code
    kzjyfs = request.POST.kzjyfs
    kzjyCode = request.POST.txtKzjyfsmkdm
    kzjynr = request.POST.txtKzjysql if kzjyfs=='SQL' else kzjyCode
    #流水导入内容
    lsjyfs = request.POST.lsdrfs
    lsjyCode = request.POST.txtLsdrmkdm
    lsdrnr = request.POST.txtLsdrfssql if lsjyfs=='SQL' else lsjyCode
    #扣款明细sql
    kkmxsql = request.POST.hqkkmxjesql
    #扣款明细数据查询信息
    kkmxcx = request.POST.kkmxsjcxsql
    #异常全部撤销
    ycqbcx = request.POST.ycqbcxsql
    #异常全部通过
    ycqbtg = request.POST.ycqbtgsql
    #异常单笔状态更新
    ycdbztgx = request.POST.ycdbztgxsql

    try:
        sql_data = {'ssyw':ssyw,'wjlx':wjlx,'kzjyfs':kzjyfs,'kzjyCode':kzjyCode,'lsjyfs':lsjyfs,
                    'lsjyCode':lsjyCode,'kzjynr':kzjynr,'lsdrnr':lsdrnr,'kkmxsql':kkmxsql,
                    'kkmxcx':kkmxcx,'ycqbtg':ycqbtg,'ycqbcx':ycqbcx,'ycdbztgx':ycdbztgx}
        #调用后台service
        data = add_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '新增失败！异常错误![%s]' % error_msg
    # 将结果反馈给前台
    return data

@register_url('POST')
def cx_ywpz_view():
    """
    # 查询业务配置展示信息
    """
    data ={'msg':[]}
    try:
        # 业务配置ID
        ywpz_id = request.POST.ywpz_id
        sql_data = {'ywpz_id':ywpz_id}
        #调用后台service
        data = cx_ywpz_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '查询失败！异常错误![%s]' % error_msg

    # 将结果反馈给前台
    return data

@register_url('POST')
def edit_ywpz_view():
    """
    # 修改业务配置记录
    """

    # 初始化返回值
    data = {'state':False, 'msg':''}
    #业务配置ID
    id = request.POST.csid
    #所属业务与文件类型
    ywmc = request.POST.ssywbm
    wjlx = request.POST.wjlx
    #扩展交易内容 sql or code
    kzjyfs = request.POST.kzjyfs
    kzjyCode = request.POST.txtKzjyfsmkdm
    kzjynr = request.POST.txtKzjysql if kzjyfs=='SQL' else kzjyCode
    #流水导入内容
    lsjyfs = request.POST.lsdrfs
    lsjyCode = request.POST.txtLsdrmkdm
    lsdrnr = request.POST.txtLsdrfssql if lsjyfs=='SQL' else lsjyCode
    #扣款明细sql
    kkmxsql = request.POST.hqkkmxjesql
    #扣款明细数据查询信息
    kkmxcx = request.POST.kkmxsjcxsql
    #异常全部撤销
    ycqbcx = request.POST.ycqbcxsql
    #异常全部通过
    ycqbtg = request.POST.ycqbtgsql
    #异常单笔状态更新
    ycdbztgx = request.POST.ycdbztgxsql
    #原信息列表
    yxxlb = request.POST.yxxlb

    try:
        sql_data = {'id':id,'ywmc':ywmc,'wjlx':wjlx,'kzjyfs':kzjyfs,'kzjyCode':kzjyCode,'lsjyfs':lsjyfs,
                    'lsjyCode':lsjyCode,'kzjynr':kzjynr,'lsdrnr':lsdrnr,'kkmxsql':kkmxsql,
                    'kkmxcx':kkmxcx,'ycqbtg':ycqbtg,'ycqbcx':ycqbcx,'ycdbztgx':ycdbztgx,'yxxlb':yxxlb}
        #调用后台service
        data = update_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '保存失败！异常错误![%s]' % error_msg
    # 将结果反馈给前台
    return data

@register_url('POST')
def delete_ywpz_view():
    """
    # 删除业务配置记录
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}
    #业务配置ID列表
    ids = request.POST.ids
    try:
        #前台传入业务配置ID列表
        sql_data = {'ids':ids}
        #调用后台service
        data = delete_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '删除失败！异常错误![%s]' % error_msg
    # 将结果反馈给前台
    return data