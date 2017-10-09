# -*- coding: utf-8 -*-
# Action: 自动化测试 子流程测试案例 节点信息查看view
# Author: 周林基
# AddTime: 2015-2-12
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import logger, request, render_to_string
from .kf_ywgl_013_jyxqck_csal_ck_jdxx_service import index_service, jd_index_service


@register_url('GET')
def index_view():
    """
    # 自动化测试：测试案例查看 节点信息查看页面
    """
    csaldyid = request.GET.csaldyid
    lx = request.GET.lx
    demoid = request.GET.demoid
    data_dic = {'csaldyid': csaldyid, 'lx': lx}
    data = index_service(data_dic)
    if lx == "jd":
        data_dic = {'jdcsalzxbzid': data['jdcsalzxbzid']}
        data = jd_index_service(data_dic)
        data['demoid'] = demoid
        return render_to_string("kf_ywgl/kf_ywgl_013/kf_ywgl_013_jyxqck_csal_ck_jdxx_jbxx.html", data)
    else:
        data['demoid'] = demoid
        return render_to_string("kf_ywgl/kf_ywgl_013/kf_ywgl_013_jyxqck_csal_ck_jdxx.html", data)
