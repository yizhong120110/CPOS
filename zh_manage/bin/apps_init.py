# -*- coding: utf-8 -*-
"""
    处理和apps注册相关的事项
    1.各app中static的注册，支持nginx的方式
        使用时实际路径rootpath/static/appsname/js/对应url为/appsname/static/js/  
            todo 不要static直接/appsname/js/ 是否可行？
    2.各app中url的自动扩展为可用
        todo 将每个app作为一个单独的python模块存在，然后可以得到这个模块下的所有函数名，进而转为url
"""
import os, sys
from sjzhtspj import settings
from sjzhtspj import get_err_codingfile
from sjzhtspj import logger
from sjzhtspj import ROOT_DIR, APPS_DIR, STATIC_DIR

# url的通用处理部分
from sjzhtspj.appurls import get_plugins, add_app_urls, ls_files

# 虚拟目录的处理部分
import urls_init
from sjzhtspj.virtualdir import del_static_app_ml, get_apps_static_dir, add_static_app_ml, add_virtual_ml


# 不需要创建static目录的app
NOT_STATIC_APPS = []#['__pycache__',]


def apps_init():
    # 调试模式下，应该先检查文件字符集是否是utf-8
    if settings.CHECK_CHARDET == True:
        errrs = get_err_codingfile(APPS_DIR,
                                   exception=['.pyc', '.jpg', '.png', '.gif', '.otf', '.eot', '.ttf', '.woff'],
                                   encoding=['utf-8', 'ascii'])
        if errrs != []:
            logger.info('=====部分文件字符集不正确=====\n%s\n==============================' % (repr(errrs)))
            raise Exception('部分文件字符集不正确', errrs)

    # 逐次动态映射每个子应用的目录url，首先获取apps下所有的子应用集合
    # 先删除该目录下的文件夹
    del_static_app_ml(STATIC_DIR)

    # 当前有哪些app的static {appname:[js,tpl,images]}
    apps_static_dic = get_apps_static_dir(APPS_DIR, NOT_STATIC_APPS)

    # 在/root/static/目录下先建立app目录
    add_static_app_ml(STATIC_DIR, apps_static_dic.keys())

    # 在各个app目录下创建新的软链接
    add_virtual_ml(STATIC_DIR, apps_static_dic)


    # 加载APPS_DIR下每个app的文件对应url ,同时对url做修饰
    settings.yy_plugins = get_plugins(settings.PLUGINS)
    add_app_urls(APPS_DIR, walk_func=ls_files, yy_plugins=settings.yy_plugins, not_static_apps=NOT_STATIC_APPS)


    # url登记结果展示
    print(settings.urlmap.get_url_all)
    errurls, boolerrrs = settings.urlmap.get_url_err()
    if boolerrrs:
        logger.info('=====部分url映射关系重复=====\n%s\n==============================' % (errurls))
        raise Exception('部分url映射关系重复', errurls)
    return True


if __name__ == "__main__":
    apps_init()
#    print(get_apps_static_dir(r'E:\projects\oa_other\GM_MANAGE_PL\OA_MANAGE_SJ\apps'))
#    del_static_app_ml(r'F:\e')
#    add_static_app_ml( r'F:\e' ,['f','f1','f2'] )
    