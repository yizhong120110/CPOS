# -*- coding: utf-8 -*-

import os, sys
from subprocess import Popen, PIPE
from . import ROOT_DIR ,logger


def del_static_app_ml(dirpath):
    """
    删除该目录内的文件夹
    先对目录下第一层文件夹中的软链接做删除，然后删除目录下第一层的文件夹（此时文件夹为空）
    """
    for absdir in os.listdir(dirpath):
        # 这一层是appname对应的实际目录
        appnamedir = os.path.join(dirpath, absdir)
        if os.path.isdir(appnamedir) == True:
            logger.debug('app_ml==== %s'%appnamedir)
            # app下的static软链接目录
            del_virtual_ml([os.path.join(appnamedir, x) for x in os.listdir(appnamedir) if
                            os.path.isdir(os.path.join(appnamedir, x)) == True])
            # 软链接删除完成后，再删除appname目录
            os.rmdir(appnamedir)
    return True


def get_apps_static_dir(dirpath, exceptiondirs=[]):
    """
    获得app的static中目录名，对这些目录做软链接 {appname:[js,tpl,images]}
    仅对每个app下static中存在的目录做连接，不存在的不做链接
    """
    appspathinfo = {}
    for appname in os.listdir(dirpath):
        # 需要先是目录，然后排除部分情况
        if os.path.isdir(os.path.join(dirpath, appname)) == True and appname not in exceptiondirs:
            rs_tmp = {appname: []}
            # 这一层是appname对应的实际目录
            appstaticdir = os.path.join(dirpath, appname, 'static')
            if os.path.isdir(appstaticdir) == True:
                for ttdir in os.listdir(appstaticdir):
                    ttabspath = os.path.join(appstaticdir, ttdir)
                    if os.path.isdir(ttabspath) == True:
                        rs_tmp[appname].append(ttabspath)
                        logger.debug('static_dir==== %s'%ttabspath)
            if rs_tmp[appname] != []:
                appspathinfo.update(rs_tmp)
    return appspathinfo


def add_static_app_ml(basepath, pathlist):
    """
    在static目录下创建appname对应的目录
    """
    for ttpath in pathlist:
        os.mkdir(os.path.join(basepath, ttpath))
    return True


def get_win_lnexe():
    """
    在windows环境上检查junction.exe是否存在，不存在提示，存在返回目录
    """
    if os.path.exists(os.path.join(ROOT_DIR, 'junction.exe')) == True:
        return os.path.join(ROOT_DIR, 'junction.exe')
    else:
        raise Exception("程序根目录下junction.exe文件缺失")


def del_virtual_ml(pathlist):
    """
    删除发现的软链接
    """
    for virtual_ml in pathlist:
        if sys.platform[:3] == 'win':#windows平台
#            os.system('%s -d %s' % (get_win_lnexe(), virtual_ml))
            args = [get_win_lnexe(),"-d" ,virtual_ml]
        else:
            args = ["rm","-rf" ,virtual_ml]
#            os.system(' rm -rf  %s' % virtual_ml)   #非windows平台，我们目前是linux，使用ln
        with Popen(args, stdout=PIPE) as proc:
            proc.stdout.read()
    return True


def add_virtual_ml(virbase, pathinfodic):
    """
    对于提供的文件列表，添加软链接
    @virbase 建立软链接的基础目录/root/static
    @pathinfo {appname:[js,tpl,images]}
    """
    for appname in pathinfodic.keys():
        for real_ml in pathinfodic[appname]:
            virtual_ml = os.path.join(virbase, appname, os.path.basename(real_ml))
            if sys.platform[:3] == 'win':#windows平台，使用junction
                #junction.exe -s  D:\projects\GM_MANAGE_PL\static\menu  D:\projects\GM_MANAGE_PL\apps\menu\static
#                os.system('%s -s -q %s %s' % (get_win_lnexe(), virtual_ml, real_ml))
                args = [get_win_lnexe(), "-s", "-q", virtual_ml, real_ml]
            else:
                #注意：linux和windows的目录顺序正好相反！！！！！
#                os.system('ln -s %s %s' % (real_ml, virtual_ml))  #非windows平台，我们目前是linux，使用ln
                args = ["ln", "-s", real_ml, virtual_ml]
            with Popen(args, stdout=PIPE) as proc:
                proc.stdout.read()
    return True

