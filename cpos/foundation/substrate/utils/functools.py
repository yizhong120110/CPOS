# -*- coding: utf-8 -*-
"""
定义函数工具
"""
import warnings
import textwrap
import io as cStringIO
import builtins as __builtin__
import inspect
import textwrap
import ctypes
import sys
import os
import psutil
from .logger import logger


def py2func(code, modules=[], func_args=(), name='<string>'):
    # 指定参数列表,然后将代码块转变为标准函数
    code = textwrap.dedent(code.replace('\r', ''))  # 转换为标准linux格式
    clines = code.split('\n')
    cs = ["def func( " + ' , '.join(func_args) + " ):"]
    cs.extend(['    try:'])
    cs.extend(['        ' + x for x in modules + clines])
    cs.extend(['        pass'])  # 防止纯回车，导致出错
    cs.extend(['    except:'])
    cs.extend(['        import sys ,traceback'])
    cs.extend(['        exc = sys.exc_info()'])
    cs.extend(['        traceback.print_exception( *exc )'])      # 输出错误信息
    cs.extend(["        print('错误信息中提示的func中的line值比实际多3')"])
    cs.extend(['        raise'])
    funcbody = '\n'.join(cs).strip()
    # print('======================\n',funcbody,'\n======================')
    # compile 编译源到代码或AST对象
    c = compile(funcbody, name, 'exec')
    exec(c, globals())
    return func


class Namespace:
    # 用于提供注册到系统中扩展函数的名字空间

    @staticmethod
    def create(name):
        if not name:
            __builtin__.ns_modules = {}
            return __builtin__

        root = __builtin__
        path = []
        for x in name.split('.'):
            path.append(x)
            if hasattr(root, x):
                root = getattr(root, x)
            else:
                ns = Namespace('.'.join(path))
                setattr(root, x, ns)
                root = ns

        return root

    def __init__(self, name):
        self.__name = name
        self.ns_modules = {}

    def __str__(self):
        return self.__name


def _register(spc, obj):
    if inspect.isfunction(obj):
        name = getattr(obj, 'name', obj.__name__)
    elif inspect.isclass(obj):
        name = obj.__name__
    else:
        raise RuntimeError('名字空间中只可注册函数或类[%s]' % str(type(obj)))

    if name in spc.ns_modules and obj.__module__ != spc.ns_modules[name]:
        warnings.warn('已经在[%s]名字空间中注册了函数[%s]' % ( spc, name), RuntimeWarning)
        #raise RuntimeError( '已经在[%s]名字空间中注册了函数[%s]' % ( spc , name ) )
        return

    spc.ns_modules[name] = obj.__module__
    setattr(spc, name, obj)


def register(namespace=None):
    if type(namespace) in ( tuple, list):
        ns = map(Namespace.create, namespace)
    else:
        ns = ( Namespace.create(namespace), )
        #print ('register ---------------',ns)

    def _reg(func):
        #        # TODO 此处的注释很奇怪, 貌似是为了规避什么问题. 但历史太过久远. 暂时封闭下面代码, 有问题再打开
        #        if func.__module__ == '__main__':
        #            return func

        for n in ns:
            _register(n, func)
        return func

    return _reg


def isicm(pid, substr="icm/app.py", params={}):
    """
        判断是否是ICM进程，如果是，后续需要对所有pid做遍历删除
    """
    if substr in params.get("appfilepath", ""):
        return True
    r = os.popen("ps -fp %s" % pid)
    s = cStringIO.StringIO(r.read())
    for line in s:
        if substr in line:
            return True
    return False


def kill_ICM(substr="icm/app.py"):
    """
        对于ICM的专用kill方法
    """
    try:
        r = os.popen("ps -ef|grep %s" % substr)
        s = cStringIO.StringIO(r.read())
        for line in s:
            cmd = "kill -9 %s" % (line.split()[1])
            print(cmd)
            os.system(cmd)
    except:
        pass


def kill_process(pid, params={}):
    """
        这是个回调函数，如果没有提供的话，则使用这个
        将没有响应的进程停止
    """
    logger.ods("%s %s" % ("强制停止进程", pid), lv='info', cat='kill_process')
    logger.flush_fbdic(closeall=True)
    try:
        if 'win' in sys.platform and not ('darwin' in sys.platform):
            """kill function for Win32"""
            # 可能进程号不存在
            p = psutil.Process(int(pid))
            p.terminate()
        else:
            if isicm(pid, params=params):
                kill_ICM()
            else:
                cmd = "kill -9 %s" % pid
                print(cmd)
                os.system(cmd)
    except:
        pass
    return True
#    #fix bug in macOS.
#    if 'win' in sys.platform and not ('darwin' in sys.platform):
#        """kill function for Win32"""
#        kernel32 = ctypes.windll.kernel32
#        handle = kernel32.OpenProcess(1, 0, pid)
#        #使用termina函数结束进程
#        return (0 != kernel32.TerminateProcess(handle, 0))
#    else:
#        return (0 != os.system("kill %s"%pid))
