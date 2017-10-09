# -*- coding: utf-8 -*-
import ftplib, os, traceback, glob


class FTP:
    def __init__( self, ip, port, user, pwd, path='',pasv = 1):
        """ 
            开启FTP并进入指定目录 
        """
        self.ftp = ftplib.FTP()
        #设置ftp put为被动模式
        self.ftp.set_pasv( pasv )
        self.ftp.connect( ip, port )
        self.ftp.login( user, pwd )
        if path != '':
            self.path = path
            # 切换目录时不再捕捉异常，若目录不存在则直接抛出异常
#            try:
#                self.ftp.cwd( path )
#            except:
#                pass
            self.ftp.cwd( path )


    def close( self ):
        """ 
            关闭FTP 
        """
        self.ftp.quit()

    def mkdir(self,dirname):
        """ 
            创建远程目录 
        """
        if self.check_dir(dirname):
            pass
        else:
            self.ftp.mkd(dirname)

    def check_dir(self,dirname):
        """
            检查远程目录是否存在，True：存在   False：不存在
        """
        try:
            self.ftp.cwd(dirname)
            return True
        except ftplib.error_perm:
            return False
    
    def _allFiles( self, search_path, pattern, pathsep=os.pathsep ):
        """ 查找指定目录下符合指定模式的所有文件,以列表形式返回
            @param search_path  查询目录列表
            @param pattern      文件名模式
            @param pathsep      目录分隔符
        """
        for path in search_path.split( pathsep ):
            for match in glob.glob( os.path.join(path, pattern) ):
                yield match
    
    def searchFileFromFTP( self, pattern ):
        """ 在FTP的指定目录下查找文件
            @param pattern  文件名模式
        """
        flist = []
        try:
            self.ftp.dir( pattern, flist.append )
        except:
            flist = []
        # 提取文件名，格式如：-rw-r--r--    1 500      502           881 Aug 29 09:16 AllTest.py
        namelist = []
        for l in flist:
            name = l.split( ' ' )[-1]
            namelist.append( name )
        return namelist
    
    def upload( self, fromdir, pattern ):
        """ 上传文件
            @param fromdir  本地文件目录
            @param pattern  本地文件目录中的，文件名模式
        """
        if fromdir[-1] != os.sep:
            fromdir += os.sep
        flist = self._allFiles( fromdir, pattern )
        for f in flist:
            try:
                name = f.split( os.sep )[-1]
                #self.ftp.storlines( 'stor ' + name, open( fromdir + name ) )
                self.ftp.storbinary( 'stor ' + name, open( fromdir + name, 'rb' ) )
            except:
                print( '上传文件[%s]错误!' % name )
                return False
        return True
        
    def download( self, todir, pattern, isBin=False ):
        """ 下载文件.注意:文件名中带中文的下载不下来
            @param todir        下载到本地的目录
            @param pattern      文件名,可以使用通配符批量下载文件
            @param isBin        是否是二进制文件.是=True;否=False
        """
        # 若目录最后不是'\',则补充之
        if todir[-1] != os.sep:
            todir += os.sep
            
        flist = self.searchFileFromFTP( pattern )
        if len( flist ) == 0:
            print( '未找到文件[%s]!' % pattern )
            return False
        fn = [] # 将下载到本地的文件列表(带目录)
        for f in flist:
            fn.append( todir + f )
        
        # 循环下载每一个文件
        flag = False
        for i in range( len(fn) ):
            # 2010-11-24 12:13 add by 刘洪钢:Windows下，FTP查询会多出'.'、'..'两项，故需要跳过
            if flist[i] in ( '.', '..' ):
                continue
            try:
                fp = None
                try:
                    print( '正在下载文件:', flist[i] )
                    if isBin:   # 二进制文件
                        fp = open( fn[i] , 'wb' )
                        self.ftp.retrbinary( 'retr ' + flist[i], fp.write )
                    else:       # 非二进制文件
                        fp = open( fn[i] , 'w' )
                        l = []
                        self.ftp.retrlines( 'retr ' + flist[i], l.append )
                        for k in l:
                            fp.write( k + '\n' )
                        del l
                    flag = True
                finally:
                    if fp:  
                        fp.close()
            except:
                print( '下载文件[%s]时出错!' % flist[i] )
                return False
        if flag:
            return True
        else:
            return False
    
    def deleteFileFromFTP( self, pattern ):
        """ 删除文件,注意:文件名不能为中文
            @param pattern  要删除的文件名,可以使用通配符批量删除文件
        """
        flist = self.searchFileFromFTP( pattern )
        if len( flist ) == 0:
            print( '未找到文件[%s]!' % pattern )
            return False
        for f in flist:
            try:
                self.ftp.delete( f )
            except:
                print( '删除文件[%s]时出错!' % f )
                return False
        return True
    
    def renameFileFromFTP( self, oldname, newname ):
        """ 重命名FTP上的某个文件名
            @param oldname  原文件名
            @param newname  欲改成的文件名
        """
        try:
            self.ftp.sendcmd( 'dele %s' % newname )
        except:
            pass
        
        try:
            print( '正在将文件[%s]改名为[%s]' % ( oldname, newname ) )
            self.ftp.sendcmd( 'RNFR ' + oldname )
            self.ftp.sendcmd( 'RNTO %s' % newname )
            return True
        except:
            print( '将文件[%s]改名为[%s]时出错!' % ( oldname, newname ) )
            return False



    
    