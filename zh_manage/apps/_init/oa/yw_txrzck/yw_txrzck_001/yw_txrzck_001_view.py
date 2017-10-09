# -*- coding: utf-8 -*-
# Action: 通讯日志查看 主页面 view
# Author: pansy
# AddTime: 2016-01-21
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

import traceback,json,os
from sjzhtspj.common import format_log
from sjzhtspj import logger, request,render_to_string,TMPDIR, response
from .yw_txrzck_001_service import ( 
    data_service, get_rz_service )


@register_url('GET')
def index_view():
    """
    # 通讯日志查看-通讯展示
    """
    return render_to_string("yw_txrzck/yw_txrzck_001/yw_txrzck_001.html")

@register_url('GET')
def data_view():
    """
    # 通讯日志查看-通讯展示 列表初始化
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    try:
        # 翻页
        rn_start = request.rn_start
        rn_end = request.rn_end
        # 组织调用函数字典
        data_dic = { 'rn_start': rn_start, 'rn_end': rn_end }
        # 调用操作数据库函数
        data = data_service( data_dic )
    except:
        logger.info(traceback.format_exc())
        
    return data
    
@register_url('POST')
def data_rzck_view():
    """
    # 通讯管理-日志查看 view
    """
    # 反馈信息
    result = {'state':True, 'msg':'', 'rz': ''}
    try:
        # 交易日期
        jyrq = request.forms.seaJyrq
        jyrq = jyrq.replace('-','')
        # 开始时间
        kssj = request.forms.kssj
        # 结束时间
        jssj = request.forms.jssj
        # 通讯文件名称
        txwjmc = request.forms.txwjmc
        if txwjmc[-3:] == '.py':
            txwjmc = txwjmc[0:-3]
        # 组织调用函数字典
        data_dic = { 'jyrq': jyrq,
            'kssj': kssj,
            'jssj': jssj,
            'txwjmc':txwjmc 
            }
        # 调用操作数据库函数
        result['rz'] = get_rz_service( data_dic )
        if result['rz'] == 'error':
            result['state'] = False
#        else:
#            result['rz'] = format_log(result['rz'])
            
    except:
        result['state'] = False
        error_msg = traceback.format_exc()
        logger.info(error_msg)
        result['msg'] = '查询日志失败！异常错误提示信息[%s]' % error_msg  
    return result
 
@register_url('GET')
def data_rzdc_view():
    """
    # 导出日志日志
    """
    # 初始化反馈信息
    # rznr： 日志内容
    try:
        # 交易日期
        jyrq = request.GET.jyrq
        jyrq = jyrq.replace('-','')
        # 开始时间
        kssj = request.GET.kssj
        # 结束时间
        jssj = request.GET.jssj
        # 通讯文件名称
        txwjmc = request.GET.txwjmc
        if txwjmc[-3:] == '.py':
            txwjmc = txwjmc[0:-3]
        # 调用操作数据库函数
        data_dic = { 'jyrq': jyrq,
            'kssj': kssj,
            'jssj': jssj,
            'txwjmc':txwjmc 
            }
        if jssj != '':
            jssj = '_' + jssj
        # 调用操作数据库函数
        rznr = get_rz_service( data_dic )
        if rznr == 'error':
            return rznr
        # 日志文件名称
        dow_fname = filename = '%s_%s%s_%s.log' % ( jyrq, kssj, jssj, txwjmc )
        # 日志全路径（ 放到临时文件中 ）
        filepath = os.path.join(TMPDIR,filename)
        # 创建文件对象，写文件
        fileobj = open(filepath, 'w')
        fileobj.write( rznr )
        fileobj.close()
        # 将文件反馈给前台进行下载
        # 下载文件名称（ filename ）
        # 下载文件路径
        root = TMPDIR
        import time ,datetime
        # 设置cookie名称fileDownload，值为true，路径是根目录/
        response.set_cookie("fileDownload", "true", path="/")
        response.set_header('Content-Type','image/jpeg')
        root = os.path.abspath(root) + os.sep
        filename = os.path.abspath(os.path.join(root, filename.strip('/\\')))
        stats = os.stat(filename)
        response.set_header('Content-Length' ,stats.st_size)
        lm = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(stats.st_mtime))
        response.set_header('Last-Modified', lm)
        response.set_header('Date', time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()))
        response.set_header("Accept-Ranges", "bytes")
        download = os.path.basename(filename)
        import urllib
        response.set_header('Content-Disposition', 'attachment; filename="%s"' % urllib.parse.quote(dow_fname))
        # 下载文件
        return open(filename, 'rb')
        
    except:
        error_msg = traceback.format_exc()
        logger.info(error_msg)