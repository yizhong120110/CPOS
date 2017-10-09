# -*- coding: utf-8 -*-
"""
    执行shell，先将shell内容写到本地文件中，然后执行这个文件
"""
import os
userhome = os.environ.get('HOME','')

# shell文件的生成目录
SBINPATH = "%s/sjsbin"%(userhome)
