# -*- coding: utf-8 -*-
# Action: 版本提交view
# Author: zhangzf
# AddTime: 2015-1-13
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import request, logger, render_to_string
from .kf_ywgl_023_bbtj_service import last_bbxx_service,bbtj_service,bbhy_index_service,bbhy_add_service,bbxxck_data_service,bbxx_data_service,bbdb_data_service

@register_url('GET')
def last_bbxx_view():
    """
    # 版本提交页面
    """
    
    # 提交内容的类型
    lx = request.GET.lx
    # 提交内容的id
    id = request.GET.id
    # 提交版本后需要刷新的grid的id
    gridid = request.GET.gridid
    
    # 查询上一版本的提交内容
    bbxx = last_bbxx_service(lx, id, gridid)
    return render_to_string("kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbtj.html",bbxx)

@register_url('POST')
def bbtj_view():
    """
    # 版本提交方法
    """
    
    # 提交内容的类型
    lx = request.forms.lx
    # 提交内容的id
    id = request.forms.id
    # 提交描述
    tjms = request.forms.tjms
    result = {'state':False, 'msg':''}
    try:
        # 版本提交
        return bbtj_service(lx,id,tjms)
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '版本提交失败！异常错误提示信息[%s]' % error_msg
        
    return result
    
@register_url('GET')
def bbhy_index_view():
    """
    # 版本还原页面
    """
    # 还原内容的类型
    lx = request.GET.lx
    # 还原内容的id
    id = request.GET.id
    # 提交版本后需要刷新的grid的id
    gridid = request.GET.gridid
    
    # 查询上一版本的提交内容
    bbxx = bbhy_index_service(lx, id, gridid)
    return render_to_string("kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbhy.html",bbxx)

@register_url('POST')
def bbhy_add_view():
    """
    # 版本还原方法
    """
    # 还原内容的类型
    lx = request.forms.lx
    # 还原内容的id
    id = request.forms.id
    result = {'state':False, 'msg':''}
    try:
        # 还原提交
        bbhy_add_service(lx,id)
        result['state'] = True
        result['msg'] = '还原成功'
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '版本还原失败！异常错误提示信息[%s]' % error_msg
    return result

@register_url('GET')
def bbxxck_index_view():
    """
    # 访问版本信息查看首页
    """
    # 类型
    lx = request.GET.lx
    # id
    id = request.GET.id
    # 节点类型
    jdlx = request.GET.jdlx
    result = {'lx':lx, 'id':id, 'jdlx':jdlx}
    return render_to_string("kf_ywgl/kf_ywgl_023/kf_ywgl_023_bbxxck.html", result)

@register_url('GET')
def bbxxck_data_view():
    """
    # 版本信息查看数据获取
    """
    data = {'total':0, 'rows':[]}
    try:
        # 类型
        lx = request.GET.lx
        # id
        id = request.GET.id
        # 提交日期
        tjrq = request.GET.tjrq
        # 提交描述
        tjms = request.GET.tjms
        # 版本号
        bbh = request.GET.bbh
        # 获取rownum的开始和结束
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'lx': lx, 'id': id, 'tjrq': tjrq, 'tjms': tjms, 'bbh': bbh, 'rn_start': rn_start, 'rn_end': rn_end }
        # 版本信息查看信息
        data = bbxxck_data_service( data_dic )
    except:
        logger.info(traceback.format_exc())
    return data
    
@register_url('GET')
def bbxx_data_view():
    """
    # 版本详细信息查看
    """
    # 类型
    lx = request.GET.lx
    # id
    id = request.GET.id
    # 版本号
    bbh = request.GET.bbh
    # 节点类型
    jdlx = request.GET.jdlx
    data = {'url':'','rs':''}
    try:
        # 版本详细信息查看
        data = bbxx_data_service(id,lx,bbh)
    except:
        logger.info(traceback.format_exc())
    data['rs']['jdlx'] = jdlx
    return render_to_string(data['url'],data['rs'])

@register_url('GET')
def bbdb_data_view():
    """
    # 版本对比
    """
        # 比对内容的类型
    lx = request.GET.lx
    # 比对内容内容的id
    id = request.GET.id
    # 版本号1
    bbh1 = request.GET.bbh1
    # 版本号2
    bbh2 = request.GET.bbh2
    # 比对类型，版本对比还是本地文件对比
    type = request.GET.type
    # 节点类型
    jdlx = request.GET.jdlx
    data = {'url':'','rs':''}
    try:
        # 版本对比
        data = bbdb_data_service(id,lx,bbh1,bbh2,type,jdlx)
    except:
        logger.info(traceback.format_exc())
    return render_to_string(data['url'],data['rs'])
