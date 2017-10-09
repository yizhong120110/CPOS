# -*- coding: utf-8 -*-
# Action: 维护系统导入
# Author: zhangzhf
# AddTime: 2015-10-20
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback,json
from sjzhtspj import logger, request, render_to_string
from .yw_pzsj_001_service import local_data_service,data_drwj_add_service,bbdb_data_service,dr_submit_service

@register_url('GET')
def index_view():
    """
    # 维护系统导入页面加载view
    """
    return render_to_string("yw_pzsj/yw_pzsj_001/yw_pzsj_001.html")
    
@register_url('POST')
def local_data_view():
    """
    # 获取要导出信息的view
    """
    # 数据结构    
    data = {'state':False, 'msg':'没有可导出的对象','rows':[]}
    try:
        # 调用service
        data = local_data_service()
    except:
        # 程序异常时，将异常抛出，写入到日志中
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        data['msg'] = '获取导出信息失败！异常错误提示信息\n[%s]' % error_msg
    return json.dumps(data)
    
@register_url('POST')
def data_drwj_add_view():
    """
    # 将导入文件中的数据导入值数据库
    """
    # 文档对象
    fileobj = request.files.get('drwj');
    # 文件名称
    filename = fileobj.raw_filename
    # 文件内容
    wjnr = fileobj.file.read()
    # 导入类型
    drlx = "wh"
    data = {'state':False,'msg':'','leftRows':[], 'rightRows':[],'id_dic':{},'drlsid':''}
    try:
        data = data_drwj_add_service(filename,wjnr,drlx)
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '文件导入失败！异常错误提示信息[%s]' % error_msg
    return data

@register_url('GET')
def bbdb_data_view():
    """
    # 数据比对
    """
    # 比对类型
    lx = request.GET.lx
    # 名称
    mc = request.GET.mc
    # id
    id = request.GET.id
    # 指标id
    zbid = request.GET.zbid
    # 规则id
    gzid = request.GET.gzid
    # 返回比对数据
    data = {'url':''}
    try:
        data = bbdb_data_service(id,lx,mc,zbid,gzid)
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '获取信息失败！异常错误提示信息[%s]' % error_msg
    return render_to_string(data['url'],data)
    
@register_url('POST')
def dr_submit_view():
    """
    # 将数据从临时表导入正式表
    """
    # 导入对象的id
    id_dic = request.forms.id_dic
    # 导入类型
    drlx = "wh"
    # 导入描述
    drms = request.forms.drms
    # 备注
    bzxx = request.forms.bz
    # 复核人
    fhr = request.forms.fhr
    # 复核人密码
    fhrmm = request.forms.fhrmm
    # 导入流水
    drlsid = request.forms.drlsid
    
    data = {'state':False,'msg':''}
    try:
        data = dr_submit_service(id_dic, drlx,drms,bzxx,fhr,fhrmm,drlsid)
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '文件导入失败！异常错误提示信息[%s]' % error_msg
    return data