# -*- coding: utf-8 -*-
# Action: 开发系统-代码下载 view
# Author: zhangchl
# AddTime: 2015-11-19
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback
from sjzhtspj import logger, request, render_string
from .kf_ywgl_025_service import dm_down_service_yw, dm_down_service_tx


@register_url('GET')
def dm_down_view():
    """
    # 业务详情-文档清单 下载
    """
    # 业务id
    ywid = request.GET.ywid
    # 通讯id
    txid = request.GET.txid
    # 下载失败，转url
    to_path = request.GET.to_path
    # 默认反馈：
    result = render_string( "<script>%s</script>" % to_path )
    try:
        # 下载类型
        downtype = request.GET.downtype
        # 下载文档清档id集合
        idstr = request.GET.idstr
        # 组织调用函数字典
        data_dic = { 'ywid': ywid, 'downtype': downtype, 'idstr': idstr, 'to_path': to_path, 'txid': txid }
        # 调用操作数据库函数
        if ywid:
            result = dm_down_service_yw( data_dic )
        else:
            result = dm_down_service_tx( data_dic )
        return result
    except:
        logger.info(traceback.format_exc())
        return result
    
    return result
