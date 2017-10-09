# -*- coding: utf-8 -*-
"""
    为了代替print
    使用print时，会明显的降低代码的执行效率
"""
import re
import datetime
import os
import sys
import time
import threading
import json
from .binhex import bytes_to_hex
from .. import traceback2
from  ...file.buffer import BufferFile


class SimpleLogger(object):
    def __del__(self):
        print('SimpleLogger destroyed.')
    level_map = {'DEV':0,'INFO':1,'WARNING':3,'ERROR':4, 'FATAL':5}
    def __init__ (self,copy_config_from = None):
        self.runtime_level = self.level_map['DEV'] or 0
        # 要过滤哪些日志输出
        self.filtered_catalogs = []
        if copy_config_from is not None:
            self.filtered_catalogs = copy_config_from.filtered_catalogs
            self.runtime_level = copy_config_from.runtime_level

    def level(self,level = 'DEV'):
        level = level.upper()
        self.runtime_level = self.level_map.get(level) or 0

    def filter (self,filtered_catalogs = None):
        filtered_catalogs = filtered_catalogs or []
        self.filtered_catalogs = []
        for c in filtered_catalogs:
            self.filtered_catalogs.append(c.upper())

    def ods(self, message = '',lv = 'DEV',cat = 'GENERIC'):
        """
            output debug string
            核心运行中产生的日志文件
        """
        lv = lv.upper()
        cat = cat.upper()
        ods_level = self.level_map.get(lv) or 0  # when in dev mode , tolerate all kinds of levels , even not in the level_map.

        #if ods_level >= self.runtime_level and cat.upper() not in self.filtered_catalogs:
        if ods_level >= self.runtime_level:
            for restr_t in self.filtered_catalogs:
                if re.findall(restr_t,cat.upper()):
                    # 在logger过滤列表中的正则都要被过滤掉
                    return
            msg_str = ' | '.join( [datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') ,str(os.getpid()) ,lv.upper(), cat.upper(), message ,'\n'] )
            self.write(msg_str)

    def oes( self , message = '',lv = 'DEV',cat = 'GENERIC' ):
        # 输出format_exc
        exc_msg = traceback2.format_exc( show_locals = True )
        message += '\n%s'%str(exc_msg)
        self.ods( message=message ,lv=lv ,cat=cat )

    def obs( self , message = '',block = bytes([]) , lv = 'DEV',cat = 'GENERIC' ):
        # 将bytes转为16进制数字输出
        exc_msg = traceback2.format_exc( show_locals = True )
        message += '\n%s'%bytes_to_hex(block)
        self.ods( message=message ,lv=lv ,cat=cat )

    def write(self ,msg_str):
        """
            对数据做处理，\n\n循环替换为\n
            在写入数据的最后添加换行符，目的是使用换行符做数据分隔，方便从文件中读取
        """
        while msg_str.find('\n\n')>-1:
            msg_str = msg_str.replace('\n\n','\n')
        print(msg_str+'\n')


class FileLogger(SimpleLogger):
    def __del__(self):
        print('FileLogger destroyed.')
    """
        仅有write是外部使用的函数
    """
    def __init__(self,copy_config_from = None):
        self.root = None
        self.filename = None
        # 多个文件句柄的处理
        self.fb_dic = {}
        # 调试模式，直接打印日志
        self.enable_console = False
        SimpleLogger.__init__(self,copy_config_from)
        self.fb_dic_guard = threading.RLock()

    def set_root(self ,root):
        """
            root 写日志文件的根目录，按进程号区分
        """
        self.root = root
        try:
            # 保证文件目录是存在的
            os.makedirs(os.path.join(self.root ,str(os.getpid())))
#        except:
#            exc_msg = traceback2.format_exc( show_locals = True )
#            print(str(os.getpid()) + exc_msg)
        finally:
            return self.root

    def set_filename(self ,filename):
        """
            filename 可以指定使用一个文件名，如果不指定，则使用每分钟一个文件的方式保存
        """
        self.filename = str(filename)

    def write(self ,msgstr):
        """
            将写入内容做json.dumps处理，每行写一条
        """
        if self.root is None:
            #raise RuntimeError("需要指定文件的根目录")
            print(msgstr)
            return
        self.write_bytes(msgstr)

    def write_bytes(self ,msgstr ,root_has_pid=True):
        """
            获得文件名，如果这个是使用过的，那么直接获取句柄使用，没有的使用过的话，就补充一下
            一分钟一个pid生成一个文件
        """
        fn = self.__get_filename()
        try:
            self.fb_dic_guard.acquire()
            # 出现新的文件名
            if not self.fb_dic.get(fn):
                self.set_root(self.root)
                if root_has_pid:
                    self.fb_dic[fn] = BufferFile( os.path.join(self.root ,str(os.getpid()) \
                        ,"%s.%s.tmp"%(fn,datetime.datetime.now().strftime('%H%M%S%f'))) )
                else:
                    self.fb_dic[fn] = BufferFile( os.path.join(self.root \
                        ,"%s.%s.tmp"%(fn,datetime.datetime.now().strftime('%H%M%S%f'))) )
            # 检查得到的文件句柄是否是本进程的
            if self.close_other_pid_file(fn ,root_has_pid):
                # 再创建一个新的文件句柄
                self.set_root(self.root)
                if root_has_pid:
                    self.fb_dic[fn] = BufferFile( os.path.join(self.root ,str(os.getpid()) \
                        ,"%s.%s.tmp"%(fn,datetime.datetime.now().strftime('%H%M%S%f'))) )
                else:
                    self.fb_dic[fn] = BufferFile( os.path.join(self.root \
                        ,"%s.%s.tmp"%(fn,datetime.datetime.now().strftime('%H%M%S%f'))) )
            self.fb_dic[fn].write(msgstr if isinstance(msgstr ,bytes) else msgstr.encode('utf8'))
            if self.enable_console:
                # 这个可以是True，也可以是一个文件路径用于输出日志到某个目录
                if self.enable_console != True:
                    try:
                        open(self.enable_console,'ab').write(msgstr.encode(encoding="utf-8"))
                    except:
                        pass
                else:
                    # 不输出到文件的时候就输出到控制台
                    print(msgstr)
        except:
            exc_msg = traceback2.format_exc( show_locals = True )
            print(str(os.getpid()) + exc_msg)
        finally:
            self.fb_dic_guard.release()

        # 进行维护的文件句柄的检索操作
        self.flush_fbdic()

    def __get_filename(self):
        """
            这是最终的文件名，优先使用filename，没有就按照分钟来保存
            # YYYYmmddHHMM
        """
        return self.filename or self.__get_mintime()

    def __get_mintime(self):
        return time.strftime("%Y%m%d%H%M", time.localtime())

    def set_debug(self ,enable_console):
        """
            设置是debug模式，会输出write的内容到控制台
        """
        self.enable_console = enable_console

    def close_other_pid_file(self, fn ,root_has_pid=True):
        if root_has_pid:
            try:
                # 不是当前这一分钟的文件名，那么可以移除掉了
                if str(os.getpid()) != self.fb_dic[fn].filename.split(os.path.sep)[-2]:
                    # 不是本进程的pid，先移除掉
                    self.fb_dic[fn].close_noflush()
                    self.fb_dic.pop(fn)
                    # 不是自己pid的
                    return True
            except:
                exc_msg = traceback2.format_exc( show_locals = True )
                print(str(os.getpid()) + exc_msg)
        # 是自己pid的
        return None

    def close(self, filename):
        filename = str(filename)
        try:
            self.fb_dic_guard.acquire()
            if self.fb_dic.get(filename):
                self.fb_dic[filename].close()
                fn_tobj = self.fb_dic.pop(filename)
                # 将文件重命名，将.tmp变为.log
                fn_old = fn_tobj.filename
                fn_new = '.'.join(fn_old.split('.')[:-1]+['log'])
                os.renames(fn_old ,fn_new)
        except:
            exc_msg = traceback2.format_exc( show_locals = True )
            print(str(os.getpid()) + exc_msg)
        finally:
            self.fb_dic_guard.release()

    def flush_fbdic(self ,closeall=False):
        """
            进行维护的文件句柄的检索操作
            closeall 用于kill进程前刷新所有的日志到本地文件中
        """
        try:
            self.fb_dic_guard.acquire()
            fnlist =list(self.fb_dic.keys())
            for fn_t in fnlist:
                if closeall == True:
                    self.close(fn_t)
                    continue
                if fn_t != self.__get_mintime() and fn_t != self.filename:
                    # 不是当前这一分钟的文件名，那么可以移除掉了
                    if not self.close_other_pid_file(fn_t):
                        self.close(fn_t)
        except:
            exc_msg = traceback2.format_exc( show_locals = True )
            print(str(os.getpid()) + exc_msg)
        finally:
            self.fb_dic_guard.release()

def logger_enable_console(logger,if_enable = False):
    if isinstance(logger ,FileLogger):
        logger.set_debug(if_enable)

def logger_set_root(logger,path):
    if isinstance(logger ,FileLogger):
        logger.set_root(path)


logger = FileLogger()



if __name__ == '__main__':
    logger.level('dev')
    logger.filter(['1'])
    logger.ods('123',cat='amqp')
    logger.obs('123',block='中国'.encode('utf8'),cat='amqp')
    try:
        aaaa
    except Exception as err:
        logger.oes("测试exception：")
