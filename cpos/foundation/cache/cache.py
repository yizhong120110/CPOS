# -*- coding: utf-8 -*-
import datetime
from ..substrate.utils.logger import logger


class CachedObject(object):

    """
        # from_source决定了缓存对象的格式，一般应该是CachedObject的子类
        # 子类继承后自行实现from_source
    """

    def __init__(self, keystr, memclient=None):
        # 先检查keystr的格式是否正确
        if not isinstance(keystr, str):
            raise RuntimeError("缓存对象的key值仅能为str类型")
        self.keystr = keystr
        self.memclient = memclient
        self.d = {
            # 版本号 从0开始
            '__obj_version': 0,
            # 内容的类型，用于和版本号结合，进行类似数据校验
            '__obj_type': '',
            # 更新时间
            '__obj_expiration': '0000-00-00 00:00:00.000000',
            # 内容
            '__obj_content': None,
        }
        self.set_content()
        if self.check_content_type() == False:
            raise RuntimeError("错误的数据类型，初始化失败")

    def check_content_type(self):
        """
            # 进行数据结构的检查
        """
        return True

    def set_content(self):
        """
            # 不用管这是什么类型的，直接保存即可
        """
        self.d['__obj_content'] = self.get_object()
        self.__set_expiration_time()

    def get_content(self):
        return self.d['__obj_content']

    def set_version(self, ver):
        """
            # 本对象的版本后自增1
            # 版本号从0开始计数
            # 在更新内容时自动更新，没有必要对外提供
        """
        self.d['__obj_version'] = ver

    def get_version(self):
        """
            # 获得版本信息
        """
        return self.d['__obj_version']

    def __set_expiration_time(self):
        """
            # 暂时是str(datetime.datetime.now())格式 '2015-02-04 00:01:59.128000'
            # 使用直接写明的方式，避免跨平台导致时间格式串错误
            # 在更新内容时自动更新，没有必要对外提供
            # %f：microsecond
        """
        self.d['__obj_expiration'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    def get_expiration_time(self):
        return self.d['__obj_expiration']

    def get_object(self):
        """
            # 先查memcache，没有再通过指定方式获得
        """
        # 先从memcache中取内容
        val_obj = self.from_cache()
        # 正常取到了内容，val_obj就不应该是None了
        if val_obj is None:
            val_obj = self.from_source()
            if val_obj is None:
                raise RuntimeError("未能够获得指定的缓存对象")
            else:
                self.to_cache(val_obj)
        return val_obj

    def to_cache(self, val_obj):
        """
            # val_obj的数据类型由from_cache自行决定
            # 返回值：True/False
        """
        # 更新memcache中的内容
        try:
            if self.memclient:
                self.memclient.set(self.keystr, val_obj)
                return True
            return False
        except:
            logger.oes("缓存对象保存失败", lv='warning', cat='esb.cache')
            return False

    def from_cache(self):
        """
            # 返回值：None 没有获取到对象
            # object：memcache中保存的值
        """
        try:
            if self.memclient:
                #print("[%s] data：from_cache"%(self.keystr))
                return self.memclient.get(self.keystr)
            return None
        except:
            logger.oes("获取缓存对象失败", lv='warning', cat='esb.cache')
            return None

    def from_source(self):
        """
            # memcache中没有，需要通过其他方式获取
        """
        raise RuntimeError("需要在子类中自行实现from_source方法")
