# -*- coding: utf-8 -*-
from bottle import request
from cpos3.conf import settings
from cpos3.bottleext.mako import render_to_string
from sjzhtspj import register, ModSql
import json

_ROUTE_CFG = { 'method' : 'GET' }
@register_app(__file__)
def view():
    """
    主页访问url
    """
 #    data = [
 #          { "id": 1,"text": "开发系统","children": [
 #                 { "id": 11, "text": "业务管理", "pid": 1,"url" : "/oa/kf_ywgl/kf_ywgl_001/kf_ywgl_001_view/index_view" },
 #                 { "id": 12, "text": "通讯管理", "pid": 1,"url" : "/oa/kf_txgl/kf_txgl_001/kf_txgl_001_view/index_view" },
 #                 { "id": 13, "text": "节点管理", "pid": 1,"url" : "/oa/kf_jdgl/kf_jdgl_001/kf_jdgl_001_view/index_view" },
 #                 { "id": 14, "text": "系统参数管理", "pid": 1,"url" : "/oa/kf_csgl/kf_csgl_001/kf_csgl_001_view/index_view" }
 #             ], "url":"" },
 #          { "id": 2, "text": "管理系统","children": [
 #                 { "id": 21, "text": "角色管理", "pid": 2,"url" : "/oa/gl_jsgl/gl_jsgl_001/gl_jsgl_001_view/index_view" },
 #                 { "id": 22, "text": "部门管理", "pid": 2,"url" : "/oa/gl_bmgl/gl_bmgl_001/gl_bmgl_001_view/index_view" },
 #                 { "id": 23, "text": "用户管理", "pid": 2,"url" : "/oa/gl_yhgl/gl_yhgl_001/gl_yhgl_001_view/index_view" },
 #                 { "id": 24, "text": "菜单管理", "pid": 2,"url" : "/oa/gl_cdgl/gl_cdgl_001/gl_cdgl_001_view/index_view" },
 #                 { "id": 25, "text": "用户权限", "pid": 2,"url" : "/oa/gl_yhqx/gl_yhqx_001/gl_yhqx_001_view/index_view" },
 #                 { "id": 26, "text": "角色权限", "pid": 2,"url" : "/oa/gl_jsqx/gl_jsqx_001/gl_jsqx_001_view/index_view" },
 #                 { "id": 27, "text": "密码管理", "pid": 2,"url" : "/oa/gl_mmgl/gl_mmgl_001/gl_mmgl_001_view/index_view" }
 #          ]},
 #          { "id": 3, "text": "运行系统","children": [
 #                 { "id": 301, "text": "交易监控", "pid": 3,"url": "/oa/yw_jyjk/yw_jyjk_001/yw_jyjk_001_view/index_view?pt=yx" },
 # #                { "id": 302, "text": "自动交易监控管理" , "pid": 3,"url" : "html/ywpt/jyjk/jyjk.html" },
 #                 { "id": 303, "text": "数据表信息查看" , "pid": 3,"url" : "/oa/yw_dsiv/yw_dsiv_001/yw_dsiv_001_view/index_view" },
 # #                { "id": 304, "text": "通讯监控流水" , "pid": 3,"url" : "html/qfwjk/txjk/txjk_jdhb.html" },
 # #                { "id": 305, "text": "数据库监控流水" , "pid": 3,"url" : "html/qfwjk/sjkjk/sjkjk_jkjl.html" },
 # #                { "id": 306, "text": "交易失败率监控流水" , "pid": 3,"url" : "html/qfwjk/jysbl/jysbl_jkjl.html" },
 # #                { "id": 307, "text": "日志监控流水" , "pid": 3,"url" : "html/qfwjk/rzjk/rzjk_jkls.html" },
 # #                { "id": 308, "text": "文件监控流水" , "pid": 3,"url" : "html/qfwjk/wjjk/wjjk_jkls.html" },
 # #                { "id": 309, "text": "GTP监控流水" , "pid": 3,"url" : "html/qfwjk/gtpjk/gtpjk_jkls.html" },
 # #                { "id": 311, "text": "自定义交易监控流水" , "pid": 3,"url" : "html/qfwjk/zdyjk/zdyjk_jylb.html" },
 #                 { "id": 312, "text": "行员日常运维流水" , "pid": 3,"url" : "/oa/yw_hycz/yw_hycz_001/yw_hycz_001_view/index_view" },
 #                  {"id": 313, "text": "知识库主页", "pid": 3,"url": "/oa/yw_kbmn/yw_kbmn_001/yw_kbmn_001_view/index_view" }
 #
 #             ], "url":"" },
 #          { "id": 4, "text": "维护系统","children": [
 # #                { "id": 4001, "text": "监控定义", "pid": 4,"url": "html/qfwjk/jkdy/jkdy.html" },
 # #                { "id": 4002, "text": "预警定义", "pid": 4,"url": "html/qfwjk/yjdy/yjdy.html" },
 # #                { "id": 401, "text": "通讯监控", "pid": 4,"url": "html/qfwjk/txjk/txjk.html" },
 # #                { "id": 402, "text": "数据库监控", "pid": 4,"url": "html/qfwjk/sjkjk/sjkjk.html" },
 # #                { "id": 403, "text": "交易失败率监控", "pid": 4,"url": "html/qfwjk/jysbl/jysbl.html" },
 # #                { "id": 404, "text": "日志监控", "pid": 4,"url": "html/qfwjk/rzjk/rzjk.html" },
 # #                { "id": 405, "text": "文件监控", "pid": 4,"url": "html/qfwjk/wjjk/wjjk.html" },
 # #                { "id": 406, "text": "通用GTP监控", "pid": 4,"url": "html/qfwjk/gtpjk/gtpjk.html" },
 # #                { "id": 407, "text": "自定义交易监控", "pid": 4,"url": "html/qfwjk/zdyjk/zdyjk.html" },
 # #                { "id": 408, "text": "接口有效性校验", "pid": 4,"url": "html/qfwjk/jkyxxjy/jkyxxjy.html" },
 # #                { "id": 409, "text": "限流设置", "pid": 4,"url": "html/qfwjk/xlsz/xlsz.html" },
 #                  { "id": 410, "text": "大屏监控" , "pid": 4,"url" : "/oa/yw_sscf/yw_sscf_001/yw_sscf_001_view/index_view" },
 #                  { "id": 411, "text": "参数设置" , "pid": 4,"url" : "/oa/yw_csgl/yw_csgl_001/yw_csgl_001_view/index_view" },
 # #                { "id": 412, "text": "行员日常运维流水" , "pid": 3,"url" : "html/qfwjk/ywls/ywls.html" },
 #                  { "id": 413, "text": "特色业务系统巡检记录" , "pid": 4,"url" : "/oa/yw_rcxj/yw_rcxj_001/yw_rcxj_001_view/index_view" },
 #                  { "id": 414, "text": "计划任务管理" , "pid": 4,"url" : "/oa/yw_jhrw/yw_jhrw_001/yw_jhrw_001_view/index_view" },
 #                  { "id": 415, "text": "监控对象管理" , "pid": 4,"url" : "/oa/yw_jkgl/yw_jkgl_002/yw_jkgl_002_view/index_view" },
 #                  { "id": 410, "text": "分析规则管理" , "pid": 4,"url" : "/oa/yw_jkgl/yw_jkgl_003/yw_jkgl_003_view/index_view" },
 #                  { "id": 416, "text": "响应动作管理" , "pid": 4,"url" : "/oa/yw_jkgl/yw_jkgl_004/yw_jkgl_004_view/index_view" },
 #                  { "id": 417, "text": "阈值流水校验" , "pid": 4,"url" : "/oa/yw_gtpm/yw_gtpm_003/yw_gtpm_003_view/index_view" },
 #                  { "id": 406, "text": "GTP_业务配置" , "pid": 4,"url" : "/oa/yw_gtpm/yw_gtpm_002/yw_gtpm_002_view/index_view" },
 #                  { "id": 418, "text": "数据采集配置管理" , "pid": 4,"url" : "/oa/yw_jkgl/yw_jkgl_005/yw_jkgl_005_view/index_view" },
 #                  {"id": 419, "text": "阈值校验配置", "pid": 4,"url": "/oa/yw_gtpm/yw_gtpm_001/yw_gtpm_001_view/index_view" },
 #                  {"id": 420, "text": "主机详细信息监控", "pid": 4,"url": "/oa/yw_sscf/yw_sscf_002/yw_sscf_002_view/index_view" },
 #                  {"id": 421, "text": "监控管理-监控配置", "pid": 4,"url": "/oa/yw_jkgl/yw_jkgl_006/yw_jkgl_006_view/index_view" },
 #                  {"id": 422, "text": "子账号维护", "pid": 4,"url": "/oa/jn_ywgl/jn_ywgl_004/jn_ywgl_004_view/index_view" }
 #             ], "url":"" }
 #    ]
    # 初始化返回结果
    # 获取前台传入的行员代码和行员id
    id = request.GET.id
    dlxt = request.GET.dlxt
    with sjapi.connection() as db:
       lst=[]
       # 获取菜单列表
       cd_lst = ModSql.init.execute_sql_dict(db, "data_cd_rs")
       data_dic = {'fjdid':'0'}
       # 获取用户拥有的菜单权限
       data_lst = ModSql.init.execute_sql_dict(db, "get_cdqx", {'id': id})
       qx_lst = [row['id'] for row in data_lst]
       if qx_lst:
           get_fjdidlb(cd_lst,qx_lst,lst)
       last = []
       for i in lst:
           last.extend(i)
       if last:
           qx_lst.extend(last)
           qx_lst = list(set(qx_lst))

       sql_data = {'ids':qx_lst}
       yhqx_lst= ModSql.init.execute_sql_dict(db, "data_cd_lst", sql_data)

       if dlxt =='开发系统':
           data_dic = {'pid':'kf'}
           pid='kf'
       elif dlxt=='管理系统':
           data_dic = {'pid':'gl'}
           pid='gl'
       elif dlxt =='运行系统':
           data_dic = {'pid':'yx'}
           pid='yx'
       else:
           data_dic = {'pid':'wh'}
           pid='wh'
       #     调用递归函数-构建树
       tree_view(yhqx_lst,pid,data_dic)
       if data_dic.get('children'):
           data = data_dic['children']
       else:
           data=[]
    return json.dumps(data)

def tree_view(lst,pId,k):
    """
    # 获取树结构
    :return:
    """
    aLst=[]
    for m in lst:
        if m['pid'] == pId:
            aLst.append(m)
    if aLst:
        k['children']=aLst
        for l in aLst:
            tree_view(lst,l['id'],l)

def get_fjdidlb(ylst,jd_lst,lst):
    """
    # 获取父节点列表
    :return:
    """
    aLst=[]
    for m in ylst:
        if m['id'] in jd_lst:
            aLst.append(m)
    if aLst:
        fjdid_lst = [k['pid'] for k in aLst]
        lst.append(fjdid_lst)
        get_fjdidlb(ylst,fjdid_lst,lst)
    else:
        return  lst
