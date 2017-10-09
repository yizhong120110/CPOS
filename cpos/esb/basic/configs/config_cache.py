# -*- coding: utf-8 -*-

# memcache的地址
MEMCACHE_IPS = ['46.17.167.237:5628'] 
MEMCACHE_DEBUG = 0
MEMCACHE_TIMEOUT = 0.1

# 这个参数主要是为了方便阿里云上的代码和普通的代码进行区分
# 部署在 阿里云上时使用"aliyun"，虚拟机本地时没有要求 ,type不同，某些方法的调用不一样
MEMCACHE_TYPE = "cpos"
MEMCACHE_PARAMS = (MEMCACHE_IPS, MEMCACHE_DEBUG, MEMCACHE_TIMEOUT)
# 当是阿里云时，params应该这样设置 MEMCACHE_PARAMS = (('ip:port'), 'user', 'passwd')
#MEMCACHE_PARAMS = (('0c8d33a47aa84543.m.cnbjalicm12pub001.ocs.aliyuncs.com:11211'), '0c8d33a47aa84543', 'cposMemcache123456')
