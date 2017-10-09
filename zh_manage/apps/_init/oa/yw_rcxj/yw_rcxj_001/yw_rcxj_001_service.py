# -*- coding: utf-8 -*-
# Action: 交易监控
# Author: zhangchl
# AddTime: 2015-04-13
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

# 数据库连接模块
from sjzhtspj import ModSql,render_string,response
# 引入公共模块：根据类型获取编码维护表信息，当前日期，翻译日期
from sjzhtspj.common import get_strftime,get_file_path,get_strftime2,get_xtcsdy
import os,json,urllib
#导出pdf的类库
#字体库
import reportlab.lib.fonts              
#canvas画图的类库
from reportlab.pdfgen.canvas import Canvas  
#用于定位的inch库，inch将作为我们的高度宽度的单位
from reportlab.lib.units import inch   
from .pdf_common_service import creat_pdf

def index_service( sql_data ):
    """
    # 初始化交易监控页面数据准备 service
    """
    # 当前日期
    sql_data['datetime'] = get_strftime()
    # 将结果反馈给view
    return sql_data

def data_zjjk_service():
    """
    # 主机巡检信息
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询获取需要监控的主机IP
        zjip_lst = ModSql.yw_rcxj_001.execute_sql_dict(db, "data_zjip")
        # 查询获取文件监控信息
        wjxt_xx = ModSql.yw_rcxj_001.execute_sql_dict(db, "data_wjxt")
        # 查询获取内存使用率信息
        ncsyl_xx = ModSql.yw_rcxj_001.execute_sql_dict(db, "data_ncsyl")
        # 查询获取CPU使用率
        cpusyl_xx = ModSql.yw_rcxj_001.execute_sql_dict(db, "data_cpusyl")
        # 查询获取磁盘使用率
        cpsyl_xx = ModSql.yw_rcxj_001.execute_sql_dict(db, "data_cpsyl")
    zxx_lst = []
    # wjxt_xx中的KEY值：jkzj_ip,jkdxlx,dxmc,yz,jkqk
    # 拼接字符串：Str_wjxt = 主机名称 + “(” + 监控主机IP + “):” +”文件系统” + “:” +对象名称;
    for xx in wjxt_xx:
        Str_wjxt =xx['zjmc']+'(' + xx['jkzj_ip'] + '):' +'文件系统' + ':' +xx['dxmc']
        zxx_lst.append({'jknr':Str_wjxt, 'yj':xx['yz'], 'jkqk':xx['jkqk'], 'ip':xx['jkzj_ip']})
    # ncsyl_xx中的KEY值：jkzj_ip,jkdxlx,dxmc,yz,jkqk
    # 拼接字符串：Str_ncsyl =主机名称 + “(” + 监控主机IP + “):” +”内存使用率”;
    for xx in ncsyl_xx:
        Str_ncsyl =xx['zjmc']+'(' + xx['jkzj_ip'] + '):' +'内存使用率'
        zxx_lst.append({'jknr':Str_ncsyl, 'yj':xx['yz'], 'jkqk':xx['jkqk'], 'ip':xx['jkzj_ip']})
    # cpusyl_xx中的KEY值：jkzj_ip,jkdxlx,dxmc,yz,jkqk
    # 拼接字符串：Str_cpusyl =主机名称 + “(” + 监控主机IP + “):” +”CPU使用率”
    for xx in cpusyl_xx:
        Str_cpusyl =xx['zjmc']+'(' + xx['jkzj_ip'] + '):' +'CPU使用率'
        zxx_lst.append({'jknr':Str_cpusyl, 'yj':xx['yz'], 'jkqk':xx['jkqk'], 'ip':xx['jkzj_ip']})
    # cpsyl_xx中的KEY值：jkzj_ip,jkdxlx,dxmc,yz,jkqk
    # 拼接字符串：Str_iosyl =主机名称 + “(” + 监控主机IP + “):” +”磁盘I/O使用率”;
    for xx in cpsyl_xx:
        Str_iosyl =xx['zjmc']+'(' + xx['jkzj_ip'] + '):' +'磁盘I/O使用率'
        zxx_lst.append({'jknr':Str_iosyl, 'yj':xx['yz'], 'jkqk':xx['jkqk'], 'ip':xx['jkzj_ip']})
    wjxt_lst = []
    for ip in zjip_lst:
        for xx in zxx_lst:
            if xx['ip'] == ip['zj_ip']:
                wjxt_lst.append(xx)
    data['rows'] = wjxt_lst
    data['total'] = len(wjxt_lst)
    # 将查询到的结果反馈给view
    return data

def data_sjkxj_service():
    """
    # Oracle数据库巡检信息
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    Sjk_list = []
    # 数据库链接
    with sjapi.connection() as db:
        # 查询获取需要的数据库巡检信息
        sjkxx_lst = ModSql.yw_rcxj_001.execute_sql_dict(db, "data_sjkjk")
    # sjkxx_lst中的KEY值：jkzj_ip,dxmc,yz,jkqk
    for xx in sjkxx_lst:
        Sjk_list.append({'bjkm':xx['dxmc'], 'yj':xx['yz'], 'bkjsybl':xx['jkqk']})
    data['rows'] = Sjk_list
    data['total'] = len(Sjk_list)
    # 将查询到的结果反馈给view
    return data
    
def data_jcxj_service():
    """
    # 进程巡检信息
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    jc_list = []
    # 数据库链接
    with sjapi.connection() as db:
        # 查询获取需要的进程巡检信息
        jcjkxx_lst = ModSql.yw_rcxj_001.execute_sql_dict(db, "data_jcjk")
    # sjkxx_lst中的KEY值：zjmc,zjip,jcmc
    #拼接字符串 Str_jc =主机名称 + “(” + 监控主机IP + “):” + “:” +进程名称
    for xx in jcjkxx_lst:
        Str_jc =xx['zjmc'] + '(' + xx['zjip'] + '):' +xx['jcmc']
        jc_list.append({'ptfujc':Str_jc})
    data['rows'] = jc_list
    data['total'] = len(jc_list)
    # 将查询到的结果反馈给view
    return data
    
def data_logxj_service():
    """
    # Tong中间件日志信息
    """
    # 初始化返回值
    data = {'total':0, 'rows':[]}
    # 数据库链接
    with sjapi.connection() as db:
        # 查询获取需要的Tong中间件日志信息
        # logjkxx_lst = ModSql.yw_rcxj_001.execute_sql_dict(db, "data_logjk")
        logjkxx_dic = get_xtcsdy( db, 'tong_log_file' )
    # logjkxx_lst中的KEY值：value
    # 拼接字符串Str_rzcj1 = “ls –lhtr” +参数值 + “Pktlog” + “|awk '{print $9"|"$5}'”
    # 拼接字符串Str_rzcj2 = “ls –lhtr” +参数值 + “TongLINK.log” + “|awk '{print $9"|"$5}'”
    # 拼接字符串Str_rzcj3 = “ls –lhtr” +参数值 + “Syslog” + “|awk '{print $9"|"$5}'”
    rzcjjg_lst = []
    if logjkxx_dic:
        # 命令中“|grep -i”是起到不区分大小写的作用
        Str_rzcj1 = 'ls -lhtr ' +logjkxx_dic['value'] + '|grep -i Pktlog' + " |awk \'{print $9\"|\"$5}\'"
        Str_rzcj2 = 'ls -lhtr ' +logjkxx_dic['value'] + '|grep -i TongLINK.log' + " |awk \'{print $9\"|\"$5}\'"
        Str_rzcj3 = 'ls -lhtr ' +logjkxx_dic['value'] + '|grep -i Syslog' + " |awk \'{print $9\"|\"$5}\'"

        # os.popen执行完的结果是一个对象，需要read()出来,数据结构： ['pktlog|1.8K\n']
        rzcj1 = os.popen(Str_rzcj1)
        Json_rzcj1 = json.dumps(rzcj1.read().split())
        for k in eval(Json_rzcj1):
            rzcjjg_lst.append(k)

        rzcj2 = os.popen(Str_rzcj2)
        Json_rzcj2 = json.dumps(rzcj2.read().split())
        for k in eval(Json_rzcj2):
            rzcjjg_lst.append(k)
            
        rzcj3 = os.popen(Str_rzcj3)
        Json_rzcj3 = json.dumps(rzcj3.read().split())
        for k in eval(Json_rzcj3):
            rzcjjg_lst.append(k)

    Rz_list = []
    for rzxx in rzcjjg_lst:
        rzxx_lst = rzxx.strip('\n').split('|')
        rzmc = rzxx_lst[0]
        rzdx = rzxx_lst[1]
        Rz_list.append({'rzmc':rzmc,'rzdx':rzdx})

    data['rows'] = Rz_list
    data['total'] = len(Rz_list)
    # 将查询到的结果反馈给view
    return data
    
def export_pdf_service(export_data):
    """
    # 导出pdf  service
    """
    export_data =  json.loads(export_data)
    data = {'state':True,'msg':'导出成功'}
    f_path = getPath()
    # 文件名称
    filename = '日常巡检报告'+get_strftime2()+'.pdf'
    # 下载路径
    real_path = f_path+filename
    # 主机监控内容
    zjjk_data = {'data':data_zjjk_service()['rows'],'title_code':['jknr','yj','jkqk']}
    # 表空间使用情况
    sjkxj_data = {'data':data_sjkxj_service()['rows'],'title_code':['bjkm','yj','bkjsybl']}
    # 平台进程检查表
    jc_data = {'data':export_data['jc_data'],'title_code':['ptfujc','jcgs','qdsj','qt']}
    # 平台进程检查表
    jcxjjg_data = {'data':export_data['jcxjjg'],'title_code':['jcxjjg']}
    # Tong中间件日志检查
    tong_data = {'data':export_data['tong_data'],'title_code':['rzmc','rzdx','bug']}
    # 分行特色业务平台系统交易情况
    jy_data = {'data':export_data['jy_data'],'title_code':['title','value']}
    # 分行特色业务平台系统交易异常情况
    jyyc_data = {'data':export_data['jyyc_data'],'title_code':['xh','ycms','ycyyjcs']}
    
    # 巡检小结
    xjxj_data = {'data':export_data['xjxj_data'],'title_code':['xjxj']}
    creat_pdf(real_path,[zjjk_data,sjkxj_data,jc_data,jcxjjg_data,tong_data,jy_data,jyyc_data,xjxj_data])
    #pdf的下载路径传送给前台，提供下载路径
    data['real_path'] = real_path
    
    return data
def getPath():
    """
    # 获取存放模板的路径
    """
    fpath = os.getcwd() + '/'
    return fpath
    
def pdf_head(canvas, headtext):
    #setFont是字体设置的函数，第一个参数是类型，第二个是大小
    canvas.setFont("Helvetica-Bold", 11.5)  
    #向一张pdf页面上写string
    canvas.drawString(1*inch, 10.5*inch, headtext)  
    #画一个矩形，并填充为黑色
    canvas.rect(1*inch, 10.3*inch, 6.5*inch, 0.12*inch,fill=1) 
    #画一条直线
    canvas.line(1*inch, 10*inch, 7.5*inch, 10*inch)
    
def data_down_service(filepath):
    """
    # 下载文件方法
    """
    # 写文件
    # 写文件路径
    # 首先处理路径
    if os.path.exists(filepath) == False:
        return render_string( "<script>alert('下载文件不存在！')</script>")
    # 总文档大小(默认第一个)
    fname_size = os.path.getsize(filepath)
    # 设置cookie名称fileDownload，值为true，路径是根目录/
    response.set_cookie("fileDownload", "true", path="/")
    response.set_header('Content-Type','image/jpeg')
    response.set_header('Content-Length' ,fname_size)
    response.set_header("Accept-Ranges", "bytes")
    fn = filepath.split('/')
    response.set_header('Content-Disposition', 'attachment; filename="%s"' % urllib.parse.quote(fn[len(fn)-1]))
    return open(filepath, 'rb')
        
def delDC_service(filepath):
    """
    # 删除文件
    """
    data = {'state':True, 'msg':'删除成功'}
    if os.path.exists(filepath):
        os.remove(filepath)
    return data
