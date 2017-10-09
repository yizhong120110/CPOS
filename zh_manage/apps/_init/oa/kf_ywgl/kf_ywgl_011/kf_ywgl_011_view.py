# -*- coding: utf-8 -*-
# Action: 数据库模型管理
# Author: jind
# AddTime: 2015-02-02
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback,json
from sjzhtspj import request,render_to_string,logger
from .kf_ywgl_011_service import ( index_service,data_service,data_sjb_add_service,data_sjbtbls_service,data_tbxx_sjb_service,data_tbxx_sy_service,
    data_tbxx_ys_service,data_tbxx_zd_service,data_zdgl_service,data_sygl_service,data_ysgl_service,data_bef_zd_edit_service,data_load_zd_service,
    data_sjb_add_except_service,data_zd_add_service,data_zd_edit_service,data_sy_add_service,data_sy_del_service,data_ys_add_service,data_ys_del_service )

@register_url('GET')
def index_view():
    """
    # 数据库模型管理访问url
    """
    # 平台
    pt = request.GET.pt
    ywid = request.GET.ywid
    data = {'ywid': ywid}
    try:
        data = index_service( data )
        # 平台
        data['pt'] = pt if pt else 'kf'
    except:
        logger.info(traceback.format_exc())
    return render_to_string( "kf_ywgl/kf_ywgl_011/kf_ywgl_011.html",data )
    
@register_url('GET')
def data_view():
    """
    # 获取数据库模型列表数据
    """
    # 平台
    pt = request.GET.pt
    #业务ID
    ywid = request.GET.ywid
    # 数据表名称
    seaMc = request.GET.seaMc
    # 数据表名称描述
    seaMs = request.GET.seaMs
    # 获取rownum的开始和结束
    rn_start = request.rn_start
    rn_end = request.rn_end
    # 组织调用函数字典
    data_dic = { 'pt': pt, 'ywid': ywid, 'seaMc': seaMc, 'seaMs': seaMs, 'rn_start': rn_start, 'rn_end': rn_end }
    data = {'total':0, 'rows':[]}
    try:
        data = data_service( data_dic )
    except:
        logger.info(traceback.format_exc())
    return data

@register_url('POST')
def sjb_add_view():
    """
    # 新增数据表
    """
    # 字段信息
    data =  json.loads( request.forms.data )
    # 数据表名称 需将数据表名称转为大写，存储时为大写，以便后期与oracle系统表中的信息匹配时频繁的转换大小写
    sjbmc = request.forms.sjbmc.upper()
    # 数据表名称描述
    sjbmcms = request.forms.sjbmcms
    # 业务ID
    ywid = request.forms.ywid
    result = {'state':False, 'msg':''}
    try:
        result = data_sjb_add_service( ywid,data,sjbmc,sjbmcms )
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        result['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
        data_sjb_add_except_service( sjbmc )
    return result
    
@register_url('POST')
def data_zd_add_view():
    """
    # 新增字段
    # 此处不增加try except是因为在执行新增字段时，有一些DDL语句无法自动回滚，需执行回滚SQL进行处理，
    # 但在调用data_zd_add_service方法时，该方法中没有异常处理的机制，若出现异常无法将需要回滚的SQL返回，所以改为在data_zd_add_service方法中增加异常处理
    """
    # 数据表ID
    sjbid = request.forms.sjbid
    # 数据表名称
    sjbmc = request.forms.sjbmc
    # 字段名称
    zdmc = request.forms.zdmc.upper()
    # 字段描述
    zdms = request.forms.zdms
    # 字段类型
    zdlx = request.forms.zdlx
    # 字段长度
    zdcd = int( request.forms.zdcd ) if request.forms.zdcd else request.forms.zdcd
    # 小数长度
    xscd = int( request.forms.xscd ) if request.forms.xscd else request.forms.xscd
    # 是否可空
    sfkk = request.forms.sfkk 
    # 是否主键
    iskey = request.forms.iskey
    # 默认值
    mrz = request.forms.mrz
    # 调用新增字段方法
    result = data_zd_add_service( sjbid,sjbmc,zdmc,zdms.replace(';','；'),zdlx,zdcd,xscd,sfkk,iskey,mrz )
    return result
    
@register_url('POST')
def data_zd_edit_view():
    """
    # 新增字段
    # 此处不增加try except是因为在执行编辑字段时，有一些DDL语句无法自动回滚，需执行回滚SQL进行处理，
    # 但在调用data_zd_edit_service方法时，该方法中没有异常处理的机制，若出现异常无法将需要回滚的SQL返回，所以改为在data_zd_edit_service方法中增加异常处理
    """
    # 数据表ID
    sjbid = request.forms.sjbid
    # 数据表名称
    sjbmc = request.forms.sjbmc
    # 字段名称
    zdmc = request.forms.zdmc.upper()
    # 字段描述
    zdms = request.forms.zdms
    # 字段类型
    zdlx = request.forms.zdlx
    # 字段长度
    zdcd = int( request.forms.zdcd ) if request.forms.zdcd else request.forms.zdcd
    # 小数长度
    xscd = int( request.forms.xscd ) if request.forms.xscd else request.forms.xscd
    # 是否可空
    sfkk = request.forms.sfkk 
    # 是否主键
    iskey = request.forms.iskey
    # 默认值
    mrz = request.forms.mrz
    # 字段id
    zdid = request.forms.zdid
    # 调用编辑字段方法
    result = data_zd_edit_service( sjbid,sjbmc,zdmc,zdms.replace(';','；'),zdlx,zdcd,xscd,sfkk,iskey,mrz,zdid )
    return result
    
@register_url('POST')
def data_sy_add_view():
    """
    # 新增索引
    # 此处不增加try except是因为在执行新增索引时，有一些DDL语句无法自动回滚，需执行回滚SQL进行处理，
    # 但在调用data_sy_add_service方法时，该方法中没有异常处理的机制，若出现异常无法将需要回滚的SQL返回，所以改为在data_sy_add_service方法中增加异常处理
    """
    # 数据表ID
    sjbid = request.forms.sjbid
    # 数据表名称
    sjbmc = request.forms.sjbmc
    # 索引名称
    symc = request.forms.symc.upper()
    # 索引字段
    syzd = request.forms.syzd
    # 索引类型
    sylx = request.forms.sylx
    # 是否唯一索引
    sfwysy = request.forms.sfwysy
    # 调用新增索引方法
    result = data_sy_add_service( sjbid,sjbmc,symc,syzd,sylx,sfwysy )
    return result
    
@register_url('POST')
def data_sy_del_view():
    """
    # 删除索引
    # 此处不增加try except是因为在执行删除索引时，有一些DDL语句无法自动回滚，需执行回滚SQL进行处理，
    # 但在调用data_sy_del_service方法时，该方法中没有异常处理的机制，若出现异常无法将需要回滚的SQL返回，所以改为在data_sy_del_service方法中增加异常处理
    """
    # 数据表ID
    sjbid = request.forms.sjbid
    # 数据表名称
    sjbmc = request.forms.sjbmc
    # 索引ID
    syid = request.forms.syid
    # 调用删除索引方法
    result = data_sy_del_service( sjbid,sjbmc,syid )
    return result
    
@register_url('POST')
def data_ys_add_view():
    """
    # 新增约束
    # 此处不增加try except是因为在执行新增约束时，有一些DDL语句无法自动回滚，需执行回滚SQL进行处理，
    # 但在调用data_ys_add_service方法时，该方法中没有异常处理的机制，若出现异常无法将需要回滚的SQL返回，所以改为在data_ys_add_service方法中增加异常处理
    """
    # 数据表ID
    sjbid = request.forms.sjbid
    # 数据表名称
    sjbmc = request.forms.sjbmc
    # 约束名称
    ysmc = request.forms.ysmc.upper()
    # 约束字段
    yszd = request.forms.yszd
    # 调用约束索引方法
    result = data_ys_add_service( sjbid,sjbmc,ysmc,yszd )
    return result
    
@register_url('POST')
def data_ys_del_view():
    """
    # 删除约束
    # 此处不增加try except是因为在执行删除约束时，有一些DDL语句无法自动回滚，需执行回滚SQL进行处理，
    # 但在调用data_ys_del_service方法时，该方法中没有异常处理的机制，若出现异常无法将需要回滚的SQL返回，所以改为在data_ys_del_service方法中增加异常处理
    """
    # 数据表ID
    sjbid = request.forms.sjbid
    # 数据表名称
    sjbmc = request.forms.sjbmc
    # 约束ID
    ysid = request.forms.ysid
    # 调用删除约束方法
    result = data_ys_del_service( sjbid,sjbmc,ysid )
    return result
    
@register_url('GET')
def data_sjbtbls_view():
    """
    # 获取数据库模型列表数据
    """
    # 业务ID
    ywid = request.GET.ywid
    # 开始日期
    ksrq = request.GET.ksrq
    # 结束日期
    jsrq = request.GET.jsrq
    # 获取rownum的开始和结束
    rn_start = request.rn_start
    rn_end = request.rn_end
    data = {'total':0, 'rows':[]}
    try:
        data = data_sjbtbls_service( ywid,ksrq,jsrq,rn_start,rn_end )
    except:
        logger.info(traceback.format_exc())
    return data

@register_url('POST')
def data_tbxx_sjb_view():
    """
    # 获取数据表名称描述的同步信息
    """
    # 同步流水ID
    tblsid = request.forms.tblsid
    # 数据表ID
    sjbid = request.forms.sjbid
    data = {'state':False}
    try:
        data = data_tbxx_sjb_service( tblsid,sjbid )
    except:
        logger.info(traceback.format_exc())
    return data

@register_url('GET')
def data_tbxx_sy_view():
    """
    # 获取数据表索引同步信息
    """
    # 同步流水ID
    tblsid = request.GET.tblsid
    data = {'rows':[],'state':False}
    try:
        data = data_tbxx_sy_service( tblsid )
    except:
        logger.info(traceback.format_exc())
    return data
    
@register_url('GET')
def data_tbxx_ys_view():
    """
    # 获取数据表约束同步信息
    """
    # 同步流水ID
    tblsid = request.GET.tblsid
    data = {'rows':[],'state':False}
    try:
        data = data_tbxx_ys_service( tblsid )
    except:
        logger.info(traceback.format_exc())
    return data
    
@register_url('GET')
def data_tbxx_zd_view():
    """
    # 获取数据表字段同步信息
    """
    # 同步流水ID
    tblsid = request.GET.tblsid
    data = {'rows':[],'state':False}
    try:
        data = data_tbxx_zd_service( tblsid )
    except:
        logger.info(traceback.format_exc())
    return data

@register_url('GET')
def data_zdgl_view():
    """
    # 编辑数据表时字段管理数据
    """
    # 数据表ID
    sjbid = request.GET.sjbid
    data = {'rows':[],'state':False}
    try:
        data = data_zdgl_service( sjbid )
    except:
        logger.info(traceback.format_exc())
    return data

@register_url('GET')
def data_sygl_view():
    """
    # 编辑数据表时索引管理数据
    """
    # 数据表ID
    sjbid = request.GET.sjbid
    data = {'rows':[],'state':False}
    try:
        data = data_sygl_service( sjbid )
    except:
        logger.info(traceback.format_exc())
    return data

@register_url('GET')
def data_ysgl_view():
    """
    # 编辑数据表时约束管理数据
    """
    # 数据表ID
    sjbid = request.GET.sjbid
    data = {'rows':[],'state':False}
    try:
        data = data_ysgl_service( sjbid )
    except:
        logger.info(traceback.format_exc())
    return data
    
@register_url('POST')
def data_bef_zd_edit_view():
    """
    # 编辑字段时，获取字段信息
    """
    # 字段ID
    id = request.forms.id
    data = {'state':False,'id':id }
    try:
        rs = data_bef_zd_edit_service( id )
        data.update( rs)
        data['state'] = True
    except:
        logger.info(traceback.format_exc())
    return data

@register_url('POST')
def data_load_zd_view():
    """
    # 获取字段名称下拉框数据
    """
    # 数据表ID
    sjbid = request.forms.sjbid
    data = {'state':False }
    try:
        data = data_load_zd_service( sjbid )
    except:
        logger.info(traceback.format_exc())
    return data
