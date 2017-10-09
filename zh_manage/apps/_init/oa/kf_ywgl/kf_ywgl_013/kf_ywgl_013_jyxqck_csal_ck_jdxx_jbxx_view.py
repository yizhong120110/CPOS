# -*- coding: utf-8 -*-
# Action: 自动化测试 子流程测试案例 节点信息 输入输出查看 view
# Author: 周林基
# AddTime: 2015-2-13
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import request,render_to_string
from .kf_ywgl_013_jyxqck_csal_ck_jdxx_jbxx_service import index_service


@register_url('GET')
def index_view():
    """
    # 自动化测试：测试案例查看 节点信息查看页面
    """
    #data = {}
    jdcsalzxbzid = request.GET.jdcsalzxbzid
    demoid = request.GET.demoid
    data_dic = {'jdcsalzxbzid': jdcsalzxbzid,'demoid':demoid}
    data = index_service(data_dic)
    return render_to_string("kf_ywgl/kf_ywgl_013/kf_ywgl_013_jyxqck_csal_ck_jdxx_jbxx.html", data)
