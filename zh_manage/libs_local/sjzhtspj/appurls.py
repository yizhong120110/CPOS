# -*- coding: utf-8 -*-
"""
    url的通用处理部分
"""
import os, sys
from bottle import install, route
from cpos3.conf import settings
from cpos3.backplat.utils.modulehelper import getModule
from cpos3.utils.ftools import register
from cpos3.utils.ospath import walk as os_path_walk
from cpos3.modelsql.sqlxml import MapperList, readxml
from cpos3.utils.ftools import AttrDict
from mako.template import Template
from . import APPS_DIR
import threading

def get_module_name(fname, sub):
    #@param: fname 要拆分的文件的完整路径
    #@param:sub    拆分
    if 'win' in sys.platform:
        fname = fname.lower()
        sub = sub.lower()
    l = list(filter(None, fname.split(sub)))
    try:
        sub_fname = l[0]
        l_sub = list(filter(None, sub_fname.split(os.sep)))
        return l_sub[0]
    except:
        raise Exception('有误', l)


@register()
# 是因为register_app(__file__)的使用方式使得他需要_call2吗？
def register_app(fname):
    # _call 这一层应该是为了避免每次执行函数时都做一次处理，浪费资源
    def _call(func):
        # 计算出模块的名字
        # 使用func.__module__替换这个函数 todo
        # func.__module__ 可以得到这个函数的实际位置，从pythonpath中配置的路径开始计算
        app_name = get_module_name(fname, APPS_DIR)

        # _call2这一层才是在调用的时候才会执行的
        def _call2(*args, **kwargs):
            # 将_T.APP_NAME写在这里，应该是避免将settings中的值冲掉吧
            settings._T = AttrDict({"APP_NAME":app_name}) # 2015-12-11 add by msc
            ret = func(*args, **kwargs)
            return ret

        return _call2

    return _call


##函数 register_modelsql
##    参数：  modelid 字符串 模块编号，对应MapperList中的modelsid
##    返回值：函数体
##    功能描述：
##        使用函数注释的方式，对url做处理
##        将可提供sql语句的ModelsSQL对象MS放到settings._T中
#@register()
## 这个是绑定在url上的，不是对单个被调用函数生效的
#def register_modelsql(modelid):
#    def _call(func):
#        # 计算出模块的名字
#        app_name = func.__module__.split('.')[0]
#
#        def _call2(*args, **kwargs):
#            settings._T.APP_NAME = app_name
#            # 从settings中取出期望的modelid对象
#            appmodelnm = 'appname_%s' % app_name
#            setattr(settings._T, 'MS', eval("settings.%s.modelid_%s" % (appmodelnm, modelid)))
#            ret = func(*args, **kwargs)
#            return ret
#
#        return _call2
#
#    return _call


@register()
# 为了将修饰的函数变成url映射的一部分
def register_url(method="GET"):
    _ROUTE_CFG = {'method': method}

    def _call(func):
        # 完整的func模块信息
        modfuncname = '.'.join([func.__module__, func.__name__])
        url = get_url_by_modfunc(modfuncname)
        # 对route的plugin操作
        plugin_lst = settings.yy_plugins.get('all', [])
        app_name = func.__module__.split('.')[0]
        plugin_lst.extend(settings.yy_plugins.get(app_name, []))

        # 对url映射关系登记到settings中
        record_url_map(url, modfuncname)
        def _call2(*args, **kwargs):
            # 将_T.APP_NAME写在这里，应该是避免将settings中的值冲掉吧
            settings._T = AttrDict({"APP_NAME":app_name})
            ret = func(*args, **kwargs)
            return ret
            
        if plugin_lst:
            route(url, callback=_call2, apply=plugin_lst, **_ROUTE_CFG)
        else:
            route(url, callback=_call2, **_ROUTE_CFG)
            
        return _call2

    return _call


# 通过函数模块得到url串
def get_url_by_modfunc(modfuncname):
    url = ''
    # 原始 /_init/_index    ==》 /
    # 原始 /_init/*         ==》 /*
    # 原始 /_init/*/_index  ==》 /*/_index
    # 原始 /*/_index        ==》 /*/_index
    if modfuncname == '_init.index':
        return '/'
    else:
        urllst = modfuncname.split('.')
        if urllst[0] == '_init':
            urllst = urllst[1:]
        return '/' + '/'.join(urllst)


# 记录url和func的关系到settings中
def record_url_map(url, modfuncname):
    class UrlMap(object):
        def __init__(self):
            self._dict = {}
            makostr = """
<?xml version="1.0"?>
<urlmap>
%for urlstr in sorted(urlmapdic.keys()):
  %for modname in sorted(urlmapdic[urlstr]['modfuncname']):
    <urlmod urlcnt="${urlmapdic[urlstr]['cnt']}" urlstr="${urlstr}" modname="${modname}" />
  %endfor
%endfor
</urlmap>
            """
            self.tpl = Template(makostr)

        def add_url(self, url, modfuncname):
            if not self._dict.get(url):
                self._dict[url] = {'modfuncname': [], 'cnt': 0}
            self._dict[url]['cnt'] += 1
            self._dict[url]['modfuncname'].append(modfuncname)

        @property
        def get_url_all(self):
            # 这里直接返回一个XML字符串
            return self.tpl.render(urlmapdic=self._dict)

        def get_url_err(self):
            # 仅提供cnt>1的
            tdic = {}
            for k in self._dict.keys():
                if self._dict[k]['cnt'] > 1:
                    tdic[k] = self._dict[k]
            return self.tpl.render(urlmapdic=tdic), bool(tdic)

    # 使用一个类对象来登记、检查url的映射关系
    if settings.urlmap is None:
        settings.urlmap = UrlMap()
    settings.urlmap.add_url(url, modfuncname)
    return True


def get_plugins(plugins, yy_plugins={}):
    """
    获取出来plugins应用到哪些子应用上的信息
    """
    #根据设置的PLUGINS信息加载模块和其下的函数
    for module in plugins.keys():
        #模块名+函数名
        yy_mc = plugins.get(module)
        mod_lst = module.split('.')
        # plugins是bin同级目录
        mod = getModule("plugins." + module)
        func = getattr(mod, mod_lst[-1])
        func_obj = func()

        ##此处需要判断下yy_mc如果是空列表，才install，否则只匹配到具体子应用的url上
        if yy_mc:
            for mc in yy_mc:
                if mc not in yy_plugins:
                    yy_plugins[mc] = []
                    yy_plugins[mc].append(func_obj)
                else:
                    yy_plugins[mc].append(func_obj)
        else:
            install(func_obj)
            yy_plugins['all'] = [func_obj]
    return yy_plugins


def ls_files(dirname, files, dname, yy_plugins):
    """
    对指定目录下的所有文件进行解析，并组织好数据放到数据结构中
    循环处理文件目录
    进行特殊处理
    加载route的配置信息post/get
    加载plugin
    绑定route
    """
    #获取URL前缀基础部分
    basepath = ["/" + dname]
    #获取BASEPATH路径
    #print '*********',dname,dirname,files
    ##调试状态下目录找debug ， 否则用pyc
    for filename in files:
        #log.info( "gm" , "检测到目录名[%s]" , dirname )
        if filename.startswith('_') and filename.endswith('.py') and filename != "__init__.py":
            #log.info( "gm" , "将目录[%s]下的文件名[%s]映射成URL" , dirname , filename )
            ml_lst = []
            mod_lst = [] #导入模块
            url = ""
            ap1 = dirname.split('apps' + os.sep + dname)[1]
            ap1 = list(filter(None, ap1.split(os.sep)))

            if dname == '_init':
                ml_lst = ['']
                ml_lst.extend(ap1)
                #特殊处理 为了初次访问系统时使用 如http://46.17.189.251
                # 2015-01-21 shhx 感觉这里是写错了，似乎应该仅仅特殊处理/_init/_index 和/_init，而不是/_init/*/_index
                # 决定纠正这个问题
                # 原始 /_init/_index    ==》 /
                # 原始 /_init/*         ==》 /*
                # 原始 /_init/*/_index  ==》 /*/_index
                # 原始 /*/_index        ==》 /*/_index
                # 之后对url进行检查，启动前将重复url抛出
                if filename == "_index.py" and len(list(filter(None, ml_lst))) == 0:
                    ml_lst.append('')
                else:
                    ml_lst.append(filename[1:-3])
            else:
                ml_lst.extend(basepath)
                ml_lst.extend(ap1)
                ml_lst.append(filename[1:-3])
            url = "/".join(ml_lst)
            mod_lst.append(dname)
            mod_lst.extend(ap1)
            mod_lst.append(filename[:-3])

            #print 'url*****',ml_lst,url
            #log.info( "gm" , "目录[%s]下的文件名[%s]映射成URL的值为[%s]" , dirname , filename , url  )
            #引入url对应的模块
            if mod_lst:
                u_mod = getModule(".".join(mod_lst))
            _ROUTE_CFG = {}
            if hasattr(u_mod, '_ROUTE_CFG'):
                _ROUTE_CFG = getattr(u_mod, '_ROUTE_CFG')
                ##此处需要判断如果没有定义view函数，是否直接报错出来？？？？
            u_func = getattr(u_mod, 'view')
            plugin_lst = yy_plugins.get('all', [])
            plugin_lst.extend(yy_plugins.get(dname, []))
            #研究下空列表是否会冲掉全局的installtodo.....
            # 这种模式的固定登记函数为view即可
            record_url_map(url, ".".join(mod_lst) + '.view')
            if plugin_lst:
                route(url, callback=u_func, apply=plugin_lst, **_ROUTE_CFG)
            else:
                route(url, callback=u_func, **_ROUTE_CFG)
        elif filename.endswith('.py'):
            mod_lst = [] #导入模块
            ap1 = dirname.split('apps' + os.sep + dname)[1]
            ap1 = list(filter(None, ap1.split(os.sep)))
            mod_lst.append(dname)
            mod_lst.extend(ap1)
            mod_lst.append(filename[:-3])
            if mod_lst:
                u_mod = getModule(".".join(mod_lst))
            pass
            #log.info( "gm" , "目录[%s]下的文件名[%s]不符合URL映射规则，跳过" , dirname , filename )


def add_app_urls(dirpath, walk_func, yy_plugins={}, not_static_apps=[]):
    """
    加载APPS_DIR下每个app的文件对应url
    walk_func 在做os_path_walk时，每层要执行的函数
    """
    for appname in os.listdir(dirpath):
        # 需要先是目录，然后排除部分情况
        if os.path.isdir(os.path.join(dirpath, appname)) == True and appname not in not_static_apps:
            # 遍历每个子应用的目录结构，且此函数只遍历一个子应用根目录下的所有文件
            os_path_walk(os.path.join(dirpath, appname), walk_func, appname, yy_plugins)
    return True
