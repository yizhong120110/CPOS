# -*- coding: utf-8 -*-
from sjzhtspj import request, redirect,ModSql
from sjzhtspj import settings
from sjzhtspj import render_to_string
from sjzhtspj import set_sess, get_sess_hydm, get_sess, set_sess_uuid
from sjzhtspj.common import cal_md5,get_strftime

import json

_ROUTE_CFG = { 'method' : 'POST' }
@register_app(__file__)
def view():
    """
    主页访问url
    """
    # 初始化返回结果
    with sjapi.connection() as se:
        username = request.forms.username
        password = request.forms.pwd
        dlxt = request.forms.hidxt
        if dlxt=='开发系统':
            dlxt_sql = 'kf'
        elif dlxt == '管理系统':
            dlxt_sql = 'gl'
        elif dlxt =='运行系统':
            dlxt_sql = 'yx'
        elif dlxt == '维护系统':
            dlxt_sql = 'wh'
        else:
            dlxt_sql=''
        # 密码加密
        md5_mm = cal_md5(password)
        if username:
            # 获取用户信息
            # sql = "select * from gl_hydy where hydm = '%(hydm)s' and mm = '%(mm)s'" % ({'hydm':username,'mm':md5_mm})
            # hyobj = se.execute(sql).fetchone()
            # user = hyobj and hyobj['hydm']
            hy_xx=ModSql.init.execute_sql_dict(se, "check_yhxx", {'hydm': username,'mm':md5_mm})
            # if user is None:
            if hy_xx is None or len(hy_xx)==0:
                return """<script>
                            alert('用户名或密码错误，请重新输入');
                            window.history.go(-1);
                </script>"""
            else:
                # 检索用户权限
                # sql_yhqx = "select qxid from gl_yhqxpz where yhid ='%(id)s' and " \
                #            "qxid in (select id from gl_cddy where ssxt='%(dlxt)s'and scbz='0') "\
                #            %({'id':hyobj['id'],'dlxt':dlxt_sql})
                # qxobj = se.execute(sql_yhqx).fetchone()
                # qx = qxobj and qxobj['qxid']
                hy_xx=hy_xx[0]
                yhqx_lst = ModSql.init.execute_sql_dict(se, "check_yhqx", {'id': hy_xx['id'],'dlxt':dlxt_sql})

                # if qx is None:
                if yhqx_lst is None or len(yhqx_lst)==0:
                    return """<script>
                            alert('登录用户没有当前系统的登录权限');
                            window.history.go(-1);
                    </script>"""
                else:
                    # 登录系统放到session中
                    set_sess("dlxt",str(dlxt))
                    # 行员代码放到session中
                    # set_sess("hydm",user)
                    set_sess("hydm",hy_xx['hydm'])
                    set_sess_uuid()
                     # 获取机构代码信息
                    jgobj = ModSql.init.execute_sql_dict(se, "checksession", {'hydm': username})
                    if len(jgobj):
                        jgobj=jgobj[0]
                        # 机构代码放到session中
                        set_sess("jgbm",jgobj['bm'])
                        set_sess("jgmc",jgobj['bmmc'])
                        set_sess("bmid",jgobj['bmid'])
                        set_sess("bmcbm",jgobj['cbm'])
                        set_sess("hyid",jgobj['id'])
                    #  更新行员定义表中的登录次数，最新登录日期
                    # 最后登录时间
                    zhdlsj = get_strftime()
                    if hy_xx['dlcs']:
                        dlcs = hy_xx['dlcs'] + 1
                    else:
                        dlcs=1
                    # ModSql.init.execute_sql_dict(se, "update_hy", {'hydm':username,'zhdlsj':zhdlsj,'dlcs':dlcs})
                    sql_update = """
                                  update gl_hydy set zhdlsj = '%(zhdlsj)s',
                                  dlcs = '%(dlcs)s'
                                  where hydm = '%(hydm)s'
                    """ % ({'hydm':username,'zhdlsj':zhdlsj,'dlcs':dlcs})
                    se.execute(sql_update)
                    se.commit()
                    return  redirect("/")
        else:
            return """<script>
                            alert('用户名或密码为空，请重新输入');
                            window.history.go(-1);
                </script>"""
