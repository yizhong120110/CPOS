# -*- coding: utf-8 -*-
# Action: 数据库表信息查看 view
# Author: zhangchl
# AddTime: 2014-12-30
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import logger, request,render_to_string
from .kf_ywgl_012_service import index_service, data_service, data_add_service, data_edit_service, data_del_service


@register_url('GET')
def index_view():
    """
    # 数据库表信息查看：主页面
    """
    # 平台
    pt = request.GET.pt
    # 数据库模型ID
    sjkmxdy_id = request.GET.sjkmxdy_id
    # Demo基本信息
    demojbxxid = request.GET.demojbxxid
    # 类型(lx为'demo'时表示操作demo基本信息和demo数据表，并不是真实表)
    lx = request.GET.lx
    # 反馈信息
    # sjkmxdy_dic：数据表基本信息
    #   sjbmc: 数据表名称
    #   sjbzwmc: 数据表中文名称
    # dg_columns: 数据表中字段信息集合
    sjkmxdy_dic = {'sjkmxdy_id':sjkmxdy_id, 'sjbmc':'', 'sjbzwmc':''}
    data = {'sjkmxdy_dic':sjkmxdy_dic, 'dg_columns': [], 'demojbxxid': demojbxxid, 'lx': lx }
    try:
        # 组织调用函数字典
        data_dic = { 'sjkmxdy_id': sjkmxdy_id, 'demojbxxid': demojbxxid, 'lx': lx }
        # 调用操作数据库函数
        data = index_service( data_dic )
        # 此数据表不存在
        if data['error_msg']:
            return render_string( data['error_msg'] )
        # 平台
        data['pt'] = pt if pt else 'kf'
    except:
        logger.info(traceback.format_exc())
    
    return render_to_string("kf_ywgl/kf_ywgl_012/kf_ywgl_012.html", data)

@register_url('GET')
def data_view():
    """
    # 数据库表信息查看：获取显示数据
    """
    # 初始化反馈信息
    # total： 数据表内数据总条数
    # rows： 数据表内本页面显示信息
    data = {'total':0, 'rows':[]}
    try:
        # 数据库表名称
        sjbmc = request.GET.sjbmc
        # 数据库表表字段集合
        zdmc_str = request.GET.zdmc_str
        # 数据库表主键集合
        sjbzj_str = request.GET.sjbzj_str
        # 字段信息集合（字段名称，字段描述，字段长度，是否可控，数据类型, 小数位数, 总位数）
        zdxx_str = request.GET.zdxx_str
        # 条件查询 条件名称
        search_name = request.GET.search_name
        # 条件查询 条件名称查询
        search_name_sel = request.GET.search_name_sel
        # 条件查询 条件值
        search_value = request.GET.search_value
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'sjbmc': sjbmc, 'zdmc_str': zdmc_str,
        'sjbzj_str': sjbzj_str, 'zdxx_str': zdxx_str, 'search_name': search_name,
        'search_name_sel': search_name_sel, 'search_value': search_value, 
        'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = data_service( data_dic )
    except:
        logger.info(traceback.format_exc())
        
    return data

@register_url('POST')
def data_add_view():
    """
    # 数据库模型 表信息 新增 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 操作表名称
        czsjbmc = request.forms.czsjbmc
        # 主键字段集合
        zjzd_str = request.forms.sjbzj
        # 字段信息集合（字段名称，字段描述，字段长度，是否可控，数据类型, 小数位数, 总位数）
        zdxx_str = request.forms.zdxx_str
        # 数据表字段集合
        zdmc_str = request.forms.zdmc_str
        # 数据表字段集合lst
        zdmc_lst = zdmc_str.split(',')
        # 组织前台页面填写信息
        new_dic = {}
        for zdmc in zdmc_lst:
            if zdmc:
                zdv = eval( 'request.forms.name_%s' % zdmc )
                new_dic[ zdmc ] = zdv
        # 组织调用函数字典
        data_dic = { 'czsjbmc': czsjbmc, 'zjzd_str': zjzd_str,
            'zdxx_str': zdxx_str, 'zdmc_str': zdmc_str,
            'zdmc_lst': zdmc_lst, 'new_dic': new_dic }
        # 调用操作数据库函数
        result = data_add_service( data_dic )
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        ret_err_msg = error_msg[error_msg.find('cx_Oracle'):]
        result['msg'] = '插入失败！\n异常错误提示信息[%s]' % ret_err_msg
    
    return result

@register_url('POST')
def data_edit_view():
    """
    # 数据库模型 表信息 编辑 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 操作表名称
        czsjbmc = request.forms.czsjbmc
        # 数据表主键value(zdmc|zdvalue~zdmc2|zdvalue)
        zj_v = request.forms.sjbzjvalue
        zj_v_lst = zj_v.split('~')
        # 主键字段列表
        sjbzjzd_lst = [ zjxx.split('|')[0] for zjxx in zj_v_lst ]
        # 主键值字典{主键k:主键v,主键2: 主键2v}
        sjbzjzd_dic = dict( [ [ zjxx.split('|')[0], zjxx.split('|')[1] ] for zjxx in zj_v_lst ] )
        # 字段信息集合（字段名称，字段描述，字段长度，是否可控，数据类型, 小数位数, 总位数）
        zdxx_str = request.forms.zdxx_str
        # 数据表字段集合
        zdmc_str = request.forms.zdmc_str
        zdmc_lst = zdmc_str.split(',')
        
        # 组织前台页面填写信息
        upd_dic = {}
        for zdmc in zdmc_lst:
            if zdmc and zdmc not in sjbzjzd_lst:
                zdv = eval( 'request.forms.name_%s' % zdmc )
                upd_dic[ zdmc ] = zdv
        # 组织调用函数字典
        data_dic = { 'czsjbmc': czsjbmc, 'zdxx_str': zdxx_str,
        'upd_dic': upd_dic,'sjbzjzd_dic': sjbzjzd_dic }
        # 调用操作数据库函数
        result = data_edit_service( data_dic )
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        ret_err_msg = error_msg[error_msg.find('cx_Oracle'):]
        result['msg'] = '修改失败！\n异常错误提示信息[%s]' % ret_err_msg
    
    return result

@register_url('POST')
def data_del_view():
    """
    # 表信息删除 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    try:
        # 数据表名称
        sjbmc = request.forms.sjbmc
        # 删除数据列表( zdmc|zdvalue|zdtype~zdmc2|zdvalue|zdtype,zdmc|zdvalue2|zdtype~zdmc2|zdvalue2|zdtype, )
        ids = request.forms.ids
        # 组织调用函数字典
        data_dic = { 'ids': ids, 'sjbmc': sjbmc }
        # 调用操作数据库函数
        result = data_del_service( data_dic )
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '删除失败！异常错误提示信息[%s]' % error_msg
    
    return result