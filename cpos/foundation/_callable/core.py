# -*- coding: utf-8 -*-
import textwrap
import sys
import os
from ..substrate.utils.logger import logger
from ..substrate.interfaces import Clarified


class Callable(object):
    def __init__(self, py_code, fragment_name=''):
        self.d = {'py_code':py_code,'fragment_name':fragment_name}

    def run(self, np,np_local):
        """
            # 在np中注册py_code
        """
        try:
            #logger.ods (str(self.d['py_code']) , lv = 'dev' , cat = 'foundation.callable')
            exec(self.d['py_code'],np,np_local)
            return True
        except:
            logger.oes("callable error：" , lv = 'error' , cat = 'foundation.callable')
            return False

    def get_name (self):
        return self.d['fragment_name']


class DynamicRuntime(Clarified):
    NAME = "DynamicRuntime"
    # np_init_code and udp_np should be deprecated , keeping it is just for the compatibility with old codes.
    # Runtime and Callable should be used like test cases showed below.
    def __init__ (self,np_init_code='',upd_np={}, np = {}, np_local = None):
        self.np = np
        self.np_local = np_local
        self.np_init_code = np_init_code
        self.prepare_environment()
        self.np.update(upd_np)

    def call(self,callable_object):
        return callable_object.run(self.np,self.np_local)
    
    def prepare_environment(self):
        ca = Callable(textwrap.dedent(self.np_init_code.replace('\r', '')))
        self.call(ca)
        return True
    
    def last_result (self):
        # equel to the "_" variable in the py console.
        if '_' in (self.np.keys()):
            return self.np['_']
        return None
    
    def var (self,var_name):
        # equel to the "_" variable in the py console.
        if var_name in (self.np.keys()):
            return self.np[var_name]
        return None


def statement_dynamic_call (statement = '', runtime = None):
    # args like this : p1=value,p2=value,p3=value , in string.
    dr = runtime or DynamicRuntime()
    if statement != '':
        if not dr.call( Callable( statement ) ):
            return None
    return dr


def direct_dynamic_call (module_name = '',func_name = '',args = '', runtime = None):  
    # args like this : p1=value,p2=value,p3=value , in string.
    dr = runtime or DynamicRuntime()
    if dr.var('_') is None:
        dr = statement_dynamic_call('_ = None',dr)
    if module_name != '':
        statement = 'from %s import %s' % (module_name,'*' if func_name == '' else func_name) 
        dr = statement_dynamic_call(statement,dr)

    if func_name != '' and func_name != '*':
        statement = '_ = %s(%s) or _'%(func_name, args)
        dr = statement_dynamic_call(statement,dr)

        if not dr:
            return None
    return dr


def direct_dynamic_call_pyfile (pyfile='' , root='' ,func_name = '',args = '', runtime = None):  
    # args like this : p1=value,p2=value,p3=value , in string.
    dr = runtime or DynamicRuntime()
    if dr.var('_') is None:
        dr = statement_dynamic_call('_ = None',dr)
    if pyfile != '':
        root = os.path.abspath(root) + os.sep
        pyfile = os.path.abspath(os.path.join(root, pyfile.strip('/\\')))
        statement = open(pyfile,mode='rb').read()
        dr = statement_dynamic_call(statement,dr)

    if func_name != '':
        statement = '_ = %s(%s) or _'%(func_name, args)
        dr = statement_dynamic_call(statement,dr)

        if not dr:
            return None
    return dr


scall = statement_dynamic_call
dcall = direct_dynamic_call
dcallpy = direct_dynamic_call_pyfile


#######################################################################
#TEST
a = 0
def __test_call ():
    global a
    a = 100
    print ('__test_call')
    
    return 0


def _test1 ():
    # 使用globals()会对当前环境造成影响，导致open不能正常使用
    #dr = DynamicRuntime(np=globals())
    dr = DynamicRuntime(np=locals())
    dr = dcall('os',runtime = dr)
    if dr:
        dr = dcall(func_name = 'times',args = '',runtime = dr)
    if dr:
        dr = dcall(func_name = 'print',args = '_',runtime = dr)
    if dr:
        dr = dcall(func_name = 'times',args = '',runtime = dr)
    if dr:
        dr = dcall(func_name = 'print',args = '_',runtime = dr)
    if dr:
        dr = scall('print(\' Hello \')',runtime = dr)
    if dr:
        dr = scall('__test_call()',runtime = dr)
    print(a)

def _test2 ():
    b = 1
    c = 1
    dr = DynamicRuntime( np = locals())
    scall('b = b + 1',dr)
    print(dr)
    print(b)  
    ## note! we have to obtain the resualt manually. The 'b = b + 1' call will not touch the 'b' in this scope.
    # why?  ????
    #refer to python doc [exec]:
    #Note
    #The default locals act as described for function locals() below: 
    #    modifications to the default locals dictionary should not be attempted. Pass an explicit locals dictionary 
    #    if you need to see effects of the code on locals after function exec() returns.


    #
    print (dr.var('b'))

    
def _test3 ():
    dr = scall('t3 = "this is t3" ')
    print(dr.var('t3'))
    dr = scall('t4 = t3 + " and t4" ',dr)
    print(dr.var('t4'))
    
def _test4 ():
    # 如果下面这句执行报错，则说明本地环境被破坏，是np=globals()造成的
    #print("++++++++++==========",help(open))
    dr = dcallpy(os.path.abspath( __file__ ),'_test4_print')
    dr = dcallpy(func_name='_test4_print_2' ,args='1111' ,runtime=dr)
    dr = dcallpy(func_name='_test4_print_3' ,args='1111,2222' ,runtime=dr)

def _test4_print():
    print("===== my name is _test4_print")
def _test4_print_2(aaaa):
    print("===== my name is _test4_print_2 %s"%(aaaa))
def _test4_print_3(aaaa,bbbbb):
    print("===== my name is _test4_print_3 %s %s"%(aaaa,bbbbb))


def _test5 ():
    dr = scall('')
    dr.np['aaaaa'] = 'test is aaaaa'
    dr = dcall(func_name = 'print',args = 'aaaaa',runtime = dr)

if __name__ == '__main__':
    _test1()
    print('==========================================================')
    _test2()
    print('==========================================================')
    _test3()
    print('==========================================================')
    _test4()
    print('==========================================================')
    _test5()
