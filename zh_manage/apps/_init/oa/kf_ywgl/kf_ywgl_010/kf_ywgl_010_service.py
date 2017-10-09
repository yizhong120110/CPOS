# -*- coding: utf-8 -*-
# Action: 业务详情-文档清单 service
# Author: zhangchl
# AddTime: 2015-01-05
# Standard: 注释仅能以“#”开头，sql可以是“--”；注释不能同代码在同一行

from sjzhtspj import ModSql, response, static_file, TMPDIR, render_string
from sjzhtspj.common import get_strftime2, get_uuid, ins_czrz, get_file_path
import os
import random
import zipfile


def index_service():
    """
    # 文档清单主页面
    """
    data_wdlb = []
    # 数据库操作
    with sjapi.connection() as db:
        # 查询文档类别
        data_wdlb = ModSql.kf_ywgl_010.execute_sql_dict( db, 'index_wdlb' )
    
    return data_wdlb

def data_service( data_dic ):
    """
    # 业务详情-文档清单 列表初始化
    """
    # 反馈信息
    data = {'total':0, 'rows':[]}
    # 数据库操作
    with sjapi.connection() as db:
        # 查询文档清单总条数
        sql_dic = { 'ywid': data_dic['ywid'] }
        total = ModSql.kf_ywgl_010.execute_sql( db, 'data_count', sql_dic )[0].count
        # 本页面显示文档清单信息
        sql_dic.update( { 'rn_start': data_dic['rn_start'], 'rn_end': data_dic['rn_end'] } )
        wdqdxx = ModSql.kf_ywgl_010.execute_sql_dict( db, 'data_rs', sql_dic )
        # 组织反馈信息
        data['total'] = total
        data['rows'] = wdqdxx
    
    return data

def data_add_service( data_dic ):
    """
    # 业务详情-文档清单 新增 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    
    # 数据库操作
    with sjapi.connection() as db:
        # 校验文档是否已经上传
        check_dic = { 'wdmc': data_dic['wdmc'], 'ssywid': data_dic['ssywid'] }
        rs_check = ModSql.kf_ywgl_010.execute_sql( db, 'data_check', check_dic )[0].count
        # 存在直接反馈即可
        if rs_check > 0:
            result['msg'] = "文档名称异常，名称已经存在，请重新选择"
            return result
        
        # 保存数据
        # 将文件保存到指定路径下
        # 首先处理路径
        msg,fpath = get_file_path( db, 'upload', 'FILE_UPLOAD_PATH' )
        if msg != True:
            result['msg'] = msg
            return result
        # 将文件写入到文件夹内
        wdmc_bch = '%s.%s' % ( data_dic['ssywid'], data_dic['wdmc'] )
        fname_path = os.path.join( fpath, wdmc_bch )
        file = open(fname_path, "wb")
        file.write( data_dic['wdnr'] )
        file.close()
        
        # 文档清单新增
        wdqd_dic = { 'wdmc': data_dic['wdmc'], 'ssywid': data_dic['ssywid'],
        'wdlb': data_dic['wdlb'], 'id': get_uuid(), 'wdmc_bch': wdmc_bch }
        ModSql.kf_ywgl_010.execute_sql( db, 'data_add_wdqd', wdqd_dic )
        nr = '文档新增：文件名称[%s]，文件类别[%s]，文件名称-保存后[%s]' % (wdqd_dic['wdmc'], wdqd_dic['wdlb'], wdqd_dic['wdmc_bch'])
        ins_czrz( db, nr, gnmc = '文档清单管理_新增' )
        #提交 定义反馈信息
        result['state'] = True
        result['msg'] = '添加文件成功'
    
    return result

def data_edit_service( data_dic ):
    """
    # 业务详情-文档清单 上传
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    # 数据库操作
    with sjapi.connection() as db:
        # 根据文档ID查询当前文档的基本信息以便登记日志
        upd_befor = ModSql.kf_ywgl_010.execute_sql_dict( db, 'select_wdqd', data_dic)[0]
        # 组织sql
        # 文档清单字典
        sql_wdqd_data = { 'wdlb': data_dic['wdlb'], 'wdqdid': data_dic['wdqdid'], 'wdbz':'' }
        if data_dic['fileobj']:
            # 文档名称
            wdmc = data_dic['fileobj'].raw_filename
            # 文档内容
            wdnr = data_dic['fileobj'].file.read()
            # 校验文档是否已经上传
            check_dic = { 'wdmc': wdmc, 'ssywid': data_dic['ssywid'], 'wdqdid': data_dic['wdqdid'] }
            rs_check = ModSql.kf_ywgl_010.execute_sql( db, 'data_check', check_dic )[0].count
            # 存在直接反馈即可
            if rs_check > 0:
                result['msg'] = "文档名称异常，名称已经存在，请重新选择"
                return result
            else:
                # 不存在，保存到数据库
                # 将文件保存到指定路径下
                # 首先处理路径
                msg,fpath = get_file_path( db, 'upload', 'FILE_UPLOAD_PATH' )
                if msg != True:
                    result['msg'] = msg
                    return result
                
                # 将原来文件进行删除
                wdqd_lst = ModSql.kf_ywgl_010.execute_sql( db, 'data_getwdqd', { 'wdqdidlst': [data_dic['wdqdid']] } )
                if wdqd_lst:
                    # 删除文件
                    y_wdmc_bch = wdqd_lst[0]['wdmc_bch']
                    if y_wdmc_bch:
                        fname_path = os.path.join( fpath, y_wdmc_bch )
                        if os.path.exists( fname_path ):
                            os.remove(fname_path)
                
                # 将文件写入到文件夹内
                wdmc_bch = '%s.%s' % ( data_dic['ssywid'], wdmc )
                fname_path = os.path.join( fpath, wdmc_bch )
                file = open(fname_path, "wb")
                file.write( wdnr )
                file.close()
                
                # 文档清单追加修改文档名称
                sql_wdqd_data.update( { 'wdmc': wdmc, 'wdmc_bch': wdmc_bch, 'wdbz':'已变更' } )
        
        
        # 修改文档清单
        ModSql.kf_ywgl_010.execute_sql( db, 'data_edit_wdqd', sql_wdqd_data )
        # 整理日志信息
        upd_after = '未变更'
        if sql_wdqd_data['wdbz']:
            sql_wdqd_data['id'] = sql_wdqd_data['wdqdid']
            sql_wdqd_data['ssywid'] = upd_befor['ssywid']
            del sql_wdqd_data['wdqdid']
            del sql_wdqd_data['wdbz']
            upd_after = str(sql_wdqd_data)
        nr = '文档上传：上传前：%s，上传后：%s' % ( upd_befor, upd_after )
        ins_czrz( db, nr, gnmc = '文档清单管理_上传' )
        #提交 定义反馈信息
        result['state'] = True
        result['msg'] = '上传成功'
    
    return result
    
def data_del_service( data_dic ):
    """
    # 文档清单 删除 提交
    """
    # 反馈信息
    result = {'state':False, 'msg':''}
    # 数据库操作
    with sjapi.connection() as db:
        # 删除保存目录下的文件
        # 首先处理路径
        msg,fpath = get_file_path( db, 'upload', 'FILE_UPLOAD_PATH' )
        if msg != True:
            result['msg'] = msg
            return result
        # 获取文档信息
        wdqd_lst = ModSql.kf_ywgl_010.execute_sql( db, 'data_getwdqd', { 'wdqdidlst': [data_dic['wdqdid']] } )
        if wdqd_lst:
            # 删除文件
            wdmc_bch = wdqd_lst[0]['wdmc_bch']
            if wdmc_bch:
                fname_path = os.path.join( fpath, wdmc_bch )
                if os.path.exists( fname_path ):
                    os.remove(fname_path)
            # 删除文档清单
            ModSql.kf_ywgl_010.execute_sql( db, 'data_del_wdqd', {'wdqdid': data_dic['wdqdid']} )
            # 登记操作日志
            ins_czrz( db, '文档清单[%s]已被删除' % wdmc_bch if wdmc_bch else wdqd_lst[0]['wdmc'], gnmc = '文档清单管理_删除' )
            
            # 组织反馈值
            result['state'] = True
            result['msg'] = '删除成功!'
        else:
            result['msg'] = '删除失败，文档清单不存在!'
    
    return result
    
def data_down_service( data_dic ):
    """
    # 业务详情-文档清单 下载
    """
    # 文档清单信息
    wdqdxx = []
    with sjapi.connection() as db:
        # 获取对应的文档清单信息
        wdqdxx = ModSql.kf_ywgl_010.execute_sql_dict( db, 'data_getwdqd', {'wdqdidlst': data_dic['wdqdidstr'].split(',')} )
    
    # 未查询到文档信息
    if wdqdxx == []:
        return render_string( "<script>alert('选择文件在系统中已经不存在，无法下载');%s</script>" % data_dic['to_path'] )
    
    # 写文件
    # 写文件路径
    # 首先处理路径
    msg,fpath = get_file_path( db, 'upload', 'FILE_UPLOAD_PATH' )
    if msg != True:
        return render_string( "<script>alert('%s');%s</script>" % ( msg, data_dic['to_path'] ) )
    
    # 总文档大小(默认第一个)
    fname_size = os.path.getsize( os.path.join(  fpath, wdqdxx[0]['wdmc_bch'] ) )
    # 反馈文件名称（真实文件名称），默认第一个
    return_fname = wdqdxx[0]['wdmc_bch']
    # 反馈文件名称（下载文件名称），默认第一个
    dow_fname = wdqdxx[0]['wdmc']
    # 如果是批量下载，需要打成zip包
    if data_dic['downtype'] == '1':
        # 如果是zip是从tmp临时目录中下载
        y_fpath = fpath
        fpath = TMPDIR
        # 创建压缩文件
        return_fname = '%s%s%s' % ( get_strftime2(), str( random.randint(1,10000)), ".zip" )
        dow_fname = return_fname
        zip_path = os.path.join(  fpath, return_fname )
        zipobj = zipfile.ZipFile( zip_path, "a" )
        
        # 将要下载的文档加入到zip文件中
        for wdqdxx in wdqdxx:
            filepath = os.path.join( y_fpath, wdqdxx['wdmc_bch'] )
            #将要下载的文件写入zip文件中:
            zipobj.write( filepath, wdqdxx['wdmc'] )
        zipobj.close()
        # 重新获取下载文件大小
        fname_size = os.path.getsize( zip_path )
    
    # 限定下载文档大小不得大于200M
    fname_size_m = fname_size/1024/1024
    if fname_size_m > 200:
        #return render_string( "<script>alert('选择下载文件总大小[%dM]超过限定大小（200M），所以无法下载');%s</script>" % ( int(fname_size_m), data_dic['to_path'] ) )
        return "<script>window.parent.$.messager.alert('错误', '选择下载文件总大小[%dM]超过限定大小（200M），所以无法下载', 'error');</script>" % ( int(fname_size_m) )
#    # 组织反馈信息
#    # 第一个参数：现在文件真实文件名称
#    # 第二个参数root：下载真实文件所在绝对目录
#    # 第三个参数download：文档下载时显示文件名称
#    return static_file( return_fname, root=fpath, download= dow_fname )
    # 下载文件名称
    filename = return_fname
    # 下载文件路径
    root = fpath
    import time ,datetime
    # 设置cookie名称fileDownload，值为true，路径是根目录/
    response.set_cookie("fileDownload", "true", path="/")
    # return "<script>window.parent.$.messager.alert('提示', '不允许下载', 'info');</script>"
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