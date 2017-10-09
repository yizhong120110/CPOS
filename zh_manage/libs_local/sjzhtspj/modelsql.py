# -*- coding: utf-8 -*-

import os
from cpos3.modelsql.sqlxml import MapperList, readxml, ModelsSQL, SubsqlStr
from . import MODELSQL_DIR
from cpos3.utils.ftools import AttrDict
from cpos3.conf import settings


class LocalAttrDict(AttrDict, SubsqlStr):
    # 允许使用的方法
    def sql_func_nm(self):
        return ['_in','_tb','_or','_or_n','_and','_and_n','_set']

    def _in(self ,lst):
        return self.in_rel(lst, single_quotes=True)

    def _tb(self ,lst):
        return self.in_rel(lst, single_quotes=False)

    def _or(self, fl, lst):
        # id='1' or id='2' or id='3' or id='4'
        return self.subsql_rel([(fl,val) for val in lst], 'or')

    def _or_n(self, fl, lst):
        # id!='1' or id!='2' or id!='3' or id!='4'
        return self.subsql_rel([(fl,val) for val in lst], 'or', '!=')

    def _and(self, lst):
        # zj1='zj1val' and zj2='zj2val' and zj3='zj3val'
        return self.subsql_rel(lst, 'and')

    def _and_n(self, lst):
        # zj1!='zj1val' and zj2!='zj2val' and zj3!='zj3val'
        return self.subsql_rel(lst, 'and', '!=')

    def _set(self, lst):
        # nr='nrval', czr='czrval', czsj='czsjval'
        return self.subsql_rel(lst, ',')


class LocalModelsSQL(ModelsSQL):
    """
        # 将XML中定义的SQL语句和db的执行结合起来，做sql防注入处理
    """
    def __execute_sql_rel(self, db, sqlid, param_dic={}, dicorobj="class"):
        # 真正执行处理的函数，不对外提供
        sql = self.mako2sql(sqlid, LocalAttrDict(param_dic))
        print ('------',sql)
        # 排除掉列表型的数据，这一类只对mako生效，放到execute中会报错
        param_dic = dict([(kk,vv) for kk ,vv in param_dic.items() if not isinstance(vv,(list,tuple,set))])
        return db.execute_sql(sql, param_dic, dicorobj)

    def execute_sql(self, db, sqlid, param_dic={}):
        # 返回值是[class]
        return self.__execute_sql_rel(db, sqlid, param_dic, dicorobj="class")

    def execute_sql_dict(self, db, sqlid, param_dic={}):
        # 返回值是[dict]
        return self.__execute_sql_rel(db, sqlid, param_dic, dicorobj="dict")


#函数 init_models_sql
#    参数：  dirpath 字符串 app的基准目录，其下的文件夹为每个app的appname
#    返回值：无
#    功能描述：
#        将每个app下的MapperList做初始化，并在settings中增加其key、value的属性
def init_models_sql():
    """
    每个app下都应该有一个sqlmapper，这里将sql映射及sqlid情况做初始化
    """
    # sql的映射关系文件固定为 modelsql/mapper.xml
    sqlid_mapper = MapperList.fromXml(readxml('mapper.xml', MODELSQL_DIR))
    # 返回字典
    _dict = dict(zip(sqlid_mapper.modidlst,[None]*len(sqlid_mapper.modidlst)))
    # 校验sqlxml文件是否有重复的“sqlid”
    new_o = AttrDict(_dict, strict=True)
    for modid in sqlid_mapper.modidlst:
        ms = LocalModelsSQL(modid, sqlid_mapper, MODELSQL_DIR, 'mapper.xml')
        exec("new_o.%s = ms" % modid)
    
    # 项目自己扩展sql文件列表
    SQLXML_LST = settings.SQLXML_LST
    # 校验扩展文件中modelsid是否和平台已有重复
    sqlid_all = sqlid_mapper.modidlst
    # 扩展sql集合字典
    kzsql_dic = {}
    for filenm in list(set( SQLXML_LST )):
        fil_sqlid_mapper = MapperList.fromXml(readxml(filenm, MODELSQL_DIR))
        fil_dict = dict(zip(fil_sqlid_mapper.modidlst,[None]*len(fil_sqlid_mapper.modidlst)))
        fil_new_o = AttrDict(fil_dict, strict=True)
        for check_sqlid in fil_sqlid_mapper.modidlst:
            # 校验modelsid 是否重复(与平台对比)
            if check_sqlid in sqlid_mapper.modidlst:
                raise Exception("modelsid校验错误", "【%s.%s与平台modelsid重复】" % (filenm,check_sqlid), "不唯一", repr(list(set([]))))
            # 校验modelsid 是否重复(与扩展文件对比)
            for check_filenm, check_lst in kzsql_dic.items():
                if check_sqlid in check_lst:
                    raise Exception("modelsid校验错误", "【[%s.%s]在文件[%s]中已经存在，不可再定义此modelsid】" % (filenm, check_sqlid, check_filenm ), "不唯一", repr(list(set([]))))
            # 校验sqlxml文件是否有重复的“sqlid”
            fil_ms = LocalModelsSQL(check_sqlid, fil_sqlid_mapper, MODELSQL_DIR, filenm)
            exec("fil_new_o.%s = fil_ms" % check_sqlid)
        
        # 将本文件信息追加到扩展sql字典中
        kzsql_dic[filenm] = fil_sqlid_mapper.modidlst
        # 将本文件信息追加到返回值中
        _dict.update( fil_dict )
    
    return AttrDict(_dict, strict=True)
