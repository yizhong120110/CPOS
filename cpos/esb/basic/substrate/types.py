# -*- coding: utf-8 -*-
from cpos.foundation.substrate.types.attrdict import AttrDict as AttrDictDefault

class StrAttrDict(AttrDictDefault):
    def __setattr__(self, key, value):
        if key == '_dict':
            self.__dict__['_dict'] = value
            return
        if key == '_stack':
            self.__dict__['_stack'] = value
            return
        if key == 'Keyword':
            self.__dict__['Keyword'] = value
            return
        if key == 'strict':
            self.__dict__['strict'] = value
            return
        if isinstance(value ,str) or isinstance(value ,bytes):
            pass
        else:
            value = str(value)

        # 如果jyzd的key中出现"."，会导致写入mongodb中时报错
        if isinstance(key ,str):
            key = key.replace('.','')

        try:
            if self.Keyword:
                attr = getattr(self.Keyword, key)
                self._dict[key] = attr.validate(key, value)
            else:
                self._dict[key] = value
        except AttributeError:
            self._dict[key] = value
