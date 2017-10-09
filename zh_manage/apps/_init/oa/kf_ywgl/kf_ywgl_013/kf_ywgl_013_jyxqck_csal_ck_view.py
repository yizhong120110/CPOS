# -*- coding: utf-8 -*-
# Action: 自动化测试 子流程测试案例 查看view
# Author: 周林基
# AddTime: 2015-2-11
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback, json
from sjzhtspj import logger, request,render_to_string, render_string
from .kf_ywgl_013_jyxqck_csal_ck_service import index_service, data_del_csaldy_service


@register_url('GET')
def index_view():
    """
    # 自动化测试：测试案例查看页面
    """
    csaldyid = request.GET.csaldyid
    demoid = request.GET.demoid
    lx = request.GET.lx
    if lx == "zlc" or lx == '2' or lx == '4':
        data = index_service({'csaldyid': csaldyid, 'lb': ['2','4'], 'sslb': '2', 'lx': lx})
    elif lx == "jd" or lx == '3':
        data = index_service({'csaldyid': csaldyid, 'lb': ['3'], 'sslb': '3', 'lx': lx})
    else:
        data = index_service({'csaldyid': csaldyid, 'lb': ['1'], 'sslb': '1', 'lx': lx})
    data['demoid'] = demoid
    return render_to_string("kf_ywgl/kf_ywgl_013/kf_ywgl_013_jyxqck_csal_ck.html", data)

@register_url('POST')
def data_del_csaldy_view():
    """
    # 自动化测试：删除测试案例定义的测试案例信息
    """
    # ID
    csaldyid = request.POST.csaldyid
    data = {'state':False, 'msg':""}
    try:
        # 调用操作数据库函数
        data = data_del_csaldy_service( csaldyid )
    except:
        logger.info(traceback.format_exc())
        error_msg = traceback.format_exc()
        data['msg'] = '删除失败！异常错误提示信息[%s]' % error_msg
    return json.dumps(data)
    