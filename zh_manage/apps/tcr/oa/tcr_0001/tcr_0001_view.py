# -*- coding: utf-8 -*-

import traceback,json
from libs_local.sjzhtspj import get_sess
from libs_local.sjzhtspj.common import get_sess_hydm
from ops.core.rpc import call_jy_reply
from sjzhtspj import request, render_to_string, logger

@register_url('GET')
def index_view():
    data = {}
    return render_to_string("tcr_0001/tcr_0001.html", data)

@register_url('POST')
def get_request():
    """
    # 联盟核心同步密钥
    """
    # 数据结构
    data = {'state':True}
    try:
        # 获取登录行员代码
        czgy = get_sess_hydm()
        # 获取登录行员所属机构码
        jyjgm = get_sess('jgbm')
        # 报文
        fsxx = {'CZGY':czgy, 'JYJGM':jyjgm}
        buf = '%s%s%s' % (str(len(fsxx) + 20).ljust(4, ' '), 'TCR_9901'.ljust(16, ' '), json.dumps(fsxx))

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
        data['state'] = False
        data['msg'] = '同步密钥异常！【%s】' % error_msg

    # 反馈信息
    return data
