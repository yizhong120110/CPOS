# -*- coding: utf-8 -*-
# Action: 导入
# Author: jind
# AddTime: 2015-02-10
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback,json,pickle
from sjzhtspj import request,render_to_string,logger
from .kf_ywgl_019_service import index_service,data_service,data_import_jy_service,data_wtjsj_service,data_drwj_add_service,bbdb_data_service,dr_submit_service

@register_url('GET')
def index_view():
    """
    # 访问导入主页面
    """
    ywid = request.GET.ywid
    drlx = request.GET.drlx
    txid = request.GET.txid
    data = {'ywid':ywid,'drlx':drlx,'txid':txid}
    try:
        data['xtlx'] = index_service()
    except:
        logger.info(traceback.format_exc())
    return render_to_string("kf_ywgl/kf_ywgl_019/kf_ywgl_019.html", data )
    
@register_url('POST')
def data_import_jy_view():
    """
    # 导出时校验是否有未提交的数据
    """
    ywid = request.forms.ywid
    drlx = request.forms.drlx
    txid = request.forms.txid
    data = {'state':False,'msg':'','sfywtj':False}
    try:
        data['sfywtj'] = data_import_jy_service( ywid,drlx,txid )
        data['state'] = True
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '请求异常！异常错误提示信息[%s]' % error_msg
    return data
        
@register_url('GET')
def data_view():
    """
    # 获取导入页面数据
    """
    ywid = request.GET.ywid
    drlx = request.GET.drlx
    txid = request.GET.txid
    data = {'state':False,'msg':'','rows':[] }
    try:
        data = data_service( ywid,drlx,txid )
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '请求异常！异常错误提示信息[%s]' % error_msg
    return data

@register_url('POST')
def data_wtjsj_view():
    """
    # 获取未提交数据
    """
    ywid = request.POST.ywid
    drlx = request.POST.drlx
    txid = request.POST.txid
    data = {'state':False,'msg':'','leftRows':'','rightRows':''}
    try:
        data = data_wtjsj_service( ywid,drlx,txid )
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '请求异常！异常错误提示信息[%s]' % error_msg
    return data
    
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
    # 业务ID
    ywid = request.forms.ywid
    # 导入类型
    drlx = request.forms.drlx
    # 系统类型
    xtlx = request.forms.xtlx
    # 通讯ID
    txid = request.forms.txid
    data = {'state':False,'msg':''}
    try:
        data = data_drwj_add_service(filename,wjnr,ywid,drlx,xtlx,txid)
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '文件导入失败！异常错误提示信息[%s]' % error_msg
    return data
	
@register_url('GET')
def bbdb_data_view():
    """
    # 版本比对
    """
    # 要比对的数据ID
    id = request.GET.id
    # 要比对的类型
    lx = request.GET.lx
    # 业务ID
    ywid = request.GET.ywid
    # 导入类型
    drlx = request.GET.drlx
    # 通讯ID
    txid = request.GET.txid
    # 节点类型
    jdlx = request.GET.jdlx
    data = {'url':''}
    try:
        data = bbdb_data_service(id,lx,ywid,drlx,txid,jdlx)
    except:
        logger.info(traceback.format_exc())
    return render_to_string(data['url'],data)
    
@register_url('POST')
def dr_submit_view():
    """
    # 导出时校验是否有未提交的数据
    """
    # 业务ID
    ywid = request.forms.ywid
    # 导入类型
    drlx = request.forms.drlx
    # 通讯ID
    txid = request.forms.txid
    # 导入信息
    drxx = json.loads( request.forms.drxx )
    # 导入描述
    drms = request.forms.drms
    # 备注
    bzxx = request.forms.bz
    # 复核人
    fhr = request.forms.fhr
    # 复核人密码
    fhrmm = request.forms.fhrmm
    # 系统类型
    xtlx = request.forms.xtlx
    # 导入流水ID
    drlsid = request.forms.drlsid
    data = dr_submit_service( ywid,drlx,txid,drxx,drms,bzxx,fhr,fhrmm,xtlx,drlsid )
    return data    