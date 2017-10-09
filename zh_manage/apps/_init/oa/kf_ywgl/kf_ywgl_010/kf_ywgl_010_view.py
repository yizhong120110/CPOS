# -*- coding: utf-8 -*-
# Action: 业务详情-文档清单 view
# Author: zhangchl
# AddTime: 2015-01-05
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import logger, request,render_to_string, get_sess_hydm, render_string
from .kf_ywgl_010_service import index_service, data_service, data_add_service, data_edit_service, data_del_service, data_down_service


@register_url('GET')
def index_view():
    """
    # 文档清单主页面
    """
    # 组织反馈信息
    data = { 'ywid': '', 'data_wdlb': [] }
    try:
        # 业务id
        ywid = request.GET.ywid
        data['ywid'] = ywid
        # 调用操作数据库函数
        data['data_wdlb'] = index_service()
    except:
        logger.info(traceback.format_exc())
    
    return render_to_string("kf_ywgl/kf_ywgl_010/kf_ywgl_010.html", data)

@register_url('GET')
def data_view():
    """
    # 业务详情-文档清单 列表初始化
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 业务id
        ywid = request.GET.ywid
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'ywid': ywid, 'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = data_service( data_dic )
    except:
        logger.info(traceback.format_exc())
        
    return data

@register_url('POST')
def data_add_view():
    """
    # 业务详情-文档清单 新增 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 当前登录人
        hydm = get_sess_hydm()
        # 文档对象
        fileobj = request.files.get('scwd');
        # 文档名称
        wdmc = fileobj.raw_filename
        # 文档内容
        wdnr = fileobj.file.read()
        # 文档内容长度，为零时，不允许上传
        wdnr_len = len(wdnr)
        # 文档大小(M) 最大可上传200M
        wdnr_size = wdnr_len/1024/1024
        # 所属业务id
        ssywid = request.forms.ywid
        # 文档类别
        wdlb = request.forms.wdlb
        # 组织调用函数字典
        data_dic = { 'hydm': hydm, 'wdmc': wdmc,
            'wdnr': wdnr, 'wdnr_len': wdnr_len,
            'wdnr_size': wdnr_size, 'ssywid': ssywid,
            'wdlb': wdlb }
        # 调用操作数据库函数
        result = data_add_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '添加文件失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def data_edit_view():
    """
    # 业务详情-文档清单 上传
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 文档对象
        fileobj = request.files.scwd;
        # 上传文档清单id
        wdqdid = request.forms.wdqdid
        # 文档类别
        wdlb = request.forms.wdlb
        # 所属业务id
        ssywid = request.forms.ywid
        # 组织调用函数字典
        data_dic = { 'fileobj': fileobj,
            'wdqdid': wdqdid, 'ssywid': ssywid,
            'wdlb': wdlb }
        # 调用操作数据库函数
        result = data_edit_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '上传失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('POST')
def data_del_view():
    """
    # 文档清单 删除 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 删除文档清单id
        wdqdid = request.forms.wdqdid
        # 删除文档名称
        wdmc = request.forms.wdmc
        # 组织调用函数字典
        data_dic = { 'wdqdid': wdqdid, 'wdmc': wdmc }
        # 调用操作数据库函数
        result = data_del_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '删除失败！异常错误提示信息[%s]' % error_msg
    
    return result

@register_url('GET')
def data_down_view():
    """
    # 业务详情-文档清单 下载
    """
    # 业务id
    ywid = request.GET.ywid
    # 反馈信息
    to_path = 'window.location.href="/oa/kf_ywgl/kf_ywgl_010/kf_ywgl_010_view/index_view?ywid=%s"' % ywid
    try:
        # 下载文档清档id集合
        wdqdidstr = request.GET.wdqdidstr
        # 下载类型
        downtype = request.GET.downtype
        # 组织调用函数字典
        data_dic = { 'wdqdidstr': wdqdidstr, 'downtype': downtype, 'to_path': to_path }
        # 调用操作数据库函数
        result = data_down_service( data_dic )
        return result
    except:
        logger.info(traceback.format_exc())
        return render_string( "<script>%s</script>" % to_path )
    
    return render_string( "<script>%s</script>" % to_path )
