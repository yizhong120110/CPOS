# -*- coding: utf-8 -*-
# Action: 开发系统-代码下载 service
# Author: zhangchl
# AddTime: 2015-11-19
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql, response, TMPDIR, render_string
from sjzhtspj.common import get_strftime2, get_uuid, ins_czrz, get_file_path
import os, random, zipfile, pickle


def dm_down_service_yw( data_dic ):
    """
    # 开发系统-代码下载 下载( 业务 )
    """
    # 业务信息
    ywdy_rs = None
    # 数据库操作
    with sjapi.connection() as db:
        # 获取业务名称
        ywdy_rs = ModSql.common.execute_sql( db, 'get_ywdy', { 'ywid': data_dic['ywid'] } )
        if not ywdy_rs:
            return "<script>window.parent.$.messager.alert('错误', '未查询到对应的业务信息', 'error');%s</script>" % data_dic['to_path']
    # 业务名称
    ywmc = ywdy_rs[0]['ywmc']
    # 业务编码
    ywbm = ywdy_rs[0]['ywbm']
    # 当前时间
    now_data = get_strftime2()
    # 业务命名的文件夹
    floder_name = '%s_%s' % ( ywbm, now_data )
    # 业务路径
    yw_fpath = os.path.join( TMPDIR, floder_name )
    # 判断目录是否存在，存在更改目录名称
    if os.path.exists(yw_fpath) :
        random_num = str( random.randint(1,10000))
        floder_name = '%s_%s' % ( floder_name, random_num )
        yw_fpath = '%s_%s' % ( yw_fpath, random_num )
    # 创建目录
    os.makedirs( yw_fpath )
    # 向业务目录下添加导出内容
    if data_dic['downtype'] == 'yw':
        dm_down_yw( yw_fpath, data_dic['ywid'] )
    elif data_dic['downtype'] == 'jy':
        dm_down_jy( yw_fpath, data_dic['idstr'].split(',') )
    elif data_dic['downtype'] == 'gghs':
        dm_down_gghs( yw_fpath, data_dic['idstr'].split(',') )
    elif data_dic['downtype'] == 'dypz':
        dm_down_dypz( yw_fpath, data_dic['idstr'].split(',') )
    
    # 对此业务文件夹进行压缩
    #  压缩文件名
    dow_fname = filename = '%s%s_dmdc_%s.zip' % ( get_strftime2(), str( random.randint(1,10000)), ywmc )
    
    return zip_down_file( yw_fpath, filename, TMPDIR, dow_fname, floder_name )

def dm_down_service_tx( data_dic ):
    """
    # 开发系统-代码下载 下载( 通讯 )
    """
    # 通讯信息
    txdy_rs = None
    # 数据库操作
    with sjapi.connection() as db:
        # 获取业务名称
        txdy_rs = ModSql.common.execute_sql( db, 'get_txgl', { 'id': data_dic['txid'] } )
        if not txdy_rs:
            return "<script>window.parent.$.messager.alert('错误', '未查询到对应的通讯信息', 'error');%s</script>" % data_dic['to_path']
    # 通讯名称
    txmc = txdy_rs[0]['mc']
    # 通讯编码
    txbm = txdy_rs[0]['bm']
    # 当前时间
    now_data = get_strftime2()
    # 通讯命名的文件夹
    floder_name = '%s_%s' % ( txbm, now_data )
    # 通讯路径
    tx_fpath = os.path.join( TMPDIR, floder_name )
    # 判断目录是否存在，存在更改目录名称
    if os.path.exists(tx_fpath) :
        random_num = str( random.randint(1,10000))
        floder_name = '%s_%s' % ( floder_name, random_num )
        tx_fpath = '%s_%s' % ( tx_fpath, random_num )
    # 创建目录
    os.makedirs( tx_fpath )
    # 向业务目录下添加导出内容
    if data_dic['downtype'] == 'tx':
        dm_down_tx( tx_fpath, txdy_rs[0] )
    elif data_dic['downtype'] == 'cdtx':
        dm_down_cdtx( tx_fpath, data_dic['idstr'].split(',') )
    
    # 对此通讯文件夹进行压缩
    #  压缩文件名
    dow_fname = filename = '%s%s_dmdc_%s.zip' % ( get_strftime2(), str( random.randint(1,10000)), txmc )
    
    return zip_down_file( tx_fpath, filename, TMPDIR, dow_fname, floder_name )

def zip_down_file( file_path, filename, down_fname, dow_fname, floder_name ):
    """
    # 压缩和下载文件:
        file_path: 待压缩文件所在目录
        filename: 压缩、下载文件真实名称
        dow_path：下载文件绝对路径
        down_fname: 下载后的文件名称
        floder_name：打包结果集开始目录
    """
    #  压缩文件目录
    zip_path = os.path.join(  down_fname, filename )
    #  压缩文件
    add_zip_floder_r( file_path, zip_path, 'a', floder_name )
    
    # 下载文件路径
    root = down_fname
    import time ,datetime
    # 设置cookie名称fileDownload，值为true，路径是根目录/
    response.set_cookie("fileDownload", "true", path="/")
    response.set_header('Content-Type','image/jpeg')
    root = os.path.abspath(root) + os.sep
    filename = os.path.abspath(os.path.join(root, filename.strip('/\\')))
    stats = os.stat(filename)
    response.set_header('Content-Length' ,stats.st_size)
    lm = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(stats.st_mtime))
    response.set_header('Last-Modified', lm)
    response.set_header('Date', time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime()))
    response.set_header("Accept-Ranges", "bytes")
    download = os.path.basename(filename)
    import urllib
    response.set_header('Content-Disposition', 'attachment; filename="%s"' % urllib.parse.quote(dow_fname))
    
    return open(filename, 'rb')

def add_zip_floder_r( foldername, filename, type, floder_name ):
    """
    # 将目录进行压缩
    # foldername：目录列表
    # filename：压缩文件目录
    # type: 压缩文件打开方式 'a': 新打开， 'w':追加
    # path_split：写文件从什么目录开始
    """
    zip = zipfile.ZipFile( filename, type )
    for root,dirs,files in os.walk(foldername):
        # root 目录全路径
        # dirs 下目录
        # files 目录下文件列表
        for filename in files:
            # 实际文件目录
            filepath = os.path.join( root, filename )
            # 保存文件目录
            arcname = os.path.join( root[root.index(floder_name):], filename )
            zip.write( filepath, arcname )
    zip.close()

def dm_down_yw( yw_fpath, ywid ):
    """
    # 下载业务下的交易、公共函数、打印配置代码
    """
    # 查询业务下的交易列表
    # 查询业务下的函数列表
    # 查询业务下的打印配置列表
    # 写在信息结果集
    ywxx_dic = {}
    with sjapi.connection() as db:
        ywxxid_rs = ModSql.common.execute_sql( db, 'get_id_byywid', { 'ywid': ywid} )
        for obj in ywxxid_rs:
            if obj['downtype'] not in ywxx_dic:
                ywxx_dic[obj['downtype']] = []
            ywxx_dic[obj['downtype']].append( obj['id'] )
    # 根据不同类型调用不同类型函数写代码
    for downtype, id_lst in ywxx_dic.items():
        if downtype == 'jy':
            dm_down_jy( yw_fpath, id_lst )
        elif downtype == 'gghs':
            dm_down_gghs( yw_fpath, id_lst )
        elif downtype == 'dypz':
            dm_down_dypz( yw_fpath, id_lst )

def dm_down_jy( yw_fpath, id_lst ):
    """
    # 下载交易列表对应代码
    """
    # 数据库操作
    with sjapi.connection() as db:
        # 处理下载信息，每十个为一组进行下载
        # 间隔数
        space_num = 1
        # 分组数
        arr_num = int(len(id_lst)/space_num) + 1 if len(id_lst)%space_num > 0 else int(len(id_lst)/space_num)
        for i in range(arr_num):
            # 本组查询的id列表
            arr_id_lst = (id_lst[i*space_num:(i+1)*space_num])
            jy_dm = ModSql.common.execute_sql_dict( db, 'dm_down_jy', { 'id_lst': arr_id_lst } )
            for obj in jy_dm:
                # 交易码
                jym = obj['jym']
                # 节点编码
                jdbm = obj['jdbm']
                # 交易目录路径( 定义目录 + 交易码 )
                jy_fpath = os.path.join( yw_fpath, 'jy', jym )
                if os.path.exists(jy_fpath) == False:
                    os.makedirs( jy_fpath )
                jy_fname = '%s.%s.py' % ( jdbm, str( random.randint(1,100)) )
                jd_fpath = os.path.join( jy_fpath, jy_fname )
                # 创建文件对象，写文件
                fileobj = open(jd_fpath, 'w', encoding = 'utf8')
                nr = pickle.loads(obj['nr'].read()) if obj['nr'] and obj['nr'].read() else ''
                fileobj.write( nr )
                fileobj.close()

def dm_down_gghs( yw_fpath, id_lst ):
    """
    # 下载公共函数列表对应代码
    """
    # 数据库操作
    with sjapi.connection() as db:
        # 处理下载信息，每十个为一组进行下载
        # 间隔数
        space_num = 1
        # 分组数
        arr_num = int(len(id_lst)/space_num) + 1 if len(id_lst)%space_num > 0 else int(len(id_lst)/space_num)
        for i in range(arr_num):
            # 本组查询的id列表
            arr_id_lst = (id_lst[i*space_num:(i+1)*space_num])
            gghs_dm = ModSql.common.execute_sql_dict( db, 'dm_down_gghs', { 'id_lst': arr_id_lst } )
            for obj in gghs_dm:
                # 函数名称
                hsmc = obj['hsmc']
                # 函数目录路径
                gghs_fpath = os.path.join( yw_fpath, 'gghs' )
                if os.path.exists(gghs_fpath) == False:
                    os.makedirs( gghs_fpath )
                gghs_fname = '%s.%s.txt' % ( hsmc.split('(')[0], str( random.randint(1,100)) )
                hs_fpath = os.path.join( gghs_fpath, gghs_fname )
                # 创建文件对象，写文件
                fileobj = open(hs_fpath, 'w', encoding = 'utf8')
                nr = pickle.loads(obj['nr'].read()) if obj['nr'] and obj['nr'].read() else ''
                fileobj.write( nr.replace('\n','') )
                fileobj.close()

def dm_down_dypz( yw_fpath, id_lst ):
    """
    # 下载打印配置列表对应代码
    """
    # 数据库操作
    with sjapi.connection() as db:
        # 处理下载信息，每十个为一组进行下载
        # 间隔数
        space_num = 1
        # 分组数
        arr_num = int(len(id_lst)/space_num) + 1 if len(id_lst)%space_num > 0 else int(len(id_lst)/space_num)
        for i in range(arr_num):
            # 本组查询的id列表
            arr_id_lst = (id_lst[i*space_num:(i+1)*space_num])
            dypz_dm = ModSql.common.execute_sql_dict( db, 'dm_down_dypz', { 'id_lst': arr_id_lst } )
            for obj in dypz_dm:
                # 模板名称
                mbmc = obj['mbmc']
                # 模板类型
                mblx = obj['mblx']
                # 函数目录路径
                dypz_fpath = os.path.join( yw_fpath, 'dypz' )
                if os.path.exists(dypz_fpath) == False:
                    os.makedirs( dypz_fpath )
                dypz_fname = '%s.%s.%s' % ( mbmc, str( random.randint(1,100)), mblx )
                hs_fpath = os.path.join( dypz_fpath, dypz_fname )
                # 创建文件对象，写文件
                fileobj = open(hs_fpath, 'w', encoding = 'utf8')
                nr = pickle.loads(obj['nr'].read()) if obj['nr'] and obj['nr'].read() else ''
                fileobj.write( nr.replace('\n','') )
                fileobj.close()

def dm_down_tx( tx_fpath, txxx ):
    """
    # 下载通讯下的代码
    """
    # 判断通讯服务方向
    # 1：客户端
    # 2：服务端
    # 当为客户端时
    if txxx['fwfx'] == '1':
        id_lst = []
        with sjapi.connection() as db:
            cdtxid_rs = ModSql.common.execute_sql( db, 'get_id_bytxid', { 'txid': txxx['id']} )
            id_lst = [ obj['id'] for obj in cdtxid_rs ]
        # 调用C端通讯写文件函数
        dm_down_cdtx( tx_fpath, id_lst )
    else:
        # 服务端，直接写服务端交易码解出代码
        tx_fname = '%s.jcjymhs.%s.py' % ( txxx['bm'], str( random.randint(1,100)) )
        hs_fpath = os.path.join( tx_fpath, tx_fname )
        # 创建文件对象，写文件
        fileobj = open(hs_fpath, 'w', encoding = 'utf8')
        nr = pickle.loads(txxx['nr'].read()) if txxx['nr'] and txxx['nr'].read() else ''
        fileobj.write( nr )
        fileobj.close()

def dm_down_cdtx( tx_fpath, id_lst ):
    """
    # 下载C端通讯列表对应代码
    """
    # 数据库操作
    with sjapi.connection() as db:
        # 处理下载信息，每十个为一组进行下载
        # 间隔数
        space_num = 1
        # 分组数
        arr_num = int(len(id_lst)/space_num) + 1 if len(id_lst)%space_num > 0 else int(len(id_lst)/space_num)
        for i in range(arr_num):
            # 本组查询的id列表
            arr_id_lst = (id_lst[i*space_num:(i+1)*space_num])
            jy_dm = ModSql.common.execute_sql_dict( db, 'dm_down_cdtx', { 'id_lst': arr_id_lst } )
            for obj in jy_dm:
                # 编码
                bm = obj['bm']
                # 节点编码
                jdbm = obj['jdbm']
                # C端通讯目录路径( 定义目录 + bm )
                cdtx_fpath = os.path.join( tx_fpath, bm )
                if os.path.exists(cdtx_fpath) == False:
                    os.makedirs( cdtx_fpath )
                cdtx_fname = '%s.%s.py' % ( jdbm, str( random.randint(1,100)) )
                jd_fpath = os.path.join( cdtx_fpath, cdtx_fname )
                # 创建文件对象，写文件
                fileobj = open(jd_fpath, 'w', encoding = 'utf8')
                nr = pickle.loads(obj['nr'].read()) if obj['nr'] and obj['nr'].read() else ''
                fileobj.write( nr )
                fileobj.close()