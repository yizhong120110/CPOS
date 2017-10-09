# -*- coding: utf-8 -*-

import json
import traceback
from sjzhtspj import logger, request, render_to_string, get_sess
from .tcr_0002_service import data_service, force_exit_service
from libs_local.sjzhtspj.common import get_sess_hydm
from ops.core.rpc import call_jy_reply

@register_url('GET')
def index_view():
    """
    # 终端列表页面
    """
    data = {}

    return render_to_string('tcr_0002/tcr_0002.html', data)

@register_url('POST')
def data_view():
    """
    # 获取管理对象列表数据
    """
    # 数据结构
    data = {'total':0, 'rows':[]}
    try:
        # 组织查询信息
        # 翻页开始下标
        rn_start = request.rn_start
        # 翻页结束下标
        rn_end = request.rn_end
        # 请求字典
        sql_data = {'rn_start': rn_start, 'rn_end': rn_end}
        # 机构名称
        sql_data['jgmc'] = request.forms.jgmc
        # 终端名称
        sql_data['tcrmc'] = request.forms.tcrmc
        # 终端IP
        sql_data['tcrip'] = request.forms.tcrip
        # 状态
        sql_data['tcrst'] = request.forms.tcrst
        print(sql_data)

        # 调用service
        data = data_service(sql_data)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
    
    # 将结果反馈给前台
    return data

@register_url('POST')
def add_view():
    """
    # 添加终端
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}
    try:
        # 机构号
        tcrjgh = request.forms.tcrjgh
        # 机构名称
        tcrjgmc = request.forms.tcrjgmc
        # 虚拟柜员号
        tcrvgyh = request.forms.tcrvgyh
        # 终端号
        tcrid = request.forms.tcrid
        # 终端名称
        tcrname = request.forms.tcrname
        # 终端IP
        tcrip = request.forms.tcrip
        # 工作开始时间
        gzqssj = request.forms.gzqssj
        # 工作结束时间
        gzjssj = request.forms.gzjssj

        # 获取登录行员代码
        czgy = get_sess_hydm()
        # 获取登录行员所属机构码
        jyjgm = get_sess('jgbm')

        # 报文
        fsxx = {'ORDERID':'0','JGH':tcrjgh, 'JGMC2':tcrjgmc, 'VGYH':tcrvgyh,'TERMINAL_ID':tcrid, 'JGMC':tcrname, 'CIP':tcrip, 'GZQSSJ':gzqssj, 'GZJSSJ':gzjssj,'CZGY':czgy}
        buf = '%s%s%s' % (str(len(fsxx) + 20).ljust(4, ' '), 'TCR_2000'.ljust(16, ' '), json.dumps(fsxx))

        # 同步调起交易
        buf_fk = call_jy_reply('ZDFSSVR', buf.encode('UTF8'))
        # 检验反馈的报文前8位，前8位为“time out”表示交易超时
        if not buf_fk or buf_fk.decode('UTF8')[:8] == 'Timeout@':
            data['state'] = False
            data['msg'] = '查询超时'
            return data

        # 格式化反馈报文
        result = json.loads(buf_fk.decode('utf8'))
        if result.get('SYS_RspCode', '') != '000000':
            data['state'] = False
        else:
            data['state'] = True
        data['msg'] = result.get('SYS_RspInfo')
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
    
    # 将结果反馈给前台
    return data

@register_url('POST')
def edit_view():
    """
    # 修改终端
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}
    try:
        # 机构号
        tcrjgh = request.forms.tcrjgh
        # 机构名称
        tcrjgmc = request.forms.tcrjgmc
        # 虚拟柜员号
        tcrvgyh = request.forms.tcrvgyh

        # 终端号
        tcrid = request.forms.jkdx_id
        # 终端名称
        tcrname = request.forms.tcrname
        # 终端IP
        tcrip = request.forms.tcrip
        # 工作开始时间
        gzqssj = request.forms.gzqssj
        # 工作结束时间
        gzjssj = request.forms.gzjssj

        # 获取登录行员代码
        czgy = get_sess_hydm()
        # 获取登录行员所属机构码
        jyjgm = get_sess('jgbm')

        # 报文
        fsxx = {'ORDERID':'1','JGH':tcrjgh, 'JGMC2':tcrjgmc, 'VGYH':tcrvgyh, 'TERMINAL_ID':tcrid, 'JGMC':tcrname, 'CIP':tcrip, 'GZQSSJ':gzqssj, 'GZJSSJ':gzjssj,'CZGY':czgy}
        buf = '%s%s%s' % (str(len(fsxx) + 20).ljust(4, ' '), 'TCR_2000'.ljust(16, ' '), json.dumps(fsxx))

        # 同步调起交易
        buf_fk = call_jy_reply('ZDFSSVR', buf.encode('UTF8'))
        # 检验反馈的报文前8位，前8位为“time out”表示交易超时
        if not buf_fk or buf_fk.decode('UTF8')[:8] == 'Timeout@':
            data['state'] = False
            data['msg'] = '查询超时'
            return data

        # 格式化反馈报文
        result = json.loads(buf_fk.decode('utf8'))
        if result.get('SYS_RspCode', '') != '000000':
            data['state'] = False
        else:
            data['state'] = True
        data['msg'] = result.get('SYS_RspInfo')
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '新增失败！异常错误提示信息[%s]' % error_msg
    
    # 将结果反馈给前台
    return data

@register_url('POST')
def force_exit_view():
    """
    # 强制签退.
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}

    try:
        # SQL参数
        sql_param = {}
        # 终端ID
        sql_param['tcrid'] = request.forms.tcrid

        data = force_exit_service(sql_param)
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '强制签退失败！异常错误提示信息[%s]' % error_msg

    return data

@register_url('POST')
def able_view():
    """
    # 激活或注销终端
    """
    # 初始化返回值
    data = {'state':False, 'msg':''}
    try:
        orderid = ''
        # 终端号
        tcrid = request.forms.tcrid
        # ip
        tcrip = request.forms.tcrip
        # 状态
        zt = request.forms.zt
        # 工作起始时间
        gzqssj = request.forms.gzqssj
        # 工作结束时间
        gzjssj = request.forms.gzjssj
        # 机构名称
        jgmc = request.forms.jgmc
        if zt == '1':
            orderid = 3
        else:
            orderid = 2

        # 获取登录行员代码
        czgy = get_sess_hydm()
        # 获取登录行员所属机构码
        jyjgm = get_sess('jgbm')

        # 报文
        fsxx = {'ORDERID':orderid, 'TERMINAL_ID':tcrid, 'CIP': tcrip,'CZGY':czgy,'GZQSSJ':gzqssj,'GZJSSJ':gzjssj,'JGMC':jgmc}
        buf = '%s%s%s' % (str(len(fsxx) + 20).ljust(4, ' '), 'TCR_2000'.ljust(16, ' '), json.dumps(fsxx))

        # 同步调起交易
        buf_fk = call_jy_reply('ZDFSSVR', buf.encode('UTF8'))
        # 检验反馈的报文前8位，前8位为“time out”表示交易超时
        if not buf_fk or buf_fk.decode('UTF8')[:8] == 'Timeout@':
            data['state'] = False
            data['msg'] = '操作超时'
            return data

        # 格式化反馈报文
        result = json.loads(buf_fk.decode('utf8'))
        if result.get('SYS_RspCode', '') != '000000':
            data['state'] = False
        else:
            data['state'] = True
        data['msg'] = result.get('SYS_RspInfo')
    except:
        # 程序异常时，将异常抛出，写入到日志中
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '操作失败！异常错误提示信息[%s]' % error_msg
    
    # 将结果反馈给前台
    return data

