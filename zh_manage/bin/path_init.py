# -*- coding: utf-8 -*-
"""
    处理和PYTHONPATH自动补充相关的内容
    1.将当前考核项目代码的根目录（bin文件夹所在目录）加入到PYTHONPATH中
    2.将libs加入到PYTHONPATH中，为了能够直接使用其下的三方库源码
    3.将libs\*.zip加入到PYTHONPATH中，为了能够使用cpos.zip
"""
import os, sys, glob


def get_ROOT_DIR():
    """
    项目的根目录
    """
    return os.path.abspath(os.path.join(os.path.split(__file__)[0], '..'))


ROOT_DIR = get_ROOT_DIR()
APPS_DIR = os.path.join(ROOT_DIR, 'apps')
LIBS_DIR = os.path.join(ROOT_DIR, 'libs')
ETC_DIR = os.path.join(ROOT_DIR, 'etc')
STATIC_DIR = os.path.join(ROOT_DIR, 'static')
MODELSQL_DIR = os.path.join(ROOT_DIR, 'modelsql')


def path_init(ROOT_DIR):
    """
    PYTHONPATH加载
    """
    ## 输出PYTHONPATH
    #show_syspath()

    sys.path.append(ROOT_DIR)

    # 一些三方库
    LIBS_DIR = os.path.join(ROOT_DIR, 'libs')
    sys.path.append(LIBS_DIR)
    # zip包类的文件
    sys.path.extend(glob.glob(os.path.join(LIBS_DIR, '*.zip')))


    # 三层结构中的中间层代码
    LIBS_LOCAL_DIR = os.path.join(ROOT_DIR, 'libs_local')
    sys.path.append(LIBS_LOCAL_DIR)

    # 加载apps目录以及apps子应用下的目录到环境变量中
    APPS_DIR = os.path.join(ROOT_DIR, 'apps')
    sys.path.append(APPS_DIR)

    # plugins目录 bottle中url的修饰符
    PLUG_DIR = os.path.join(ROOT_DIR, 'plugins')
    sys.path.append(PLUG_DIR)

    ## 输出PYTHONPATH
    #show_syspath()

    return True


def show_syspath():
    """
    展示PYTHONPATH信息
    """
    print(" " * 4 + "[PYTHONPATH]的内容，开始===========")
    for t_path in sys.path:
        print(" " * 8 + t_path)
    print(" " * 4 + "[PYTHONPATH]的内容，结束===========")
    return True


path_init(ROOT_DIR)
