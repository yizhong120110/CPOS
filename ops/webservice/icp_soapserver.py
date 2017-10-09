# -*- coding: utf-8 -*-
""" python26版 """
"""
    用于webservice方式接收三方的请求报文，报文为字符串，UTF8格式

    调用方式：
        1、python icp_soapserver.py (IP、port在__main__中的make_server指定)
        2、uwsgi --http=46.17.189.233:7789 --callable=wsgi_application --file=/home/webservice/src/icp_soapserver.py
        3、uwsgi + uwsgi.xml

    client端测试代码(python26版)
        from suds.client import Client
        cli_obj = Client('http://46.17.189.233:7789/?wsdl')
        result = cli_obj.service.get_jycljg(base64.encodebytes('0053RL9999          {"JYJGM": "1001", "CZGY": "1001"}'.encode('utf8')).decode('utf8'))
        print (result)
        
        # 下面是如何处理文件的内容上传
        import base64
        result = cli_obj.service.archive_document(base64.encodestring('anr'),'filena_aaa.txt')
        print (result)

    client端测试代码(python34版，直接上传报文没有区别)
        import base64
        result = cli_obj.service.archive_document(base64.encodebytes('中国'.encode('utf8')).decode('utf8'),'filena_aaa.txt')
        print (result)

    设置超时时间的写法：
        import socket
        from suds.transport.http import HttpTransport
        from suds.client import Client
        tport = HttpTransport()
        # 先设置一个超时时间，避免连接时间过长，超时后client会报错退出
        tport.options.timeout = 30
        cli = Client("http://46.17.189.233:7789/?wsdl",transport=tport)
        # 成功建立连接后，还可以接着调整超时时间
        cli.options.timeout = 1
        try:
            result = cli.service.get_jycljg('test')
            print (result)
        except socket.timeout:
            # server端的测试代码中设置了time.sleep(5)，用于出现超时
            # client超时退出后，server端没有异常出现
            print("socket.timeout")
"""
import soaplib
from soaplib.core.service import rpc, DefinitionBase, soap
from soaplib.core.model.primitive import String, Integer
from soaplib.core.server import wsgi
from soaplib.core.model.clazz import Array
from soaplib.core.model.binary import Attachment
import os
import icm_socket


class ICPWebService(DefinitionBase):
    @soap(String,_returns=String)
    def get_jycljg(self,jsddbw):
        rsdic = icm_socket.main({'IP':'46.17.189.232','PORT':'5620','BUF':jsddbw})
        if rsdic['flag'] == 1:
            results = rsdic['buf']
        else:
            results = str(rsdic['flag'])
        return results

    @soap(Attachment,String, _returns=String)
    def archive_document(self, document ,file_name):
        """
        # 文件内容上传后，会在$HOME目录下生成新的文件
        client.service.archive_document(base64.encodestring('anr'),'filena_aaa.txt'
        """
        userhome = os.environ.get('HOME','')
        fname = '%s/tmp'%(userhome)
        document.file_name = os.path.join(fname, file_name)
        document.save_to_file()
        return fname

soap_application = soaplib.core.Application([ICPWebService], 'SOAPSer')
wsgi_application = wsgi.Application(soap_application)


if __name__=='__main__':
    try:
        from wsgiref.simple_server import make_server
        server = make_server('46.17.189.233', 7789, wsgi_application)
        #server = make_server('127.0.0.1', 7789, wsgi_application)
        server.serve_forever()
    except ImportError:
        print "Error: example server code requires Python >= 2.5"
