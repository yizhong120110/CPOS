# -*- coding: utf-8 -*-
from cpos.foundation._callable.core import Callable
import marshal
import copy
import json
import bitstring as bs
import cpos.esb.basic.rpc.rpc_transaction as rtrans


class FunctionBodyCallable(Callable):
    """
        # GlobalFunction的代码执行
    """
    def __init__(self,dm,mc):
        Callable.__init__(self,marshal.loads(dm),mc)
        
    def run(self,np,local=None):
        Callable.run(self,np ,local)
        return np[self.get_name()]


class YWFunctionCallable(Callable):
    """
        # PublicFunction的代码执行
    """
    def __init__(self,dm,mc):
        Callable.__init__(self,marshal.loads(dm),mc)
        
    def run(self,np,local=None):
        Callable.run(self,np ,local)
        reg_to_yw = 'YW.' +self.get_name()+ ' = ' + self.get_name()
        exec(reg_to_yw,np)
        return True


class FunctionResultCallable(Callable):
    """
        # 直接执行没有参数的函数
    """
    def __init__(self,dm,mc):
        Callable.__init__(self,marshal.loads(dm),mc)

    def run(self,np,local=None):
        Callable.run(self,np ,local)
        py_get_res = '__________res_________ = ' + self.get_name() + '()'
        exec(py_get_res,np)
        return copy.deepcopy(np['__________res_________'])


class FlowNodePYCallable(FunctionResultCallable):
    """
        # 要先声明函数，然后执行函数
    """
    pass


class FlowNodePYCCallable(FunctionResultCallable):
    """
        # 要先声明函数，然后执行函数
        # 对于pyc直接dm=''就行，还是要求使用marshal.dumps
    """
    pass
    # 原来使用时是没有marshal.loads的，但是从py文件中import代码时会有问题，改成marshal.loads后即可
#    def __init__(self, dm, mc):
#        # Callable.__init__ 是特意这样写的，没有写错
#        Callable.__init__(self,dm,mc)


class FlowNodeCCallable(Callable):
    """
        # C节点类的，李志坚提供接口 todo
    """
    def run (self, np,local=None):
        # 临时挡板 todo
        return 0


class FlowNodeJavaCallable(Callable):
    """
        # java 类型的flow节点执行
        为java处理程序提供要执行的java节点代码，以及jyzd，然后将收回的值更新jyzd
    """
    def __init__(self,jdbm,jdmc):
        self.jdbm = jdbm
        self.jdmc = jdmc
        
    def run(self,np,local=None):
        # 不考虑返回值的问题
        # java {'SYS_JAVACODE'：'jdbm1','k1':'v1','k2':'v2'...}
        # return {SYS_RETURN_JAVACODE:返回值,'SYS_JAVACODE'：'jdbm1','k1':'v1','k2':'v2'...}
        
        # 发送给java的json字典
        send_dic = {"SYS_JAVACODE":self.jdbm}
        for kk in np["jyzd"].keys():
            # 二进制的value要转为16进制的字符串
            if kk in ("SYS_YFSDBW" ,"SYS_YFSDBW"):
                send_dic[kk] = str( bs.Bits(bytes=np["jyzd"][kk]).hex ) 
            elif isinstance(np["jyzd"][kk] ,bytes):
                pass
            else:
                send_dic[kk] = str(np["jyzd"][kk])
        
        # 同java的交互必须是二进制的方式，保证编码一致
        json_send = json.dumps(send_dic).encode("utf8")
        rs_json = rtrans.send_trans_java(json_send)
        rs_dic = json.loads(rs_json.decode("utf8"))
        
        for rkk in rs_dic.keys():
            if kk in ("SYS_YFSDBW"):
                bs.Bits(hex=rs_dic[rkk]).bytes
            elif kk in ("SYS_YFSDBW"):
                pass
            else:
                np["jyzd"].update( { rkk : rs_dic[rkk] } )
        return rs_dic["SYS_RETURN_JAVACODE"]
