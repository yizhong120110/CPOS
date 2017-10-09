# -*- coding: utf-8 -*-
from cpos.foundation.cache.cache import CachedObject
from cpos.esb.basic.busimodel.callable import *
from cpos.esb.basic.busimodel.dynamicruntime import ChildNodesFlowRuntime
from cpos.esb.basic.config import settings 
from cpos.esb.basic.busimodel.callable_source import main as api_source_from_db
if settings.API_SOURCE_FROM_DB is not None:
    api_source_from_db = settings.API_SOURCE_FROM_DB
import marshal
import textwrap

def merge_py_code(mc,dm):
    # 转换为标准linux格式
    code = textwrap.dedent(dm.replace('\r', '')) 
    clines = code.split('\n')
    cs = ["def " + mc + ":"]
    cs.extend(['    ' + x for x in clines])
    return mc.split('(')[0].strip(), '\n'.join(cs).strip()

def merge_py_code_str(mc,dm):
    # 这是函数类的特殊处理 
    # 2015-03-06对应处理 dmlx=str {'mc':函数名称, 'dm':函数代码,'dmlx':代码类型}
    # dm会是多行的，不能用单引号处理，必须是换行的引号
    return mc, str(mc) + '= """' + dm + '"""'

def merge_py_code_shell(mc,dm):
    # shell类型，直接写文件，mc中的函数名部分做文件名，参数这里用不到
    code = textwrap.dedent(dm.replace('\r', '')) 
    return mc.split('(')[0].strip(), code


class UPDJYLC(object):
    """
        # 仅作为工具类存在，提供jylc的callable类型转换
    """
    def update_callable_object(self,t_jylc,ssjydm):
        """
            # 对node进行callable类型转换
        """
        rs = {}
        for node_name in t_jylc.keys():
            if node_name == 'start':
                rs[node_name] = FlowNodePYC(t_jylc[node_name],ssjydm, 'def func():return 0' ,'func')
            elif node_name == 'end':
                # 应该不需要end
                pass
            elif t_jylc[node_name]['lx'] == 'py':
                rs[node_name] = FlowNodePY(t_jylc[node_name],ssjydm,node_name)
            elif t_jylc[node_name]['lx'] == 'pyc':
                rs[node_name] = FlowNodePYC(t_jylc[node_name],ssjydm)
            elif t_jylc[node_name]['lx'] == 'flow':
                rs[node_name] = ChildNodesFlow(t_jylc[node_name],t_jylc[node_name]['jdbm'],node_name ,self.memclient)
            elif t_jylc[node_name]['lx'] == 'c':
                rs[node_name] = FlowNodeC(t_jylc[node_name],ssjydm)
            elif t_jylc[node_name]['lx'] == 'java':
                rs[node_name] = FlowNodeJava(t_jylc[node_name],ssjydm)
        return rs

    def get_flow_node(self,node_name):
        """
            # 从jylc中获得要处理的Node
        """
        if self.d['__jylc'].get(node_name):
            return self.d['__jylc'][node_name]
        else:
            raise RuntimeError("没有找到指定的交易节点")


class Transaction(CachedObject,UPDJYLC):
    """
        # 交易JY
    """
    def __init__(self, keystr ,memclient=None):
        CachedObject.__init__(self,keystr ,memclient)
        ywobj = Business(self.get_content()['jyssyw'] ,memclient)
        # 用于绑定到YW上的公共函数
        self.d['__jygghs'] = ywobj.get_runsobj()
        # 交易所属业务的代码
        self.d['__jyssywdm'] = ywobj.get_ywdm()
        # 交易所属业务的名称
        self.d['__jyssywmc'] = ywobj.get_ywmc()
        # 交易所属业务的业务参数
        self.d['__jycs_ywcs'] = ywobj.get_ywcs()
        # 交易解包函数
        self.d['__jyjb_func'] = TransactionNode(self.get_content()['jyjb'] ,memclient)
        # 交易打包函数
        self.d['__jydb_func'] = TransactionNode(self.get_content()['jydb'] ,memclient)
        # 转为callable对象的jylc字典
        self.d['__jylc'] = self.update_callable_object(self.get_content()['jylc'],keystr)
    
    def get_cssj(self):
        # 超时时间
        return self.get_content()['cssj']

    def get_jyzt(self):
        # 交易状态
        return self.get_content()['jyzt']

    def get_jycs(self):
        # 交易参数
        return self.get_content()['jycs']

    def get_jymc(self):
        # 交易名称
        return self.get_content()['jymc']

    def get_jycs_all(self):
        # 交易参数 含业务参数
        ywcs = self.d['__jycs_ywcs']
        ywcs.update(self.get_content()['jycs'])
        return ywcs

    def from_source(self):
        return api_source_from_db('JY',self.keystr)
    
    def get_jydb_callable(self):
        # 交易打包函数
        return self.d['__jydb_func']

    def get_jyjb_callable(self):
        # 交易解包函数
        return self.d['__jyjb_func']

    def get_jygghs(self):
        """
            # 交易的所有公共函数，来自业务
        """
        return self.d['__jygghs']

    def get_jyssywdm(self):
        """
            # 交易的所属业务代码，为了能够给jyzd赋值
        """
        return self.d['__jyssywdm']

    def get_jyssywmc(self):
        """
            # 交易的所属业务名称，为了能够给jyzd赋值
        """
        return self.d['__jyssywmc']


class TransactionNode(CachedObject):
    """
        # 交易节点JYJD
    """
    def __init__(self, keystr ,memclient=None):
        CachedObject.__init__(self,keystr ,memclient)

    def from_source(self):
        tmp_d = api_source_from_db('JYJD',self.keystr)
        mc,dm = merge_py_code(tmp_d['mc'],tmp_d['dm'])
        tmp_d['dm'] = marshal.dumps(dm)
        tmp_d['mc'] = mc
        return tmp_d

    def run(self,np ,local=None):
        """
            # 可执行对象被调用后将返回执行结果
        """
        return FunctionResultCallable(self.get_content()['dm'], self.get_content()['mc']).run(np)


class CommunicationNode(CachedObject):
    """
        # 通讯节点TXJD
    """
    def __init__(self, keystr ,memclient=None):
        CachedObject.__init__(self,keystr, memclient)

    def from_source(self):
        tmp_d = api_source_from_db('TXJD',self.keystr)
        mc,dm = merge_py_code(tmp_d['mc'],tmp_d['dm'])
        tmp_d['dm'] = marshal.dumps(dm)
        tmp_d['mc'] = mc
        return tmp_d

    def run(self,np ,local=None):
        """
            # 函数执行后会返回结果，无返回值为None
        """
        return FunctionResultCallable(self.get_content()['dm'], self.get_content()['mc']).run(np)


class Business(CachedObject):
    """
        # 业务YW
    """
    def __init__(self, keystr ,memclient=None):
        CachedObject.__init__(self,keystr ,memclient)
        # 所有的可执行函数
        self.d['__all_callable'] = self.get_ywdypzqd_callable() + self.get_ywhsqd_callable()

    def from_source(self):
        return api_source_from_db('YW',self.keystr)
    
    def get_ywcs(self):
        # 业务参数
        return self.get_content()['ywcs']
    
    def get_ywhsqd_callable(self):
        """
            # py-py类函数
        """
        rs = []
        for funcid in self.get_content()['ywhsqd']:
            rs.append( PublicFunction(funcid ,self.memclient) )
        return rs

    def get_ywdypzqd_callable(self):
        """
            # py-str类函数
        """
        rs = []
        for funcid in self.get_content()['ywdypzqd']:
            rs.append( PublicFunction(funcid ,self.memclient) )
        return rs

    def get_runsobj(self):
        """
            # 公共函数
        """
        return self.d['__all_callable']

    def get_ywdm(self):
        """
            # 业务代码
        """
        return self.get_content()['ywdm']

    def get_ywmc(self):
        """
            # 业务名称
        """
        return self.get_content()['ywmc']


class PublicFunction(CachedObject):
    """
        # 函数HS
    """
    def __init__(self, keystr ,memclient=None):
        CachedObject.__init__(self,keystr ,memclient)

    def from_source(self):
        tmp_d = api_source_from_db('HS',self.keystr)
        if tmp_d['dmlx'] == 'py':
            mc,dm = merge_py_code(tmp_d['mc'],tmp_d['dm'])
        elif tmp_d['dmlx'] == 'str':
            mc,dm = merge_py_code_str(tmp_d['mc'],tmp_d['dm'])
        else:
            raise RuntimeError("错误的dmlx类型，初始化失败")
        tmp_d['dm'] = marshal.dumps(dm)
        tmp_d['mc'] = mc
        return tmp_d

    def run(self,np ,local=None):
        """
            # 返回函数体，将函数绑定到YW上
        """
        return YWFunctionCallable(self.get_content()['dm'], self.get_content()['mc']).run(np)


class GlobalFunction(PublicFunction):
    """
        # 函数HS
    """
    def run(self,np ,local=None):
        """
            # 返回函数体，需要显式调用函数
        """
        return FunctionBodyCallable(self.get_content()['dm'], self.get_content()['mc']).run(np)


class FlowNode(object):
    """
        # 交易流程里的节点，jylc字典中的内容很多，使用self.d方式赋值
    """
    def __init__(self, data_t, ssjydm):
        self.d = data_t
        if self.check_content_type() == False:
            raise RuntimeError("错误的数据类型，初始化失败")
        self.ssjydm = ssjydm
    
    def check_content_type(self):
        """
            # 进行数据结构的检查
        """
        return True

    @property
    def node_type(self):
        """
            # py\pyc\c\flow
        """
        return self.d['lx']

    @property
    def route_table(self):
        """
            # 通过这个字典知道下一个几点的编码
        """
        return self.d['fhz']

    @property
    def jdbm(self):
        """
            # 节点编码
        """
        return self.d['jdbm']

    @property
    def jdmc(self):
        """
            # 节点名称
        """
        return self.d['jdmc']

    @property
    def cs(self):
        """
            # 参数字典
        """
        return self.d['cs']


class FlowNodePY(FlowNode):
    """
        # 交易流程里的节点--PY
    """
    def __init__(self, data_t ,ssjydm, mckey ,memclient=None):
        FlowNode.__init__(self,data_t ,ssjydm)
        self.d['__ChildNodesFlow_CachedObject'] = FlowNodePY_CachedObject(mckey ,memclient)

    def run(self,np ,local=None):
        """
            # 可执行对象被调用后将返回执行结果
        """
        return self.d['__ChildNodesFlow_CachedObject'].run(np)


class FlowNodePY_CachedObject(CachedObject):
    """
        # 交易流程里的节点--PY
    """
    def __init__(self, keystr ,memclient=None):
        CachedObject.__init__(self,keystr ,memclient)

    def from_source(self):
        tmp_d = api_source_from_db('JYJD',self.keystr)
        mc,dm = merge_py_code(tmp_d['mc'],tmp_d['dm'])
        tmp_d['dm'] = marshal.dumps(dm)
        tmp_d['mc'] = mc
        return tmp_d

    @property
    def code_dm(self):
        return self.get_content()['dm']

    @property
    def code_mc(self):
        return self.get_content()['mc']

    def run(self,np ,local=None):
        """
            # 可执行对象被调用后将返回执行结果
        """
        return FlowNodePYCallable(self.code_dm, self.code_mc).run(np)


class FlowNodePYC(FlowNode):
    """
        # 交易流程里的节点--PYC
    """
    def __init__(self, data_t ,ssjydm, codes='', funcnm=''):
        FlowNode.__init__(self,data_t ,ssjydm)
        self.codes = codes
        self.funcnm = funcnm

    @property
    def code_dm(self):
        return marshal.dumps(self.codes or open(self.cs['modname'],'rb').read())

    @property
    def code_mc(self):
        return self.funcnm or self.cs['funcname']

    def run(self,np ,local=None):
        """
            # 可执行对象被调用后将返回执行结果
        """
        return FlowNodePYCCallable(self.code_dm, self.code_mc).run(np)


class FlowNodeC(FlowNode):
    """
        # 交易流程里的节点--C
    """
    def run(self,np ,local=None):
        """
            # 可执行对象被调用后将返回执行结果
        """
        return FlowNodeCCallable('','').run(np)


class FlowNodeJava(FlowNode):
    """
        # 交易流程里的节点--java
    """
    def run(self,np ,local=None):
        """
            # 可执行对象被调用后将返回执行结果
        """
        return FlowNodeJavaCallable(self.jdbm, self.jdmc).run(np)


class ChildNodesFlow(FlowNode):
    """
        # 子流程ZLC
    """
    def __init__(self, data_t ,ssjydm ,mckey ,memclient=None):
        FlowNode.__init__(self,data_t ,ssjydm)
        self.d['__ChildNodesFlow_CachedObject'] = ChildNodesFlow_CachedObject(mckey,ssjydm,memclient)

    def run(self,np ,local=None):
        """
            # 为了能够将py、flow统一起来
        """
        return self.d['__ChildNodesFlow_CachedObject'].run(np)


class ChildNodesFlow_CachedObject(CachedObject, UPDJYLC):
    """
        # 子流程ZLC的CachedObject
    """
    def __init__(self, keystr ,jdbm='' ,memclient=None):
        CachedObject.__init__(self,keystr,memclient)
        self.d['__jylc'] = self.update_callable_object(self.get_content(),jdbm)

    def from_source(self):
        return api_source_from_db('ZLC',self.keystr)

    def run(self,np ,local=None):
        """
            # 为了能够将py、flow统一起来
        """
        return ChildNodesFlowRuntime(self).run(np)


class Sbin_CachedObject(CachedObject):
    """
        # 动态生成可执行文件的对象
            funcparam = {'cs': 'start' ,'cs2':'star_2'}
            dr = scall('')
            dr.np.update(funcparam)
            dr = scall("shell_test_cs(cs ,cs2)".replace("shell_test_cs" ,"_=") ,runtime = dr)
            print(dr.np['_'])
    """
    def __init__(self, keystr ,memclient=None):
        CachedObject.__init__(self,keystr ,memclient)

    def from_source(self):
        tmp_d = api_source_from_db('HS_SHELL',self.keystr)
        mc,dm = merge_py_code_shell(tmp_d['mc'],tmp_d['dm'])
        tmp_d['dm'] = dm
        tmp_d['filename'] = mc
        return tmp_d

    def run(self,np ,local=None):
        """
            # 返回一个字典，将文件内容、文件名、调用参数准备好
        """
        tmp_d = self.get_content()
        exec(tmp_d['mc'].replace(tmp_d['filename'] ,"_=") ,np)
        exec(tmp_d['mc'].replace(tmp_d['filename'] ,"_=") ,np)
        _params = np['_']
        if _params and isinstance(_params ,str):
            _params = (_params ,)
        tmp_d["params"] = _params
        return copy.deepcopy(tmp_d)


def test_PublicFunction():
    # 公共函数的使用方式
    tt = PublicFunction('gg_hs_func1_32UUID')
    from cpos.esb.basic.substrate.types import StrAttrDict as AttrDict
    np = {'YW':AttrDict({})}
    tt.run(np)
    print (np)

def test_GlobalFunction():
    # 公共函数的使用方式
    from cpos.esb.basic.busimodel.dynamicruntime import CommonRuntime
    cnd = GlobalFunction('gg_hs_func1_32UUID')
    rs = CommonRuntime().call(cnd)
    rs(2)

def test_CommunicationNode():
    # 通讯节点的使用方式
    from cpos.esb.basic.substrate.types import StrAttrDict as AttrDict
    from cpos.esb.basic.busimodel.dynamicruntime import TransactionIdentificationRuntime
    cnd = CommunicationNode('ltdls_tx')
    jyzd = AttrDict({'SYS_CLBZ':'01', 'SYS_JSDDBW':'58001aaaaaa20150226', 'SYS_TXJBID':'ltdls_tx'})
    TransactionIdentificationRuntime(jyzd).call(cnd)
    print (jyzd)


def test_FlowNodePYC():
    data_t = {'fhz': {'0': 'dsyw_pack_beai_510001的节点ID'}, 'jdbm': 'ycljd', 'jdmc': '预处理节点', 'scys': {}, 'srys': {}, 'lx': 'pyc', 'cs': {'modname': 'E:\\projects\\cpos.esb\\cpos\\esb\\basic\\configs\\config_cache.py', 'type': 'py', 'funcname': 'test_pyc'}, 'xh': 1} 
    np = {'jyzd':'a'}
    #++++++++++++++++++++++++++++++
    FlowNodePYC(data_t,'lt001').run(np)
#    #++++++++++++++++++++++++++++++
#    code_dm = marshal.dumps(open(data_t['cs']['modname'],'rb').read())
#    code_mc = data_t['cs']['funcname']
##    FlowNodePYCCallable(code_dm, code_mc).run(np)
    #++++++++++++++++++++++++++++++
#    import copy
#    from cpos.foundation._callable.core import Callable
#    cab = Callable(marshal.loads(code_dm),code_mc)
#    cab.run(np ,None)
#    py_get_res = '__________res_________ = ' + code_mc + '()'
#    exec(py_get_res,np)
#    return copy.deepcopy(np['__________res_________'])
    #++++++++++++++++++++++++++++++
#    import copy
#    exec(marshal.loads(code_dm),np,None)
#    py_get_res = '__________res_________ = ' + code_mc + '()'
#    exec(py_get_res,np)
#    return copy.deepcopy(np['__________res_________'])


def test_mako(memc_key):
    # 调试mako模板初始化失败的问题
    JY = Transaction("mokotest" ,None)
    # 找到Business对应的代码
    #return JY.get_content()['jyssyw']
    
    ywobj = Business("MAKOTEST" ,None)
    # 找到PublicFunction对应的代码
    #return ywobj.get_content()['ywdypzqd']
    
    funcobj = PublicFunction("9967b738b113406c9efd1bd691b1dff1" ,None)
#    print( funcobj.get_content()['mc'] ,funcobj.get_content()['dm'] )
    print( funcobj.get_content()['mc'] ,funcobj.get_content()['dm'] )
#    Callable.__init__(self,marshal.loads(dm),mc)
    import marshal
    dm = b'\xfa=mako_for= """%for row in [1,2,3]:\r\n    \'a\'=${row}\r\n%endfor"""'
    mc = "mako_for"
    print("Callable.__init__(self,marshal.loads(dm),mc)" ,marshal.loads(dm),mc)
    from cpos.foundation._callable.core import Callable
    Callable(marshal.loads(dm),mc).run({},None)


def test_Sbin_CachedObject():
    callobj = Sbin_CachedObject("shell_with_parms的UUID").run({'cs': 'start' ,'cs2':'star_2'})
    print (callobj)
    callobj = Sbin_CachedObject("shell_with_parms的UUID_2").run({'cs': 'start' ,'cs2':'star_2'})
    print (callobj)
    callobj = Sbin_CachedObject("shell_without_parms的UUID").run({})
    print (callobj)


if __name__=="__main__":
    print(test_Sbin_CachedObject())
