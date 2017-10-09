# -*- coding: utf-8 -*-
from cpos3.utils.charset import converChardet
from cpos3.utils.charset import check_file_encoding

def converChardetByList():
    filelist = [('ISO-8859-2', r'E:\projects\oa_other\GM_MANAGE_PL\zh_manage\apps\_init\static\codemirror4.6\test\mode_test.js')]
    filelist = []
    for xx ,filepath in filelist:
        if filepath.endswith('.js') or filepath.endswith('.css') or filepath.endswith('.json'):
            converChardet(filepath)
    return True


def test_check_file_encoding():
    print (check_file_encoding(r'E:\projects\oa_other\GM_MANAGE_PL\zh_manage\apps\_init\static\codemirror4.6\test\mode_test.js'))


if __name__=="__main__":
    converChardetByList()
    test_check_file_encoding()
