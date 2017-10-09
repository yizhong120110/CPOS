# -*- coding: utf-8 -*-
import ftplib, os
from ops.core.settings import RPC_FILE_ROOT
def ftp_put( host , port , user , passwd , filen , noerror = False , pasv = 1 , debug = 0 , localpath = RPC_FILE_ROOT ):
    """
        把文件上传到服务器上
        参数列表：
            host:主机ip
            port:端口号
            user:用户名
            passwd:密码
            filen:文件名
            noerror:???
    """
    ftp = ftplib.FTP()
    try:
        ftp.set_pasv( pasv )                                #设置ftp put为被动模式
        ftp.set_debuglevel( debug )                         #打开调试级别2，显示详细信息

        ftp.connect( host , port )                    #连接
        ftp.login( user ,passwd )                     #登录
        #print ftp.getwelcome()                        #打印欢迎信息
        filen = filen.rsplit('/',1)                   #分析出文件路径和文件名
        filepath = filen[0]
        #print filepath
        filename = 'STOR ' + filen[1]                 #操作命令，"stor"为上传命令
        ftp.cwd(filepath)                             #改变文件目录到要上传目录下
        bufsize = 1024                                #设置缓冲块大小
#        localpath = settings.FILESDIR
        localfile = os.path.join( localpath , filen[1] )
        #localfile= r"c:\test.txt"                     #本地文件完整路径计文件名
        try:
            file_handler = open(localfile,"rb")           #以读模式在本地打开文件
            try:
                ftp.storbinary(filename,file_handler,bufsize) #上传文件
                return True
            finally:
                file_handler.close()
        except:
            if noerror:
                return False
            else:
                raise
    finally:
        ftp.quit()                                    #退出ftp服务器


def ftp_get( host , port , user , passwd , filen , pasv = 1 , debug = 0 , localpath = RPC_FILE_ROOT):
    """
        从服务器上取文件
        参数列表：
            host:主机ip
            port:端口号
            user:用户名
            passwd:密码
            filen:文件名
    """
    ftp = ftplib.FTP()
    bufsize = 1024
    try:
        ftp.set_pasv( pasv )                                #设置ftp put为被动模式
        ftp.set_debuglevel( debug )                         #打开调试级别2，显示详细信息

        ftp.connect( host , port )
        ftp.login( user ,passwd )
        filen = filen.rsplit('/',1)
        filepath = filen[0]
        filename = filen[1]

        ftp.cwd(filepath)
        # 列表
        import io
        s = io.StringIO()
        ftp.dir( filename , s.write )
        s.seek(0)
        ret = []
        for line in s:
            filename = line.split()[-1]
            ln = os.path.join( localpath , filename )
            file_handler = open( ln ,"wb").write
            ftp.retrbinary('RETR ' + filename , file_handler , bufsize ) #接收服务器上文件并写
            ret.append( ln )
    finally:
        ftp.quit()                                    #退出ftp服务器
        
    return ret

if __name__ == "__main__":
    ss = ftp_get( '121.160.10.9' ,21 , 'bbkz' , 'bbkz' , '/home/bbkz/gtpfile/ytsb/recv/I07090600QSRZ201120155004.RET', localpath = '/jntsyw/rpc_file/GTP_RECV_DIR' )
    print('------------[%s]'%ss)