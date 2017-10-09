# -*- coding: utf-8 -*-
# Action: 阈值校验 - 参数配置
# Author: luoss
# AddTime: 2015-05-04
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback,json
from sjzhtspj import request, redirect,render_to_string,logger
from .yw_gtpm_001_service import cspz_service,data_service,search_service,add_service,update_service,del_pl_service

@register_url('GET')
def index_view():
    """
    # 目录选择时执行的页面跳转
    """
    # 页面跳转
    return render_to_string( "yw_gtpm/yw_gtpm_001/yw_gtpm_001.html")

@register_url('GET')
def cspz_view():
    """
    # 参数配置页面的跳转 并附有两个下拉列表的值
    """
    data = { 'ssyw_lst': [], 'csdm_lst': [] }
    try:
        # 调用操作数据库函数
        data = cspz_service()
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    # 页面跳转执行
    return render_to_string( "yw_gtpm/yw_gtpm_001/yw_gtpm_001_cspz.html", data )

@register_url('POST')
def data_view():
    """
    # 自动发起表格数据查询
    """
    # 初始化反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 参数代码
        csdm = request.POST.csdm
        # 业务ID
        ywid = request.POST.ywid
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'csdm': csdm, 'ywid': ywid, 'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = data_service( data_dic )
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    # 将组织的结果反馈给前台
    return data

@register_url('GET')
def cspz_ggym_view():
    """
    # 参数配置页面的跳转 并附有两个下拉列表的值
    """
    # 初始化返回值
    data = {'ssyw_lst': [], 'csdm_lst': [] }
    try:
        # 获取前台信息
        csid = request.GET.id
        # 调用操作数据库函数
        data = cspz_service()
        data['csid'] = csid
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    # 页面跳转执行
    return render_to_string( "yw_gtpm/yw_gtpm_001/yw_gtpm_001_cspz_ggym.html", data )


@register_url('POST')
def search_view():
    """
    # 条件查询时 下拉菜单获取业务名称信息
    """
    # 初始化返回值
    data = None
    try:
        # 获取信息
        csid = request.POST.csid
        # 请求字典
        sql_data = {'csid':csid}
        # 调用方法
        data = search_service( sql_data )
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        logger.info(traceback.format_exc())
    return json.dumps(data)

@register_url('POST')
def add_view():
    """
    # 新增系统参数
    """
    # 初始化返回值
    result = {'state':False, 'msg': ''}
    try:
        # 参数代码
        csdm = request.forms.csdm
        # 业务ID
        ywid = request.forms.ywid
        # 监控时间
        jksj = request.forms.jksj
        # 单笔最大金额
        dbzdje = request.forms.dbzdje
        # 校验周期
        jyzq = request.forms.jyzq
        # 校验阈值
        jyyz = request.forms.jyyz
        # 参数描述
        csms = request.forms.csms
        # 参数状态
        cszt = request.forms.cszt
        # 调用方法
        result = add_service(csdm, ywid, jksj, dbzdje, jyzq, jyyz, csms, cszt)
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
    return result

@register_url('POST')
def update_view():
    """
    # 修改系统参数
    """
    # 初始化返回值
    result = {'state':False, 'msg': ''}
    try:
        # 参数ID
        csid = request.forms.csid
        # 参数代码
        csdm = request.forms.csdm
        # 业务ID
        ywid = request.forms.ywid
        # 监控时间
        jksj = request.forms.jksj
        # 单笔最大金额
        dbzdje = request.forms.dbzdje
        # 校验周期
        jyzq = request.forms.jyzq
        # 校验阈值
        jyyz = request.forms.jyyz
        # 参数描述
        csms = request.forms.csms
        # 参数状态
        cszt = request.forms.cszt
        # 调用方法
        result = update_service(csid, csdm, ywid, jksj, dbzdje, jyzq, jyyz, csms, cszt)
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '编辑失败！异常错误提示信息[%s]' % error_msg
    return result

@register_url('POST')
def del_pl_view():
    """
    # 批量删除业务配置记录
    """
    # 初始化返回值
    result = {'state':False, 'msg':''}
    try:
        # 参数ID，逗号分隔
        csid = request.POST.csid
        # 调用方法
        result = del_pl_service(csid)
    except:
        # 查询出现异常时，将异常信息写入到日志文件中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '删除失败！异常错误提示信息[%s]' % error_msg
    return result